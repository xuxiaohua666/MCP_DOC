@echo off
chcp 65001 >nul
echo.
echo ========================================
echo    MCP文档服务器启动脚本
echo ========================================
echo.

echo 正在检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误：未找到Python环境，请先安装Python
    pause
    exit /b 1
)

echo ✅ Python环境检查通过
echo.

echo 正在检查依赖包...
python -c "import fastapi, uvicorn, pydantic, requests" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  正在安装依赖包...
    python -m pip install fastapi uvicorn pydantic requests
    if %errorlevel% neq 0 (
        echo ❌ 依赖包安装失败
        pause
        exit /b 1
    )
    echo ✅ 依赖包安装完成
) else (
    echo ✅ 依赖包检查通过
)
echo.

echo 正在启动MCP文档服务器...
echo 📍 服务器地址: http://127.0.0.1:7778
echo 📖 API文档: http://127.0.0.1:7778/docs
echo 🏥 健康检查: http://127.0.0.1:7778/health
echo.
echo 💡 提示：按 Ctrl+C 停止服务器
echo.

python mcp-server/documentation_server.py --mcp-root mcp-docs

echo.
echo 服务器已停止
pause
