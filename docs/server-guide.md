# MCP文档服务器实现说明

## 📁 服务器目录结构

```
mcp-server/
├── start_server.py              # 智能启动器
├── mcp-config.json             # 配置文件
├── requirements.txt            # Python依赖
├── documentation_server.py      # REST API服务器（自实现）
└── mcp_protocol_server.py      # MCP协议服务器（使用官方库）
```

## 🔧 两种服务器实现

### 1. REST API服务器 (`documentation_server.py`)

**特点：**
- ✅ **无需额外依赖**：只需 FastAPI + Uvicorn
- ✅ **Web界面友好**：提供Swagger UI文档界面
- ✅ **易于调试**：可直接通过浏览器访问
- ✅ **通用性强**：任何HTTP客户端都可以使用

**适用场景：**
- Web应用集成
- API调试和测试
- 通用的文档查询服务
- 不支持MCP协议的AI工具

**启动方式：**
```bash
python mcp-server/documentation_server.py
# 访问: http://127.0.0.1:8000/docs
```

### 2. MCP协议服务器 (`mcp_protocol_server.py`)

**特点：**
- ✅ **标准协议**：使用官方Model Context Protocol
- ✅ **AI工具集成**：直接支持Claude Desktop等MCP客户端
- ✅ **高效通信**：基于JSON-RPC的结构化通信
- ❗ **需要依赖**：需要安装 `pip install mcp`

**适用场景：**
- Claude Desktop集成
- 支持MCP的AI开发工具
- 标准化的AI上下文提供

**启动方式：**
```bash
# 需要先安装MCP库
pip install mcp
python mcp-server/mcp_protocol_server.py
```

## 🚀 推荐使用方式

### 方案一：一键启动（推荐）
```bash
python mcp-server/start_server.py
```
- 自动检测可用库
- 自动选择最佳服务器
- 简单易用

### 方案二：根据需求选择

**如果您需要：**
- **Web界面调试** → 使用 REST API服务器
- **Claude Desktop集成** → 使用 MCP协议服务器
- **通用API访问** → 使用 REST API服务器
- **标准MCP支持** → 使用 MCP协议服务器

## 🔄 协议对比

| 特性 | REST API | MCP协议 |
|------|----------|---------|
| Web界面 | ✅ Swagger UI | ❌ |
| Claude Desktop | ❌ | ✅ |
| HTTP访问 | ✅ | ❌ |
| 标准化 | 自定义API | ✅ 官方协议 |
| 依赖要求 | 最小 | 需要mcp库 |
| 调试便利 | ✅ 浏览器 | 命令行 |

## 📖 API功能对比

两种服务器都提供相同的核心功能：

- **项目管理**：列出、查询项目信息
- **模块管理**：访问模块文档和元数据
- **文档搜索**：全文搜索文档内容
- **质量检查**：文档质量分析
- **结构分析**：项目结构和依赖分析

**区别在于接口格式：**
- REST API：标准HTTP + JSON
- MCP协议：JSON-RPC + 结构化消息

## 🛠️ 开发和扩展

### 添加新功能
1. 在两个服务器文件中都添加相应功能
2. 保持API一致性
3. 更新文档

### 自定义配置
两个服务器都读取相同的 `mcp-server/mcp-config.json` 配置文件。

### 错误处理
- REST API：HTTP状态码 + JSON错误信息
- MCP协议：结构化错误响应

## 🔗 集成示例

### REST API集成
```python
import requests

# 获取所有项目
response = requests.get("http://127.0.0.1:8000/projects")
projects = response.json()

# 搜索文档
response = requests.get("http://127.0.0.1:8000/search?q=用户管理")
results = response.json()
```

### Claude Desktop集成
在Claude Desktop配置文件中添加：
```json
{
  "mcpServers": {
    "documentation": {
      "command": "python",
      "args": ["D:\\data\\MCP\\mcp-server\\mcp_protocol_server.py"],
      "env": {
        "MCP_ROOT": "D:\\data\\MCP"
      }
    }
  }
}
```

## 📝 注意事项

1. **端口占用**：REST服务器默认使用8000端口
2. **权限**：确保对MCP目录有读取权限
3. **编码**：所有文档使用UTF-8编码
4. **性能**：大型项目建议启用缓存
5. **配置路径**：确保配置文件路径正确指向 `mcp-server/mcp-config.json`

## 🤝 贡献

欢迎提交问题和改进建议！两种服务器实现都欢迎扩展和优化。

---
*选择最适合您需求的服务器实现*
