$ErrorActionPreference = 'Continue'

$auditRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$reproductionRoot = Join-Path $auditRoot 'reproduction'
$runDirectory = Join-Path $reproductionRoot 'run-reproduction'
$env:UV_CACHE_DIR = 'D:\CodexWorkspaces\mathematics-atlas\uv-cache'
$records = @()

if (Test-Path -LiteralPath $runDirectory) {
    throw "Refusing to overwrite existing reproduction output: $runDirectory"
}

function Invoke-Recorded {
    param(
        [string]$Id,
        [string]$Executable,
        [string[]]$Arguments,
        [string]$DisplayCommand
    )
    $started = (Get-Date).ToUniversalTime().ToString('o')
    $timer = [System.Diagnostics.Stopwatch]::StartNew()
    Push-Location $reproductionRoot
    try {
        $output = & $Executable @Arguments 2>&1 | Out-String
        $exitCode = $LASTEXITCODE
    } finally {
        Pop-Location
    }
    $timer.Stop()
    $script:records += [pscustomobject]@{
        id = $Id
        command = $DisplayCommand
        cwd = $reproductionRoot
        started_at_utc = $started
        ended_at_utc = (Get-Date).ToUniversalTime().ToString('o')
        duration_seconds = [Math]::Round($timer.Elapsed.TotalSeconds, 6)
        exit_code = $exitCode
        output = $output.TrimEnd()
    }
    return $exitCode
}

$uv = (Get-Command uv -ErrorAction Stop | Select-Object -First 1).Path
$startedAt = (Get-Date).ToUniversalTime().ToString('o')
$uvCode = Invoke-Recorded -Id 'uv_version' -Executable $uv -Arguments @('--version') -DisplayCommand 'uv --version'
$syncCode = Invoke-Recorded -Id 'uv_sync' -Executable $uv -Arguments @('sync', '--frozen') -DisplayCommand 'UV_CACHE_DIR=D:/CodexWorkspaces/mathematics-atlas/uv-cache uv sync --frozen'
$runCode = $null
if ($syncCode -eq 0) {
    $runCode = Invoke-Recorded -Id 'canonical_replay' -Executable $uv -Arguments @('run', '--frozen', 'python', 'replay.py', '--output-dir', 'run-reproduction') -DisplayCommand 'UV_CACHE_DIR=D:/CodexWorkspaces/mathematics-atlas/uv-cache uv run --frozen python replay.py --output-dir run-reproduction'
}
$passed = ($uvCode -eq 0 -and $syncCode -eq 0 -and $runCode -eq 0)
$result = [ordered]@{
    schema_version = 'independent-copied-reproduction-command-v1'
    started_at_utc = $startedAt
    ended_at_utc = (Get-Date).ToUniversalTime().ToString('o')
    uv_executable = $uv
    uv_cache_dir = $env:UV_CACHE_DIR
    copied_preexecution_freeze_sha256 = '11359bdd37807ae1cf5b42697007503d56ae54d77a6452c4fa2ff83f9f5a6cfc'
    records = $records
    all_pass = $passed
}
$json = ($result | ConvertTo-Json -Depth 8) + "`n"
[System.IO.File]::WriteAllText((Join-Path $auditRoot 'copied-reproduction-command.json'), $json, [System.Text.UTF8Encoding]::new($false))
$result | ConvertTo-Json -Depth 8
if (-not $passed) { exit 1 }
