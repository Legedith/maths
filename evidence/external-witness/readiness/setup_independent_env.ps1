$ErrorActionPreference = 'Continue'

$auditRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$venvPython = Join-Path $auditRoot '.venv\Scripts\python.exe'
$env:UV_CACHE_DIR = 'D:\CodexWorkspaces\mathematics-atlas\uv-cache'
$records = @()

function Invoke-Recorded {
    param(
        [string]$Id,
        [string]$Executable,
        [string[]]$Arguments,
        [string]$DisplayCommand
    )

    $started = (Get-Date).ToUniversalTime().ToString('o')
    $timer = [System.Diagnostics.Stopwatch]::StartNew()
    $output = & $Executable @Arguments 2>&1 | Out-String
    $exitCode = $LASTEXITCODE
    $timer.Stop()
    $script:records += [pscustomobject]@{
        id = $Id
        command = $DisplayCommand
        started_at_utc = $started
        duration_seconds = [Math]::Round($timer.Elapsed.TotalSeconds, 6)
        exit_code = $exitCode
        output = $output.TrimEnd()
    }
    return $exitCode
}

$uvCommand = Get-Command uv -ErrorAction Stop | Select-Object -First 1
$startedAt = (Get-Date).ToUniversalTime().ToString('o')
$uvVersionCode = Invoke-Recorded -Id 'uv_version' -Executable $uvCommand.Path -Arguments @('--version') -DisplayCommand 'uv --version'
$venvCode = Invoke-Recorded -Id 'create_venv' -Executable $uvCommand.Path -Arguments @('venv', '--python', '3.12', '.venv') -DisplayCommand 'UV_CACHE_DIR=D:/CodexWorkspaces/mathematics-atlas/uv-cache uv venv --python 3.12 .venv'
$installCode = $null
$freezeCode = $null
if ($venvCode -eq 0) {
    $installCode = Invoke-Recorded -Id 'install_pins' -Executable $uvCommand.Path -Arguments @('pip', 'install', '--python', $venvPython, 'z3-solver==5.1.0.0', 'sympy==1.14.0') -DisplayCommand 'UV_CACHE_DIR=D:/CodexWorkspaces/mathematics-atlas/uv-cache uv pip install --python .venv/Scripts/python.exe z3-solver==5.1.0.0 sympy==1.14.0'
}
if ($installCode -eq 0) {
    $freezeCode = Invoke-Recorded -Id 'freeze' -Executable $uvCommand.Path -Arguments @('pip', 'freeze', '--python', $venvPython) -DisplayCommand 'UV_CACHE_DIR=D:/CodexWorkspaces/mathematics-atlas/uv-cache uv pip freeze --python .venv/Scripts/python.exe'
}

$passed = ($uvVersionCode -eq 0 -and $venvCode -eq 0 -and $installCode -eq 0 -and $freezeCode -eq 0)
$result = [ordered]@{
    schema_version = 'independent-tool-setup-v1'
    started_at_utc = $startedAt
    ended_at_utc = (Get-Date).ToUniversalTime().ToString('o')
    audit_root = $auditRoot
    uv_executable = $uvCommand.Path
    uv_cache_dir = $env:UV_CACHE_DIR
    isolated_venv = '.venv'
    records = $records
    all_pass = $passed
}

$json = ($result | ConvertTo-Json -Depth 8) + "`n"
[System.IO.File]::WriteAllText((Join-Path $auditRoot 'independent-env-setup.json'), $json, [System.Text.UTF8Encoding]::new($false))
$result | ConvertTo-Json -Depth 8
if (-not $passed) { exit 1 }

