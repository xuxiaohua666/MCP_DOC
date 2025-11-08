# MCP文档服务器 - 快速开始指南

## 概述
MCP文档服务器是一个专为AI辅助开发设计的知识库系统，通过 **Model Context Protocol (MCP)** 向 IDE 与智能体暴露项目文档、元数据和辅助工具。

## 安装和运行

### 1. 安装依赖
```bash
pip install mcp
```

### 2. 启动服务器

#### 🌐 共享给其他客户端（HTTP 网关，默认）
```bash
pip install -r mcp-server/requirements.txt
python start.py --mode http --host 0.0.0.0 --port 7778
```
在远程客户端的 `mcp.json` 中配置：
```json
{
  "mcpServers": {
    "mcp-docs-http": {
      "url": "http://server-host:7778",
      "headers": {
        "Authorization": "Bearer <your-token>"
      }
    }
  }
}
```
`Authorization` 可按需自定义或移除。

#### 🔄 本地客户端（STDIO 模式）
```bash
python start.py --mode mcp --skip-checks
```
启动后，脚本会提示在 Cursor / Trae / Claude Desktop 中使用的命令：
```
Command : python
Args    : start.py --mode mcp --skip-checks
Workdir : /path/to/MCP
```
客户端会按需启动 MCP 进程，配置完成后脚本窗口可以关闭。

## 使用工具集

### 1. 文档质量检查
```bash
# 检查所有文档
python mcp-server/scripts/quality-checker.py

# 检查特定目录并保存报告
python mcp-server/scripts/quality-checker.py --mcp-root . --output quality-report.json

# 包含外部链接检查（较慢）
python mcp-server/scripts/quality-checker.py --check-links
```

### 2. 模板处理
```bash
# 为Java项目生成文档
python mcp-server/scripts/template-processor.py --project-path ./mcp-docs/Java/my-project --language java

# 生成模块文档
python mcp-server/scripts/template-processor.py --project-path ./mcp-docs/Java/my-project/module --language java --template-type module
```

### 3. 自动化监控
```bash
# 运行一次监控检查
python mcp-server/scripts/mcp-auto-update.py --once

# 持续监控（每5分钟检查一次）
python mcp-server/scripts/mcp-auto-update.py --interval 300

# 只验证文档
python mcp-server/scripts/mcp-auto-update.py --validate-only
```

### 4. 性能监控
```bash
# 分析最近7天的性能
python mcp-server/scripts/performance-monitor.py --action analyze --days 7

# 生成性能报告
python mcp-server/scripts/performance-monitor.py --action report --output performance-report.json

# 清理30天前的旧数据
python mcp-server/scripts/performance-monitor.py --action cleanup --cleanup-days 30
```

### 5. Git集成
```bash
# 安装Git hooks
python mcp-server/scripts/install-git-hooks.py --action install

# 检查hooks状态
python mcp-server/scripts/install-git-hooks.py --action status

# 卸载hooks
python mcp-server/scripts/install-git-hooks.py --action uninstall
```

## 开源MCP服务器选项

如果您想使用标准的MCP协议，以下是一些开源选项：

### 1. 官方MCP Server (Python)
```bash
# 安装官方MCP库
pip install mcp

# 参考实现
git clone https://github.com/modelcontextprotocol/servers.git
```

### 2. 其他开源MCP服务器
- **mcp-server-git**: Git仓库集成
- **mcp-server-filesystem**: 文件系统访问
- **mcp-server-sqlite**: SQLite数据库集成

### 3. 与Claude Desktop集成
```json
{
  "mcpServers": {
    "mcp-docs": {
      "command": "python",
      "args": ["/path/to/start.py", "--mode", "mcp", "--skip-checks"],
      "env": {
        "MCP_ROOT": "/path/to/your/docs"
      }
    }
  }
}
```

## 目录结构
确保您的 MCP 目录结构如下：
```
MCP/
├── docs/                   # 文档中心
│   ├── README.md
│   ├── GETTING_STARTED.md
│   ├── server-guide.md
│   └── standards/          # 开发规范
├── mcp-server/             # 服务器实现
│   ├── http_server.py          # HTTP 网关（默认）
│   ├── mcp_protocol_server.py # MCP协议服务器
│   ├── mcp-config.json     # 配置文件
│   ├── requirements.txt    # Python依赖
│   └── scripts/            # 工具脚本
└── mcp-docs/               # 文档和示例
    ├── templates/          # 文档模板
    ├── Java/               # Java项目目录
    │   └── example-web-service/
    └── GDScript/           # GDScript项目目录
        └── example-game-project/
```

## 常见问题

### Q: 如何添加新的编程语言支持？
A: 参考 `docs/standards/language-extension-guide.md` 中的详细说明。

### Q: 如何自定义文档模板？
A: 编辑 `mcp-docs/templates/` 目录下的模板文件，或创建语言特定的模板。

### Q: 如何备份文档数据？
A: 整个MCP目录就是您的数据，可以直接备份整个目录。

### Q: 服务器启动失败怎么办？
A: 检查：
1. 是否已安装 `mcp` 依赖（HTTP 模式还需 fastapi、uvicorn）
2. `mcp-server/mcp-config.json` 与 `mcp-docs/mcp-config.json` 是否存在且格式正确
3. 运行目录是否位于项目根目录

### Q: 如何与AI工具集成？
A: 使用标准 MCP 协议连接，详见 `docs/integration-guide.md` 中的 Cursor / Trae / HTTP 配置示例。

## 下一步

1. **配置您的项目**: 在mcp-docs对应语言目录下创建项目
2. **设置Git hooks**: 启用自动文档更新
3. **配置监控**: 设置性能监控和质量检查
4. **集成AI工具**: 连接您喜欢的AI开发工具

## 支持和贡献

- 查看 `README.md` 了解完整的系统架构
- 参考 `docs/standards/` 目录下的规范文档
- 提交问题和改进建议

---
*开始您的AI辅助开发之旅！*
