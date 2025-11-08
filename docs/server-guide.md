# MCP 文档服务器实现说明

本项目现仅提供 **Model Context Protocol (MCP)** 协议实现，所有脚本与文档均围绕 `mcp-server/mcp_protocol_server.py` 这一实现展开。下文将介绍代码结构、协议能力以及如何扩展。

## 📁 目录概览

```
mcp-server/
├── mcp-config.json          # 语言与项目映射配置
├── mcp_protocol_server.py   # MCP 协议服务器主实现
├── requirements.txt         # 依赖（仅需 mcp）
└── scripts/                 # 质量检查、模板处理等辅助脚本
```

## ⚙️ 协议实现要点

`mcp_protocol_server.py` 基于官方 `mcp` Python 库实现，核心要素如下：

- **Server 对象**：`Server("mcp-documentation-server")` 负责注册所有资源与工具。
- **配置加载**：`mcp-docs/mcp-config.json` 描述可用语言、展示名称、默认模板等，启动时会读取到内存。
- **资源注册**（`list_resources`）：
  - 为每个项目生成 `mcp-docs://project/{language}/{project}` 资源。
  - 自动挂载 README、模块 `metadata.json`、模块文档等子资源。
- **资源读取**（`read_resource`）：
  - 根据 URI 读取 JSON 或 Markdown 内容，供客户端直接展示或进一步处理。
- **工具注册**（`list_tools`）：
  - `search_documentation`：全文检索 Markdown/JSON。
  - `analyze_project_structure`、`list_modules`：构建结构化视图。
  - `check_documentation_quality`、`summarize_project`、`compare_projects` 等高级分析工具。
- **运行模式**：通过 `mcp.server.stdio.stdio_server()` 与客户端建立 STDIO 通道，兼容 Cursor、Trae、Claude Desktop 等 MCP 客户端。

## 🚀 启动方式

```bash
pip install mcp
python start.py --server-type mcp            # 或直接执行 start.bat / start.ps1 / start.sh
```

启动脚本会输出推荐的客户端配置命令（Command / Args / Workdir），直接复制到 Cursor、Trae 等工具即可。

## 🔌 客户端集成提示

在支持 MCP 的工具中填入脚本输出的命令即可。例如 Cursor：

```json
{
  "mcpServers": {
    "mcp-docs": {
      "command": "python",
      "args": ["start.py", "--skip-checks"],
      "cwd": "D:/data/MCP",
      "env": {
        "MCP_ROOT": "mcp-docs"
      }
    }
  }
}
```

## 🧩 配置与扩展

- **新增语言**：编辑 `mcp-docs/mcp-config.json`，并在对应目录下创建项目结构（可使用 `docs/project-setup-guide.md` 中的模板流程）。
- **新增工具**：在 `mcp_protocol_server.py` 的 `_register_handlers` 中注册新的 `@self.server.list_tools()` 条目，实现自定义分析逻辑。
- **Wiki 文档**：`docs/wiki/index.json` 列出的 Markdown 会作为资源暴露，方便客户端快速查询集成指南、模板说明等。

## 🛠️ 辅助脚本

`mcp-server/scripts/` 目录提供质量检查、模板生成、性能监控等自动化工具，可配合 MCP 服务使用，保持文档一致性与可读性。

## ❗ 常见问题

| 问题 | 解决方案 |
| ---- | -------- |
| 启动时报错 `mcp` 未找到 | 运行 `pip install mcp` |
| 客户端无法连接 | 确认命令行、工作目录、`MCP_ROOT` 配置正确，且脚本窗口保持打开 |
| 新增语言后未出现在列表 | 检查 `mcp-config.json` 是否正确配置并重启服务器 |

---

如需构建 Web / REST 层，可在此 MCP 服务之上自行扩展。当前仓库聚焦于提供稳定、结构化的 MCP 协议能力。欢迎按照项目需求扩展工具或提交改进建议。
