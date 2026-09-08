$ErrorActionPreference = "Stop"
$env:UV_CACHE_DIR = "D:\CodexWorkspaces\mathematics-atlas\uv-cache"
uv run --frozen python -m atlas_engine evaluate --output-dir logs/canonical
exit $LASTEXITCODE

