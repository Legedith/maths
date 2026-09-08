param(
    [string]$AttemptId = "preparation-01"
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$WorkDir = (Resolve-Path -LiteralPath $PSScriptRoot).Path
$LogDir = Join-Path $WorkDir "logs/$AttemptId"
if (Test-Path -LiteralPath $LogDir) {
    throw "Preparation log directory already exists: $LogDir"
}
New-Item -ItemType Directory -Path $LogDir | Out-Null
$env:UV_CACHE_DIR = "D:/CodexWorkspaces/mathematics-atlas/uv-cache"
$Utf8 = [System.Text.UTF8Encoding]::new($false)
$AttemptLog = Join-Path $WorkDir "logs/attempts.jsonl"

function Invoke-RecordedCommand {
    param(
        [string]$Step,
        [string]$Executable,
        [string[]]$Arguments
    )
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
        throw "Could not start preparation step $Step"
    }
    $StdoutTask = $Process.StandardOutput.ReadToEndAsync()
    $StderrTask = $Process.StandardError.ReadToEndAsync()
    $Process.WaitForExit()
    $Stdout = $StdoutTask.GetAwaiter().GetResult()
    $Stderr = $StderrTask.GetAwaiter().GetResult()
    $End = [DateTimeOffset]::UtcNow
    [IO.File]::WriteAllText((Join-Path $LogDir "$Step.stdout.txt"), $Stdout, $Utf8)
    [IO.File]::WriteAllText((Join-Path $LogDir "$Step.stderr.txt"), $Stderr, $Utf8)
    $Record = [ordered]@{
        schema_version = "kemeny-command-attempt-v1"
        attempt_id = $AttemptId
        phase = "preparation"
        step = $Step
        executable = $Executable
        argv = @($Executable) + $Arguments
        working_directory = $WorkDir
        uv_cache_dir = $env:UV_CACHE_DIR
        started_at_utc = $Start.ToString("o")
        ended_at_utc = $End.ToString("o")
        return_code = $Process.ExitCode
        timeout = $false
        stdout_path = "logs/$AttemptId/$Step.stdout.txt"
        stderr_path = "logs/$AttemptId/$Step.stderr.txt"
    }
    $Line = $Record | ConvertTo-Json -Compress -Depth 10
    [IO.File]::AppendAllText($AttemptLog, $Line + "`n", $Utf8)
    if ($Process.ExitCode -ne 0) {
        throw "Preparation step $Step failed with exit code $($Process.ExitCode)"
    }
    return $Stdout.Trim()
}

$UvVersion = Invoke-RecordedCommand -Step "01-uv-version" -Executable "uv" -Arguments @("--version")
if (-not $UvVersion.StartsWith("uv 0.8.19")) {
    throw "Pinned uv version mismatch: $UvVersion"
}
Invoke-RecordedCommand -Step "02-uv-lock" -Executable "uv" -Arguments @("lock", "--python", "3.12.11") | Out-Null
Invoke-RecordedCommand -Step "03-uv-sync" -Executable "uv" -Arguments @("sync", "--frozen") | Out-Null
$PythonVersion = Invoke-RecordedCommand -Step "04-python-version" -Executable "uv" -Arguments @("run", "--project", ".", "--frozen", "python", "--version")
if ($PythonVersion -ne "Python 3.12.11") {
    throw "Pinned Python version mismatch: $PythonVersion"
}
$SympyVersion = Invoke-RecordedCommand -Step "05-sympy-version" -Executable "uv" -Arguments @("run", "--project", ".", "--frozen", "python", "-c", "import sympy; print(sympy.__version__)")
if ($SympyVersion -ne "1.14.0") {
    throw "Pinned SymPy version mismatch: $SympyVersion"
}
Invoke-RecordedCommand -Step "06-syntax-check" -Executable "uv" -Arguments @("run", "--project", ".", "--frozen", "python", "-m", "py_compile", "census.py") | Out-Null

$Result = [ordered]@{
    status = "preparation_complete_no_study_evaluation"
    uv = $UvVersion
    python = $PythonVersion
    sympy = $SympyVersion
    syntax_check = "passed"
}
$Result | ConvertTo-Json -Depth 5
