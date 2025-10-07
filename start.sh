#!/bin/bash

echo ""
echo "========================================"
echo "    MCP文档服务器启动脚本"
echo "========================================"
echo ""

# 检查Python环境
echo "正在检查Python环境..."
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "❌ 错误：未找到Python环境，请先安装Python"
        read -p "按回车键退出..."
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

echo "✅ Python环境检查通过: $($PYTHON_CMD --version)"
echo ""

# 检查依赖包
echo "正在检查依赖包..."
if ! $PYTHON_CMD -c "import fastapi, uvicorn, pydantic, requests" 2>/dev/null; then
    echo "⚠️  正在安装依赖包..."
    $PYTHON_CMD -m pip install fastapi uvicorn pydantic requests
    if [ $? -ne 0 ]; then
        echo "❌ 依赖包安装失败"
        read -p "按回车键退出..."
        exit 1
    fi
    echo "✅ 依赖包安装完成"
else
    echo "✅ 依赖包检查通过"
fi

echo ""

# 启动服务器
echo "正在启动MCP文档服务器..."
echo "📍 服务器地址: http://127.0.0.1:7778"
echo "📖 API文档: http://127.0.0.1:7778/docs"
echo "🏥 健康检查: http://127.0.0.1:7778/health"
echo ""
echo "💡 提示：按 Ctrl+C 停止服务器"
echo ""

trap 'echo ""; echo "服务器已停止"; read -p "按回车键退出..."' INT

$PYTHON_CMD mcp-server/documentation_server.py --mcp-root mcp-docs
