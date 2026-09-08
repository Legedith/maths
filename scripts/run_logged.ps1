param(
    [Parameter(Mandatory = $true)]
    [string]$Name,
    [Parameter(Mandatory = $true, ValueFromRemainingArguments = $true)]
    [string[]]$Command
)

$ErrorActionPreference = "Stop"
$workspace = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$logs = [System.IO.Path]::GetFullPath((Join-Path $workspace "logs"))
if (-not $logs.StartsWith($workspace + [System.IO.Path]::DirectorySeparatorChar)) {
    throw "Refusing to write a log outside the staging workspace"
}
New-Item -ItemType Directory -Force -Path $logs | Out-Null
$stdoutPath = Join-Path $logs ($Name + ".console.log")
$metadataPath = Join-Path $logs ($Name + ".command.json")
$started = Get-Date
$timer = [System.Diagnostics.Stopwatch]::StartNew()
# Windows PowerShell wraps native stderr as ErrorRecord, even for warnings.
# Preserve that output and decide success from the native process exit status.
$ErrorActionPreference = "Continue"
$output = & $Command[0] $Command[1..($Command.Count - 1)] 2>&1 | Out-String
$exitCode = $LASTEXITCODE
$ErrorActionPreference = "Stop"
$timer.Stop()
$ended = Get-Date
$output | Set-Content -LiteralPath $stdoutPath -Encoding utf8
[ordered]@{
    name = $Name
    command_argv = $Command
    command_display = ($Command -join " ")
    working_directory = (Get-Location).Path
    started_at = $started.ToString("o")
    ended_at = $ended.ToString("o")
    runtime_seconds = $timer.Elapsed.TotalSeconds
    exit_code = $exitCode
    console_log = "logs/" + $Name + ".console.log"
} | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $metadataPath -Encoding utf8
Write-Output $output
exit $exitCode
