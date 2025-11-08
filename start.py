#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP文档服务器启动器
提供自动环境检测与标准 MCP 协议服务器启动
"""

import argparse
import socket
import sys
import subprocess
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


LOG_STREAM = sys.stdout


def log(message: str = "") -> None:
    print(message, file=LOG_STREAM)


def check_python_environment() -> bool:
    """检查Python环境"""
    log("检查Python环境...")
    try:
        result = subprocess.run([sys.executable, "--version"], capture_output=True, text=True, check=True)
        log(f"Python版本: {result.stdout.strip()}")
        return True
    except Exception as exc:  # pylint: disable=broad-except
        log(f"Python环境检查失败: {exc}")
        return False


def check_dependencies(packages: list[str]) -> bool:
    """检查并安装依赖包"""
    if not packages:
        return True

    log("检查依赖包...")
    try:
        for package in packages:
            __import__(package)
        log("所有依赖包已安装")
        return True
    except ImportError:
        log("正在安装依赖包...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", *packages], check=True)
            log("依赖包安装完成")
            return True
        except subprocess.CalledProcessError as exc:
            log(f"依赖包安装失败: {exc}")
            return False


def check_config() -> bool:
    """检查配置文件"""
    log("检查配置文件...")
    mcp_docs_config = BASE_DIR / "mcp-docs/mcp-config.json"
    mcp_server_config = BASE_DIR / "mcp-server/mcp-config.json"

    if not mcp_docs_config.exists():
        if mcp_server_config.exists():
            log("正在复制配置文件...")
            import shutil

            shutil.copy2(mcp_server_config, mcp_docs_config)
            log("配置文件已复制")
        else:
            log("未找到配置文件")
            return False
    else:
        log("配置文件检查通过")

    return True


def start_server(mode: str, host: str, port: int, verbose: bool) -> bool:
    """启动服务器"""
    if mode == "http":
        display_host = host
        if host in {"0.0.0.0", "::", ""}:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                    s.connect(("8.8.8.8", 80))
                    display_host = s.getsockname()[0]
            except OSError:
                display_host = "localhost"

        log("启动HTTP MCP网关服务器...")
        log(f"访问地址: http://{display_host}:{port} （监听 {host}）")
        log("请将此URL配置到远程客户端 (例如 Cursor 的 mcp.json)")
        log("如需认证，可在反向代理或自定义中间层实现")
        log("配置示例：")
        log(f"    {{\"mcpServers\": {{\"mcp-docs-http\": {{\"url\": \"http://{display_host}:{port}\"}}}}}}")
        cmd = [
            sys.executable,
            str(BASE_DIR / "mcp-server/http_server.py"),
            "--mcp-root",
            str(BASE_DIR / "mcp-docs"),
            "--host",
            host,
            "--port",
            str(port),
        ]
    else:
        log("启动MCP协议服务器 (STDIO 模式)...")
        log("在支持MCP的工具中配置相同命令即可连接")
        log("配置完成后，可关闭此窗口；客户端会自动按需启动进程")
        log("若要共享给其他设备，请改用 http 模式：python start.py --mode http")
        cmd = [
            sys.executable,
            str(BASE_DIR / "mcp-server/mcp_protocol_server.py"),
            "--mcp-root",
            str(BASE_DIR / "mcp-docs"),
        ]

    if verbose:
        cmd.append("--verbose")

    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        log("服务器已停止")
    except subprocess.CalledProcessError as exc:
        log(f"服务器启动失败: {exc}")
        return False

    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="MCP文档服务器启动器")
    parser.add_argument(
        "--mode",
        choices=["mcp", "http"],
        default="http",
        help="服务器模式: mcp (STDIO) 或 http (HTTP网关)",
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="HTTP模式下绑定的主机地址 (默认: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=7778,
        help="HTTP模式下的端口 (默认: 7778)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="详细输出",
    )
    parser.add_argument(
        "--skip-checks",
        action="store_true",
        help="跳过环境检查",
    )

    args = parser.parse_args()

    global LOG_STREAM
    if args.mode == "mcp":
        LOG_STREAM = sys.stderr
    else:
        LOG_STREAM = sys.stdout

    log()
    log("=" * 40)
    log("    MCP文档服务器启动器")
    log("=" * 40)
    log()

    if not args.skip_checks:
        if not check_python_environment():
            sys.exit(1)

        required_packages = ["mcp"]
        if args.mode == "http":
            required_packages.extend(["fastapi", "uvicorn"])

        if not check_dependencies(required_packages):
            sys.exit(1)

        if not check_config():
            sys.exit(1)

        log()

    success = start_server(args.mode, args.host, args.port, args.verbose)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
