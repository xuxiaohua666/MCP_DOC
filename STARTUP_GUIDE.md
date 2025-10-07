# MCP文档服务器启动指南

## 🚀 快速启动

### Windows用户

#### 方法1：双击启动（推荐）
```
双击 start.bat 文件
```

#### 方法2：PowerShell启动
```powershell
.\start.ps1
```

#### 方法3：Python启动器
```cmd
python start.py
```

### Linux/Mac用户

#### 方法1：Shell脚本
```bash
chmod +x start.sh
./start.sh
```

#### 方法2：Python启动器
```bash
python3 start.py
```

## 🔧 高级启动选项

### Python启动器选项

```bash
# 启动REST API服务器（默认）
python start.py

# 启动MCP协议服务器
python start.py --server-type mcp

# 自动选择服务器类型
python start.py --server-type auto

# 自定义主机和端口
python start.py --host 0.0.0.0 --port 8080

# 详细输出模式
python start.py --verbose

# 跳过环境检查
python start.py --skip-checks
```

### 直接启动服务器

```bash
# REST API服务器
python mcp-server/documentation_server.py --mcp-root mcp-docs

# MCP协议服务器
python mcp-server/mcp_protocol_server.py

# 智能启动器
python mcp-server/start_server.py
```

## 📋 启动前检查

启动脚本会自动检查：

1. ✅ **Python环境** - 确保Python已安装
2. ✅ **依赖包** - 自动安装fastapi, uvicorn, pydantic, requests
3. ✅ **配置文件** - 确保mcp-config.json存在
4. ✅ **目录结构** - 验证mcp-docs目录结构

## 🌐 访问地址

服务器启动后，可以通过以下地址访问：

- **API文档**: http://127.0.0.1:7778/docs
- **健康检查**: http://127.0.0.1:7778/health
- **所有项目**: http://127.0.0.1:7778/projects
- **Java项目**: http://127.0.0.1:7778/projects/java
- **GDScript项目**: http://127.0.0.1:7778/projects/gdscript
- **搜索功能**: http://127.0.0.1:7778/search?q=关键词

## 🔍 故障排除

### 问题1：Python未找到
```
解决方案：安装Python 3.8+版本
```

### 问题2：依赖包安装失败
```
解决方案：手动安装
pip install fastapi uvicorn pydantic requests
```

### 问题3：配置文件缺失
```
解决方案：确保mcp-server/mcp-config.json存在
```

### 问题4：端口被占用
```
解决方案：使用不同端口
python start.py --port 8080
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
