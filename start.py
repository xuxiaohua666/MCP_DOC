#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP文档服务器启动器
提供自动环境检测与标准 MCP 协议服务器启动
"""

import argparse
import sys
import subprocess
from pathlib import Path

def check_python_environment():
    """检查Python环境"""
    print("🔍 检查Python环境...")
    try:
        result = subprocess.run([sys.executable, "--version"], 
                              capture_output=True, text=True, check=True)
        print(f"✅ Python版本: {result.stdout.strip()}")
        return True
    except Exception as e:
        print(f"❌ Python环境检查失败: {e}")
        return False

def check_dependencies():
    """检查并安装依赖包"""
    print("🔍 检查依赖包...")
    required_packages = ["mcp"]
    
    try:
        # 尝试导入所有必需的包
        for package in required_packages:
            __import__(package)
        print("✅ 所有依赖包已安装")
        return True
    except ImportError:
        print("⚠️  正在安装依赖包...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install"] + required_packages,
                          check=True)
            print("✅ 依赖包安装完成")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ 依赖包安装失败: {e}")
            return False

def check_config():
    """检查配置文件"""
    print("🔍 检查配置文件...")
    mcp_docs_config = Path("mcp-docs/mcp-config.json")
    mcp_server_config = Path("mcp-server/mcp-config.json")
    
    if not mcp_docs_config.exists():
        if mcp_server_config.exists():
            print("⚠️  正在复制配置文件...")
            import shutil
            shutil.copy2(mcp_server_config, mcp_docs_config)
            print("✅ 配置文件已复制")
        else:
            print("❌ 未找到配置文件")
            return False
    else:
        print("✅ 配置文件检查通过")
    
    return True

def start_server(verbose: bool = False) -> bool:
    """启动MCP协议服务器"""
    print("🚀 启动MCP协议服务器...")
    print("🤖 请在支持MCP的工具中使用相同的命令连接")
    print("")
    
    cmd = [sys.executable, "mcp-server/mcp_protocol_server.py", "--mcp-root", "mcp-docs"]
    if verbose:
        cmd.append("--verbose")
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
    except subprocess.CalledProcessError as e:
        print(f"❌ 服务器启动失败: {e}")
        return False
    
    return True

def main():
    parser = argparse.ArgumentParser(description="MCP文档服务器启动器")
    parser.add_argument("--verbose", "-v", 
                       action="store_true",
                       help="详细输出")
    parser.add_argument("--skip-checks", 
                       action="store_true",
                       help="跳过环境检查")
    
    args = parser.parse_args()
    
    print("")
    print("=" * 40)
    print("    MCP文档服务器启动器")
    print("=" * 40)
    print("")
    
    # 环境检查
    if not args.skip_checks:
        if not check_python_environment():
            sys.exit(1)
        
        if not check_dependencies():
            sys.exit(1)
        
        if not check_config():
            sys.exit(1)
        
        print("")
    
    # 启动服务器
    success = start_server(args.verbose)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
