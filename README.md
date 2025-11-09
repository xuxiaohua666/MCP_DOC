# MCP 文档服务器（MCP Documentation Server）

基于 Model Context Protocol (MCP) 的本地文档知识库服务器，为 Cursor、Trae、Claude Desktop 等支持 MCP 的工具提供统一的项目文档、元数据与辅助工具。默认以 **HTTP 网关** 形式提供服务，亦可按需使用 **STDIO 模式** 由客户端自行拉起进程。

## ✨ 核心能力

- **资源接口**：暴露 `mcp-docs/` 中的项目、模块、README、元数据等，客户端可通过 MCP `listResources` / `readResource` 读取。
- **工具接口**
  - `search_documentation`：全文检索文档，返回命中片段与路径。
  - `analyze_project_structure`、`list_modules`：获取结构化的项目/模块信息。
  - `check_documentation_quality` 等辅助诊断工具，帮助质量检查。
- **自动化脚本**：`mcp-server/scripts/` 下提供模板生成、质量检查、性能监控等脚本，保持文档与项目同步。

## 🚀 快速上手

### 共享部署（HTTP 网关，默认）

```bash
python -m pip install mcp fastapi uvicorn pydantic requests markdown
python start.py --mode http --host 0.0.0.0 --port 7778
```

在远程客户端的 `mcp.json` 中添加：

```json
{
  "mcpServers": {
    "mcp-docs-http": {
      "url": "http://your-host:7778"
    }
  }
}
```
如需认证，可在反向代理或自定义中间层添加 `Authorization` 头，示例：
```json
{
  "mcpServers": {
    "mcp-docs-http": {
      "url": "http://your-host:7778",
      "headers": {
        "Authorization": "Bearer <token-from-your-auth-system>"
      }
    }
  }
}
```

### 本地客户端（STDIO 模式）

```bash
python -m pip install mcp
python start.py --mode mcp --skip-checks
```

在 Cursor / Trae 中配置：

```
Command : python
Args    : start.py --mode mcp --skip-checks
Workdir : D:\data\MCP
```

客户端会按需启动 MCP 进程；配置完成后脚本窗口可关闭。

## 📁 目录结构

```
MCP/
├── docs/                   # 文档中心（指南、规范）
│   ├── README.md           # 文档索引
│   ├── GETTING_STARTED.md  # 快速开始
│   ├── server-guide.md     # 协议架构与扩展说明
│   ├── integration-guide.md# Cursor/Trae 等客户端配置
│   └── project-setup-guide.md
├── mcp-server/             # MCP 协议实现与脚本
│   ├── http_server.py          # HTTP 网关（默认）
│   ├── mcp_protocol_server.py  # STDIO MCP 服务器
│   ├── mcp-config.json         # 支持语言、模板配置
│   ├── requirements.txt        # 服务器依赖
│   └── scripts/                # 模板生成、质量检查等工具
└── mcp-docs/               # 项目文档与示例
    ├── templates/          # 项目/模块模板
    ├── Java/example-web-service/
    └── GDScript/example-game-project/
```

## 📚 推荐文档

- `docs/GETTING_STARTED.md`：快速开始与常见问题。
- `docs/server-guide.md`：MCP 协议服务器与 HTTP 网关架构、扩展点。
- `docs/integration-guide.md`：Cursor / Trae / HTTP 客户端配置示例。
- `docs/project-setup-guide.md`：基于模板创建新项目（PHP / Java 示例）。

## 🤝 贡献与扩展

- **新增语言/项目**：运行 `python scripts/setup_mcp_project.py`，按提示回答即可自动登记语言并生成 `mcp-docs/<Language>/<Project>/` 目录；详见 `docs/project-setup-guide.md`。
- **新增工具**：在 `http_server.py` / `mcp_protocol_server.py` 中扩展工具注册逻辑，实现自定义分析能力。
- **共享部署**：可结合反向代理、认证网关，对 HTTP 服务增加访问控制；脚本会输出对应配置示例。

欢迎在此基础上扩展自己的文档知识库或二次开发，用 MCP 协议让 AI 助手更好地理解你的项目。
