@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul
set "PYTHON_CMD="
set "PYTHONIOENCODING=utf-8"
set "PYTHONUTF8=1"
for %%P in (python python3 py -3) do (
    where %%P >nul 2>&1
    if not errorlevel 1 (
        set "PYTHON_CMD=%%P"
        goto :found_python
    )
)
:found_python
if not defined PYTHON_CMD (
    echo ❌ 错误：未找到Python环境，请先安装Python
    pause
    exit /b 1
)
echo.
echo ========================================
echo    MCP文档服务器启动脚本
echo ========================================
echo.

echo 正在检查Python环境...
%PYTHON_CMD% --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误：未找到Python环境，请先安装Python
    pause
    exit /b 1
)

for /f "usebackq tokens=*" %%V in (`%PYTHON_CMD% --version 2^>^&1`) do (
    set "PYTHON_VERSION=%%V"
    goto :version_done
)
:version_done
echo ✅ Python环境检查通过: %PYTHON_VERSION%
echo.

echo 正在检查依赖包...
%PYTHON_CMD% -c "import mcp" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  正在安装依赖包...
    %PYTHON_CMD% -m pip install mcp
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

echo 正在启动MCP协议服务器...
echo 🤖 在支持MCP的工具中配置以下命令即可连接：
echo     Command : %PYTHON_CMD%
echo     Args    : start.py --skip-checks
echo 📂 工作目录: %CD%
echo.
echo 💡 提示：服务将在当前窗口运行，按 Ctrl+C 可停止。
echo.

%PYTHON_CMD% start.py --skip-checks

echo.
echo 服务器已停止
pause
endlocal
