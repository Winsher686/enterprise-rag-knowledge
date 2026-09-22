# ============================================================
# 运行所有后端测试
# ============================================================

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$BackendDir = Join-Path $ProjectRoot "backend"

Push-Location $BackendDir
try {
    if (Test-Path ".venv\Scripts\Activate.ps1") {
        . .\.venv\Scripts\Activate.ps1
    }

    Write-Host "运行测试..." -ForegroundColor Green
    pytest -v
} finally {
    Pop-Location
}