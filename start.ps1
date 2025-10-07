# MCP文档服务器启动脚本 (PowerShell版本)

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    MCP文档服务器启动脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查Python环境
Write-Host "正在检查Python环境..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Python not found"
    }
    Write-Host "✅ Python环境检查通过: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ 错误：未找到Python环境，请先安装Python" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
}

Write-Host ""

# 检查依赖包
Write-Host "正在检查依赖包..." -ForegroundColor Yellow
try {
    python -c "import fastapi, uvicorn, pydantic, requests" 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "Dependencies not found"
    }
    Write-Host "✅ 依赖包检查通过" -ForegroundColor Green
} catch {
    Write-Host "⚠️  正在安装依赖包..." -ForegroundColor Yellow
    python -m pip install fastapi uvicorn pydantic requests
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ 依赖包安装失败" -ForegroundColor Red
        Read-Host "按回车键退出"
        exit 1
    }
    Write-Host "✅ 依赖包安装完成" -ForegroundColor Green
}

Write-Host ""

# 启动服务器
Write-Host "正在启动MCP文档服务器..." -ForegroundColor Yellow
Write-Host "📍 服务器地址: http://127.0.0.1:7778" -ForegroundColor Cyan
Write-Host "📖 API文档: http://127.0.0.1:7778/docs" -ForegroundColor Cyan
Write-Host "🏥 健康检查: http://127.0.0.1:7778/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "💡 提示：按 Ctrl+C 停止服务器" -ForegroundColor Magenta
Write-Host ""

try {
    python mcp-server/documentation_server.py --mcp-root mcp-docs
} catch {
    Write-Host "❌ 服务器启动失败" -ForegroundColor Red
} finally {
    Write-Host ""
    Write-Host "服务器已停止" -ForegroundColor Yellow
    Read-Host "按回车键退出"
}
