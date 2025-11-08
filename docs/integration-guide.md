# MCP 文档服务器集成指南

本文档介绍如何将本仓库提供的 MCP 文档服务器接入常用的支持 Model Context Protocol 的工具：Cursor 与 Trae。默认推荐通过 **HTTP 网关** 共享服务，亦可使用 **STDIO 模式** 由客户端本地启动。

---

## 通用准备工作

1. **安装依赖**
   ```bash
   pip install -r mcp-server/requirements.txt   # 包含 mcp / fastapi / uvicorn
   ```
2. **启动 HTTP 网关（默认）**
   ```bash
   python start.py --mode http --host 0.0.0.0 --port 7778 --skip-checks
   # 在其他客户端中使用 http://your-host:7778 连接
   ```
3. **可选：STDIO 启动命令（本地单机使用）**
   ```bash
   python start.py --mode mcp --skip-checks
   ```
   > 该命令会在 STDIO 模式下启动 MCP 协议服务器，适合由 Cursor / Trae 本地进程直接调用。

---

## 在 Cursor 中添加 MCP 服务

### HTTP 模式（共享服务）
1. **打开 Cursor 设置**
   - `Ctrl+,`（或 `Cmd+,`） → `Labs / Experimental` → 启用 *Model Context Protocol*。
2. **添加自定义 MCP Server**
   - 进入 `Settings -> Integrations -> Model Context`.
   - 点击 `Add MCP Server`，填写信息：
     - **Name:** `mcp-docs-http`
     - **URL:** `http://your-host:7778`（根据实际地址调整）
     - 可选：在 `Headers` 中添加 `Authorization` 等认证信息。
3. **保存并测试**
   - 保存配置后刷新服务器列表或重启 Cursor。
   - 在聊天面板输入 `list resources from mcp-docs-http` 验证连接。

### STDIO 模式（本地进程）
1. **打开 Cursor 设置** → 同上。
2. **添加自定义 MCP Server**
   - **Name:** `mcp-docs`
   - **Command:** `python`
   - **Arguments:** `start.py --mode mcp --skip-checks`
   - **Working Directory:** `D:\data\MCP`（按实际路径调整）
   - 可选：设置环境变量 `MCP_ROOT=mcp-docs`、`PYTHONUTF8=1`。
3. **保存并测试**
   - 在命令面板运行 `MCP: Refresh Servers` 或重启 Cursor。
   - 输入 `list resources from mcp-docs` 验证是否能列出文档。

> **JSON 配置方式（旧版本或手动管理）**  
> 在 `%APPDATA%\Cursor\cursor-settings.json`（Windows）或 `~/Library/Application Support/Cursor/cursor-settings.json`（macOS）中添加：
> ```json
> {
>   "mcpServers": [
>     {
>       "name": "mcp-docs",
>       "command": "python",
>       "args": ["start.py", "--mode", "mcp", "--skip-checks"],
>       "cwd": "D:/data/MCP",
>       "env": {
>         "MCP_ROOT": "mcp-docs",
>         "PYTHONUTF8": "1"
>       }
>     }
>   ]
> }
> ```

---

## 在 Trae 中添加 MCP 服务

### HTTP 模式
1. **准备 HTTP 服务地址**：确保 `python start.py --mode http ...` 已在服务器端启动。
2. **编辑 Trae 配置**
   - 打开 `Settings -> Model Context`。
   - 选择 `Add Server`，配置：
     - **Name:** `mcp-docs-http`
     - **URL:** `http://your-host:7778`
     - 按需配置认证头。
3. **验证连接**
   - 刷新服务器列表并调用 `listResources`、`search_documentation` 等工具确认结果。

### STDIO 模式
1. **准备启动脚本**（可选）
   ```cmd
   @echo off
   cd /d D:\data\MCP
   set PYTHONUTF8=1
   python start.py --mode mcp --skip-checks
   ```
2. **在 Trae 中添加进程模式**
   - **Name:** `mcp-docs`
   - **Command:** 指向 Python 或上述脚本
   - **Arguments:** `start.py --mode mcp --skip-checks`
   - **Working Directory:** `D:\data\MCP`
3. **验证连接** → 调用工具验证返回数据。

> 若 Trae 需要 JSON/YAML 配置，可参考：
> ```json
> {
>   "servers": {
>     "mcp-docs": {
>       "command": "python",
>       "args": ["start.py", "--mode", "mcp", "--skip-checks"],
>       "cwd": "D:/data/MCP"
>     }
>   }
> }
> ```

---

## 常见问题

| 问题 | 处理方案 |
| ---- | -------- |
| HTTP 模式客户端无法连接 | 检查 URL、端口、防火墙及认证配置 |
| STDIO 模式启动失败 | 确认命令、工作目录、`MCP_ROOT` 环境参数 |
| 终端输出乱码 | 设置 `PYTHONUTF8=1`（Windows）或 `export PYTHONUTF8=1`（Linux/macOS） |
| 工具列表为空 | 确认 `mcp-docs/mcp-config.json` 描述的语言、项目目录完整 |

---

完成以上配置后，可在 Cursor、Trae 等客户端中直接调用文档服务器提供的数据与工具，辅助开发与文档撰写。 

