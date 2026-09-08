param(
    [string]$AttemptId = "canonical-01"
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$WorkDir = (Resolve-Path -LiteralPath $PSScriptRoot).Path
$InputFreezePath = Join-Path $WorkDir "input-freeze.json"
if (-not (Test-Path -LiteralPath $InputFreezePath)) {
    throw "Missing input-freeze.json"
}
$InputFreeze = Get-Content -Raw -LiteralPath $InputFreezePath | ConvertFrom-Json -Depth 50
if ($InputFreeze.status -ne "frozen_before_study_computation") {
    throw "Input freeze is not in the required state"
}
foreach ($File in $InputFreeze.frozen_files) {
    $Path = $File.path.Replace("/", "\")
    $Item = Get-Item -LiteralPath $Path
    $Hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToLowerInvariant()
    if ($Item.Length -ne $File.bytes -or $Hash -ne $File.sha256) {
        throw "Frozen file mismatch: $($File.path)"
    }
}

$LogDir = Join-Path $WorkDir "logs/$AttemptId"
if (Test-Path -LiteralPath $LogDir) {
    throw "Canonical log directory already exists: $LogDir"
}
New-Item -ItemType Directory -Path $LogDir | Out-Null
$OutputDir = "D:/CodexWorkspaces/mathematics-atlas/kemeny-author-work/run-01"
if (Test-Path -LiteralPath $OutputDir) {
    throw "Canonical output directory already exists: $OutputDir"
}

$env:UV_CACHE_DIR = "D:/CodexWorkspaces/mathematics-atlas/uv-cache"
$Executable = "uv"
$Arguments = @(
    "run", "--project", ".", "--frozen", "python", "census.py",
    "--input-dir", "D:/CodexWorkspaces/mathematics-atlas/kemeny-input-work",
    "--output-dir", $OutputDir
)
$TimeoutMilliseconds = 1800 * 1000
$Utf8 = [System.Text.UTF8Encoding]::new($false)
$StdoutPath = Join-Path $LogDir "stdout.txt"
$StderrPath = Join-Path $LogDir "stderr.txt"
$CommandPath = Join-Path $LogDir "command.json"
$AttemptLog = Join-Path $WorkDir "logs/attempts.jsonl"

$Start = [DateTimeOffset]::UtcNow
$Psi = [System.Diagnostics.ProcessStartInfo]::new()
$Psi.FileName = $Executable
$Psi.WorkingDirectory = $WorkDir
$Psi.UseShellExecute = $false
$Psi.RedirectStandardOutput = $true
$Psi.RedirectStandardError = $true
$Psi.CreateNoWindow = $true
foreach ($Argument in $Arguments) {
    $Psi.ArgumentList.Add($Argument)
}
$Psi.Environment["UV_CACHE_DIR"] = $env:UV_CACHE_DIR
$Process = [System.Diagnostics.Process]::new()
$Process.StartInfo = $Psi
if (-not $Process.Start()) {
    throw "Failed to start canonical evaluator"
}
$StdoutTask = $Process.StandardOutput.ReadToEndAsync()
$StderrTask = $Process.StandardError.ReadToEndAsync()
$Exited = $Process.WaitForExit($TimeoutMilliseconds)
$TimedOut = -not $Exited
if ($TimedOut) {
    $Process.Kill($true)
    $Process.WaitForExit()
}
$Stdout = $StdoutTask.GetAwaiter().GetResult()
$Stderr = $StderrTask.GetAwaiter().GetResult()
$End = [DateTimeOffset]::UtcNow
[IO.File]::WriteAllText($StdoutPath, $Stdout, $Utf8)
[IO.File]::WriteAllText($StderrPath, $Stderr, $Utf8)
$ReturnCode = if ($TimedOut) { $null } else { $Process.ExitCode }
$CommandRecord = [ordered]@{
    schema_version = "kemeny-command-attempt-v1"
    attempt_id = $AttemptId
    phase = "canonical_author_evaluation"
    executable = $Executable
    argv = @($Executable) + $Arguments
    working_directory = $WorkDir.Replace("\", "/")
    uv_cache_dir = $env:UV_CACHE_DIR
    input_freeze_path = "input-freeze.json"
    input_freeze_sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $InputFreezePath).Hash.ToLowerInvariant()
    timeout_seconds = 1800
    started_at_utc = $Start.ToString("o")
    ended_at_utc = $End.ToString("o")
    elapsed_milliseconds = [long]($End - $Start).TotalMilliseconds
    return_code = $ReturnCode
    timeout = $TimedOut
    stdout_path = "logs/$AttemptId/stdout.txt"
    stderr_path = "logs/$AttemptId/stderr.txt"
}
[IO.File]::WriteAllText(
    $CommandPath,
    ($CommandRecord | ConvertTo-Json -Depth 20) + "`n",
    $Utf8
)
[IO.File]::AppendAllText(
    $AttemptLog,
    ($CommandRecord | ConvertTo-Json -Compress -Depth 20) + "`n",
    $Utf8
)
$CommandRecord | ConvertTo-Json -Depth 20
if ($TimedOut) {
    exit 124
}
exit $Process.ExitCode
