$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$WorkDir = (Resolve-Path -LiteralPath $PSScriptRoot).Path
$Utf8 = [System.Text.UTF8Encoding]::new($false)
$env:UV_CACHE_DIR = "D:/CodexWorkspaces/mathematics-atlas/uv-cache"

function Get-FileRecord {
    param([string]$Path, [string]$Role)
    $Item = Get-Item -LiteralPath $Path
    $Hash = Get-FileHash -Algorithm SHA256 -LiteralPath $Item.FullName
    return [ordered]@{
        path = $Item.FullName.Replace("\", "/")
        role = $Role
        bytes = $Item.Length
        sha256 = $Hash.Hash.ToLowerInvariant()
    }
}

$CodePaths = @(
    ".python-version",
    "pyproject.toml",
    "uv.lock",
    "census.py",
    "prepare.ps1",
    "freeze_inputs.ps1",
    "run_logged.ps1"
)
$CodeFiles = foreach ($RelativePath in $CodePaths) {
    Get-FileRecord -Path (Join-Path $WorkDir $RelativePath) -Role "author_code_or_environment"
}
$CodeManifest = [ordered]@{
    schema_version = "kemeny-author-code-freeze-v1"
    status = "frozen_before_study_computation"
    frozen_at_utc = [DateTimeOffset]::UtcNow.ToString("o")
    files = @($CodeFiles)
}
$CodeManifestPath = Join-Path $WorkDir "code-freeze-manifest.json"
[IO.File]::WriteAllText(
    $CodeManifestPath,
    ($CodeManifest | ConvertTo-Json -Depth 20) + "`n",
    $Utf8
)
$CodeManifestRecord = Get-FileRecord -Path $CodeManifestPath -Role "code_freeze_manifest"

$ExternalPaths = @(
    @("D:/CodexWorkspaces/mathematics-atlas/kemeny-spec-work/contract-v1.md", "frozen_contract"),
    @("D:/CodexWorkspaces/mathematics-atlas/kemeny-spec-work/contract-freeze.json", "contract_freeze"),
    @("D:/CodexWorkspaces/mathematics-atlas/discovery-next-audit-work/source-method-assessment.json", "source_method_review"),
    @("D:/CodexWorkspaces/mathematics-atlas/kemeny-input-work/source-manifest.json", "source_manifest"),
    @("D:/CodexWorkspaces/mathematics-atlas/kemeny-input-work/graph2c.g6", "graph6_input"),
    @("D:/CodexWorkspaces/mathematics-atlas/kemeny-input-work/graph3c.g6", "graph6_input"),
    @("D:/CodexWorkspaces/mathematics-atlas/kemeny-input-work/graph4c.g6", "graph6_input"),
    @("D:/CodexWorkspaces/mathematics-atlas/kemeny-input-work/graph5c.g6", "graph6_input"),
    @("D:/CodexWorkspaces/mathematics-atlas/kemeny-input-work/graph6c.g6", "graph6_input")
)
$ExternalFiles = foreach ($Entry in $ExternalPaths) {
    Get-FileRecord -Path $Entry[0] -Role $Entry[1]
}

$UvVersion = (& uv --version).Trim()
$RuntimeJson = & uv run --project $WorkDir --frozen python -c "import json,sys,sympy; print(json.dumps({'python':'.'.join(map(str,sys.version_info[:3])),'python_executable':sys.executable.replace(chr(92),'/'),'sympy':sympy.__version__},sort_keys=True))"
if ($LASTEXITCODE -ne 0) {
    throw "Runtime version query failed"
}
$Runtime = $RuntimeJson | ConvertFrom-Json
if (-not $UvVersion.StartsWith("uv 0.8.19") -or $Runtime.python -ne "3.12.11" -or $Runtime.sympy -ne "1.14.0") {
    throw "Frozen runtime version mismatch"
}

$Freeze = [ordered]@{
    schema_version = "kemeny-author-input-freeze-v1"
    status = "frozen_before_study_computation"
    frozen_at_utc = [DateTimeOffset]::UtcNow.ToString("o")
    author = "/root/sol_symmetry_worker"
    working_directory = $WorkDir.Replace("\", "/")
    uv_cache_dir = $env:UV_CACHE_DIR
    canonical_argv = @(
        "uv", "run", "--project", ".", "--frozen", "python", "census.py",
        "--input-dir", "D:/CodexWorkspaces/mathematics-atlas/kemeny-input-work",
        "--output-dir", "D:/CodexWorkspaces/mathematics-atlas/kemeny-author-work/run-01"
    )
    timeout_seconds = 1800
    environment = [ordered]@{
        uv = $UvVersion
        python = $Runtime.python
        python_executable = $Runtime.python_executable
        sympy = $Runtime.sympy
    }
    code_manifest = $CodeManifestRecord
    frozen_files = @($CodeFiles) + @($ExternalFiles) + @($CodeManifestRecord)
}
$FreezePath = Join-Path $WorkDir "input-freeze.json"
[IO.File]::WriteAllText(
    $FreezePath,
    ($Freeze | ConvertTo-Json -Depth 30) + "`n",
    $Utf8
)
$FreezeRecord = Get-FileRecord -Path $FreezePath -Role "input_freeze_manifest"
$Result = [ordered]@{
    status = "frozen_before_study_computation"
    code_manifest = $CodeManifestRecord
    input_freeze = $FreezeRecord
}
$Result | ConvertTo-Json -Depth 10
