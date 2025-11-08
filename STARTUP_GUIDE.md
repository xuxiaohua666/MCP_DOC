# MCP文档服务器启动指南

## 🚀 快速启动（HTTP 网关）

启动脚本现在默认运行 **HTTP MCP 网关**，适合共享给 Cursor、Trae、Claude Desktop 等多个客户端。

- **Windows（推荐）**：双击 `start.bat`  
  可选参数：`start.bat <host> <port>`，不传默认 `0.0.0.0 7778`
- **Windows（PowerShell）**：`.
start.ps1 [host] [port]`
- **Linux / macOS**：`chmod +x start.sh && ./start.sh [host] [port]`

脚本会输出示例配置：
```
URL : http://<host>:<port>
用途 : 在远程客户端的 mcp.json 中作为 url 字段
```

> 若需本地（单机）STDIO 模式，可执行 `start.bat stdio`、`.
start.ps1 stdio` 或 `./start.sh stdio`。

## 🔧 高级启动选项

### Python启动器选项

```bash
# 启动HTTP网关（默认）
python start.py --mode http --host 0.0.0.0 --port 7778 --skip-checks

# 启动MCP协议服务器（STDIO）
python start.py --mode mcp --skip-checks

# 详细输出模式（输出更多日志）
python start.py --verbose

# 跳过环境检查
python start.py --skip-checks
```

### 直接启动协议服务器 / 网关

```bash
# 直接运行STDIO MCP服务器
python mcp-server/mcp_protocol_server.py --mcp-root mcp-docs

# 直接运行HTTP网关
python mcp-server/http_server.py --mcp-root mcp-docs --host 0.0.0.0 --port 7778
```

## 📋 启动前检查

启动脚本会自动检查：

1. ✅ **Python环境** - 确保 Python 已安装
2. ✅ **依赖包** - 自动安装 `mcp`（HTTP 模式还需 `fastapi`、`uvicorn`）
3. ✅ **配置文件** - 确保 `mcp-server/mcp-config.json`、`mcp-docs/mcp-config.json` 存在
4. ✅ **目录结构** - 验证 `mcp-docs` 目录结构

## 🔗 连接方式

- **HTTP 客户端**：在 `mcp.json` 或配置界面中设置 `url`（详见 `docs/integration-guide.md`）。
- **STDIO 客户端（本地进程）**：使用 `python start.py --mode mcp --skip-checks` 并在客户端配置 Command/Args。

## 🔍 故障排除

### 问题1：Python未找到
```
解决方案：安装Python 3.8+版本
```

### 问题2：依赖包安装失败
```
解决方案：手动安装
pip install -r mcp-server/requirements.txt
```

### 问题3：配置文件缺失
```
解决方案：确保mcp-server/mcp-config.json存在
```

### 问题4：HTTP 无法访问
```
解决方案：检查端口是否占用、防火墙设置、反向代理/认证配置
```

### 问题5：权限问题（Linux/Mac）
```
解决方案：设置执行权限
chmod +x start.sh
```

## 📝 日志和调试

### 启用详细日志
```bash
python start.py --verbose
```

### 查看服务器日志
服务器会在控制台输出详细的请求日志，包括：
- 启动信息
- 请求处理
- 错误信息

## 🛑 停止服务器

- **Windows**: 按 `Ctrl+C` 或关闭命令窗口
- **Linux/Mac**: 按 `Ctrl+C`
- **后台运行**: 使用 `nohup` 或 `screen` 命令

## 🔄 重启服务器

```bash
# 停止当前服务器（Ctrl+C）
# 然后重新运行启动脚本
python start.py --mode http --host 0.0.0.0 --port 7778
```

## 📞 技术支持

如果遇到问题，请检查：

1. Python版本是否为3.8+
2. 依赖包是否正确安装
3. 配置文件是否存在
4. 端口是否被占用 / 防火墙是否放行
5. 客户端配置是否指向正确的 URL 或命令

---

*启动脚本会自动处理大部分常见问题，让您快速启动共享的 MCP 文档服务器！*
