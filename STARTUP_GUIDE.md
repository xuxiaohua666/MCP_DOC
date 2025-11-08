# MCP文档服务器启动指南

## 🚀 快速启动（MCP 协议）

启动脚本默认运行 **标准 MCP 协议服务器**，适用于 Cursor、Trae、Claude Desktop 等支持 MCP 的工具。

- **Windows（推荐）**：双击 `start.bat`
- **Windows（PowerShell）**：`.\start.ps1`
- **Linux / macOS**：`chmod +x start.sh && ./start.sh`

脚本会提示 MCP 客户端的配置方式：
```
Command : python
Args    : start.py --skip-checks
Workdir : D:\data\MCP
```
在 Cursor、Trae 等工具中填入相同命令即可连接。

## 🔧 高级启动选项

### Python启动器选项

```bash
# 启动MCP协议服务器（脚本已默认）
python start.py

# 详细输出模式（输出更多日志）
python start.py --verbose

# 跳过环境检查
python start.py --skip-checks
```

### 直接启动协议服务器

```bash
# 直接运行标准MCP服务器
python mcp-server/mcp_protocol_server.py --mcp-root mcp-docs
```

## 📋 启动前检查

启动脚本会自动检查：

1. ✅ **Python环境** - 确保 Python 已安装
2. ✅ **依赖包** - 自动安装 `mcp`
3. ✅ **配置文件** - 确保 `mcp-server/mcp-config.json`、`mcp-docs/mcp-config.json` 存在
4. ✅ **目录结构** - 验证 `mcp-docs` 目录结构

## 🔗 连接方式

- **Cursor / Trae / Claude Desktop**：在其 MCP 配置中填入脚本提示的命令（详见 `docs/integration-guide.md`）。
- **自定义客户端**：直接以 `python mcp-server/mcp_protocol_server.py --mcp-root mcp-docs` 方式启动，并使用 MCP STDIO 协议通信。

## 🔍 故障排除

### 问题1：Python未找到
```
解决方案：安装Python 3.8+版本
```

### 问题2：依赖包安装失败
```
解决方案：手动安装
pip install mcp
```

### 问题3：配置文件缺失
```
解决方案：确保mcp-server/mcp-config.json存在
```

### 问题4：权限问题（Linux/Mac）
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
python start.py
```

## 📞 技术支持

如果遇到问题，请检查：

1. Python版本是否为3.8+
2. 依赖包是否正确安装
3. 配置文件是否存在
4. 端口是否被占用
5. 防火墙设置

---

*启动脚本会自动处理大部分常见问题，让您快速启动MCP文档服务器！*
