# ============================================================
# 本地开发一键启动（Windows PowerShell）
# 后端 + 前端分别在新窗口中启动
# ============================================================

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$BackendDir = Join-Path $ProjectRoot "backend"
$FrontendDir = Join-Path $ProjectRoot "frontend"

Write-Host "项目根目录：$ProjectRoot"

# 后端
if (Test-Path (Join-Path $BackendDir ".venv\Scripts\Activate.ps1")) {
    Write-Host "启动后端（venv）..."
    Start-Process powershell -ArgumentList @(
        "-NoExit",
        "-Command",
        "cd '$BackendDir'; .\.venv\Scripts\Activate.ps1; uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
    )
} else {
    Write-Host "启动后端（系统 Python）..." -ForegroundColor Yellow
    Start-Process powershell -ArgumentList @(
        "-NoExit",
        "-Command",
        "cd '$BackendDir'; uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
    )
}

# 前端
if (Test-Path (Join-Path $FrontendDir "node_modules")) {
    Write-Host "启动前端..."
    Start-Process powershell -ArgumentList @(
        "-NoExit",
        "-Command",
        "cd '$FrontendDir'; npm run dev"
    )
} else {
    Write-Host "前端依赖未安装，请先执行：cd frontend; npm install" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "后端：http://127.0.0.1:8000/docs"
Write-Host "前端：http://127.0.0.1:5173"