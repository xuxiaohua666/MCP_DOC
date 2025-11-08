# MCP 文档服务器集成指南

本文档介绍如何将本仓库提供的 MCP 文档服务器接入常用的支持 Model Context Protocol 的工具：Cursor 与 Trae。无论是哪种集成方式，都推荐使用 `start.py`（或直接运行 `mcp-server/mcp_protocol_server.py`），该模式基于官方 MCP STDIO 实现，更适合被 IDE / Agent 拉起并通信。

---

## 通用准备工作

1. **安装依赖**
   ```bash
   pip install -r mcp-server/requirements.txt
   pip install mcp  # 如需标准 MCP 协议支持
   ```
2. **验证文档目录**
   ```bash
   python start.py --server-type rest --skip-checks --host 0.0.0.0 --port 7778
   # 浏览 http://localhost:7778/health 确认数据正常
   ```
3. **准备标准 MCP 启动命令**
   ```bash
   python start.py --skip-checks
   ```
   > 该命令会在 STDIO 模式下启动 MCP 协议服务器，便于各类 Agent 通过子进程方式调用。

---

## 在 Cursor 中添加 MCP 服务

Cursor 目前（2025.11）通过实验性设置支持自定义 MCP 服务器。以下步骤假设你运行的是 0.45+ 版本，并已开启 “Model Context” 功能。

1. **打开 Cursor 设置**
   - `Ctrl+,`（或 `Cmd+,`） → `Labs / Experimental` → 启用 *Model Context Protocol*。
2. **添加自定义 MCP Server**
   - 进入 `Settings -> Integrations -> Model Context`.
   - 点击 `Add MCP Server`，填写信息：
     - **Name:** `mcp-docs`
     - **Command:** `python`
    - **Arguments:** `start.py --skip-checks`
     - **Working Directory:** `D:\data\MCP`（请根据实际路径调整）
     - 可选：设置环境变量 `MCP_ROOT=mcp-docs`、`PYTHONUTF8=1`。
3. **保存并测试**
   - 保存配置后，在 Cursor 命令面板中搜索 `MCP: Refresh Servers` 或重启 Cursor。
   - 打开聊天面板，输入 `list resources from mcp-docs` 验证是否能列出文档。

> **JSON 配置方式（旧版本或手动管理）**  
> 在 `%APPDATA%\Cursor\cursor-settings.json`（Windows）或 `~/Library/Application Support/Cursor/cursor-settings.json`（macOS）中添加：
> ```json
> {
>   "mcpServers": [
>     {
>       "name": "mcp-docs",
>       "command": "python",
>       "args": ["start.py", "--server-type", "mcp", "--skip-checks"],
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

Trae（https://trae.ai/）支持通过配置文件加载自定义 MCP 服务器。以下步骤基于 0.12+ 版本的桌面应用：

1. **准备启动命令**
   - 建议创建一个脚本（例如 `scripts/start-mcp-docs.cmd`），内容如下：
     ```cmd
     @echo off
     cd /d D:\data\MCP
     set PYTHONUTF8=1
    python start.py --skip-checks
     ```
   - macOS / Linux 可使用 `.sh` 版本。
2. **编辑 Trae 配置**
   - 打开 Trae，进入 `Settings -> Model Context`.
   - 选择 `Add Server`，配置：
     - **Name:** `mcp-docs`
     - **Command:** 指向上述脚本（或直接填 `python`）
    - **Arguments:** `start.py --skip-checks`
     - **Working Directory:** `D:\data\MCP`
     - 环境变量同样可设置 `MCP_ROOT`。
3. **验证连接**
   - 在 Trae 的 MCP 侧边栏中刷新服务器列表。
   - 选择 `mcp-docs`，尝试调用 `listResources` / `search_documentation` 等工具，确认能返回项目文档。

> 若 Trae 需要 JSON/YAML 配置（例如 `~/.trae/mcp.config.json`），可参考：
> ```json
> {
>   "servers": {
>     "mcp-docs": {
>       "command": "python",
>       "args": ["start.py", "--server-type", "mcp", "--skip-checks"],
>       "cwd": "D:/data/MCP",
>       "env": {
>         "MCP_ROOT": "mcp-docs",
>         "PYTHONUTF8": "1"
>       }
>     }
>   }
> }
> ```

---

## 常见问题

| 问题 | 处理方案 |
| ---- | -------- |
| Cursor / Trae 启动命令无法找到仓库路径 | 确保 `cwd` 配置正确，或在命令中使用绝对路径 |
| 终端乱码或中文显示异常 | 设置 `PYTHONUTF8=1`（Windows）或在命令前添加 `SET PYTHONIOENCODING=utf-8` |
| 服务启动后立即退出 | 检查是否缺少 `mcp` 库；使用 `pip install mcp` |
| 工具列表为空 | 确认 `mcp-docs/mcp-config.json` 中列出了语言/项目，且目录结构完整 |

---

完成以上配置后，就可以在 Cursor、Trae 里直接调用文档服务器提供的数据和工具，辅助开发与文档撰写。欢迎结合各自的自动化脚本（质量检查、模板生成等）进一步集成。 

