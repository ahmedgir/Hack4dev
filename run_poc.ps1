$ErrorActionPreference = "Stop"
$python = Join-Path $env:USERPROFILE "miniconda3\envs\exoplanet-poc\python.exe"
if (-not (Test-Path -LiteralPath $python)) {
    throw "Python environment not found: $python"
}
& $python (Join-Path $PSScriptRoot "scripts\run_poc.py") @args
exit $LASTEXITCODE
