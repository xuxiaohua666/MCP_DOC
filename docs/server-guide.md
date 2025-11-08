# MCP文档服务器实现说明

本项目提供两种启动方式：

1. **MCP 协议服务器（STDIO）**：由 `mcp_protocol_server.py` 实现，适合 Cursor、Trae、Claude Desktop 等客户端直接拉起进程使用。
2. **HTTP 网关**：`http_server.py` 提供 FastAPI/JSON 接口，可共享给远程客户端使用。

## 📁 服务器目录结构

```
mcp-server/
├── mcp_protocol_server.py   # STDIO MCP 服务器
├── http_server.py           # HTTP 网关（FastAPI）
├── mcp-config.json          # 配置文件
├── requirements.txt         # 依赖 (mcp, fastapi, uvicorn)
└── scripts/                 # 辅助脚本
```

## ⚙️ MCP 协议服务器 (`mcp_protocol_server.py`)

- 基于官方 `mcp` Python SDK，实现 `listResources`、`readResource`、`listTools`、`callTool` 等接口。
- 资源来源：`mcp-docs/` 下的项目、模块、README、元数据。
- 工具：
  - `search_documentation`
  - `analyze_project_structure`
  - `check_documentation_quality`
- 运行方式：
  ```bash
  pip install mcp
  python start.py --mode mcp --skip-checks
  # 或者直接: python mcp-server/mcp_protocol_server.py --mcp-root mcp-docs
  ```

## 🌐 HTTP 网关 (`http_server.py`)

- FastAPI 实现，提供与 `mcp_protocol_server.py` 相同的数据读取逻辑。
- 典型接口：
  - `GET /health`
  - `GET /languages`
  - `GET /projects`、`/projects/{language}`、`/projects/{language}/{project}`
  - `GET /modules/{language}/{project}`
  - `GET /search?q=...`
  - `POST /tools/{name}` 调用搜索 / 分析等工具
- 支持 CORS，可通过 `--allow-origin` 多次传入允许的域。
- 运行方式：
  ```bash
  pip install -r mcp-server/requirements.txt
  python start.py --mode http --host 0.0.0.0 --port 7778
  ```
- 客户端配置示例（Cursor `mcp.json`）：
  ```json
  {
    "mcpServers": {
      "mcp-docs-http": {
        "url": "http://server-host:7778"
      }
    }
  }
  ```

## 🧩 配置与扩展

- 更新 `mcp-server/mcp-config.json` 以增加语言/模板。
- 在 `mcp_protocol_server.py` / `http_server.py` 中扩展工具注册逻辑，即可新增自定义分析工具。
- 使用 `mcp-server/scripts/` 的辅助脚本保持文档质量一致性。

## ❗ 常见问题

| 场景 | 解决方案 |
| ---- | -------- |
| 启动时报 `mcp` 未找到 | `pip install mcp` |
| HTTP 模式报 FastAPI/Uvicorn 缺失 | `pip install -r mcp-server/requirements.txt` |
| 客户端无法连接 STDIO 服务 | 检查命令、工作目录、`MCP_ROOT` 环境变量 |
| 客户端无法连接 HTTP 服务 | 检查 URL、端口、防火墙及认证配置 |

---
如需更复杂的部署（HTTPS、认证、负载均衡等），可在此基础上增加反向代理或统一网关。欢迎按项目需求扩展。
