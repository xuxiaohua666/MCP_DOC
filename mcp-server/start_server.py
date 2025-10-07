#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP文档服务器启动器
根据可用库自动选择合适的服务器实现
"""

import argparse
import sys
from pathlib import Path

def check_mcp_library():
    """检查是否安装了官方MCP库"""
    try:
        import mcp
        return True
    except ImportError:
        return False

def main():
    parser = argparse.ArgumentParser(description="MCP Documentation Server Launcher")
    parser.add_argument("--server-type", choices=["mcp", "rest", "auto"], 
                       default="auto", help="服务器类型")
    parser.add_argument("--mcp-root", default=".", help="MCP root directory")
    parser.add_argument("--host", default="127.0.0.1", help="Host for REST server")
    parser.add_argument("--port", type=int, default=8000, help="Port for REST server")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # 自动检测
    if args.server_type == "auto":
        if check_mcp_library():
            print("✅ 检测到官方MCP库，启动MCP协议服务器...")
            args.server_type = "mcp"
        else:
            print("ℹ️ 未检测到官方MCP库，启动REST API服务器...")
            print("💡 如需MCP协议支持，请安装: pip install mcp")
            args.server_type = "rest"
    
    # 启动相应服务器
    if args.server_type == "mcp":
        if not check_mcp_library():
            print("❌ 错误: 需要安装官方MCP库")
            print("请运行: pip install mcp")
            return 1
        
        print("🚀 启动MCP协议服务器...")
        print("📖 用于Claude Desktop和其他MCP客户端")
        
        import asyncio
        import sys
        sys.path.append(str(Path(__file__).parent / "server"))
        
        from mcp_protocol_server import main as mcp_main
        try:
            # 传递参数给MCP服务器
            sys.argv = ["mcp_protocol_server.py", "--mcp-root", args.mcp_root]
            if args.verbose:
                sys.argv.append("--verbose")
            
            asyncio.run(mcp_main())
        except KeyboardInterrupt:
            print("\n👋 MCP服务器已停止")
            return 0
    
    elif args.server_type == "rest":
        try:
            import fastapi
            import uvicorn
        except ImportError:
            print("❌ 错误: 需要安装REST API依赖")
            print("请运行: pip install fastapi uvicorn")
            return 1
        
        print("🚀 启动REST API服务器...")
        print(f"🌐 Web界面: http://{args.host}:{args.port}/docs")
        
        import sys
        sys.path.append(str(Path(__file__).parent / "server"))
        
        from documentation_server import main as rest_main
        try:
            # 传递参数给REST服务器
            sys.argv = [
                "documentation_server.py", 
                "--mcp-root", args.mcp_root,
                "--host", args.host,
                "--port", str(args.port)
            ]
            if args.verbose:
                sys.argv.append("--verbose")
            
            rest_main()
        except KeyboardInterrupt:
            print(f"\n👋 REST服务器已停止")
            return 0
    
    return 0

if __name__ == "__main__":
    exit(main())
