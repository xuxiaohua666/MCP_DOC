#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完全兼容Continue的MCP服务器
基于用户分析，实现Continue客户端期望的所有关键方法：
1. listResources() - 列出资源
2. listTools() - 列出工具  
3. listPrompts() - 列出提示（Continue特有）
4. listResourceTemplates() - 列出资源模板（解决"resource templates"加载问题）
"""

import asyncio
import json
import sys
from pathlib import Path

# 确保MCP库可用
try:
    from mcp.server import Server
    from mcp.server.models import InitializationOptions
    from mcp.server.stdio import stdio_server
    from mcp import types
    from mcp.server import NotificationOptions
except ImportError:
    print("MCP library not found. Please install with: pip install mcp")
    sys.exit(1)

# 创建服务器实例
server = Server("mcp-documentation")

# 全局变量存储MCP根目录
mcp_root = Path("D:/data/MCP/mcp-docs")

# ========== 场景1: Continue客户端依赖的基础方法 ==========

@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    """列出可用资源 - Continue客户端无条件调用的基础方法"""
    resources = []
    
    # 添加文档模板资源
    resources.extend([
        types.Resource(
            uri="template://project-readme",
            name="Project README Template",
            description="项目README模板",
            mimeType="text/markdown"
        ),
        types.Resource(
            uri="template://api-doc", 
            name="API Documentation Template",
            description="API文档模板",
            mimeType="text/markdown"
        ),
        types.Resource(
            uri="template://module-doc",
            name="Module Documentation Template", 
            description="模块文档模板",
            mimeType="text/markdown"
        ),
        types.Resource(
            uri="template://coding-standards",
            name="Coding Standards Template",
            description="编码规范模板",
            mimeType="text/markdown"
        )
    ])
    
    # 添加项目资源
    if mcp_root.exists():
        for lang_dir in mcp_root.glob("*"):
            if lang_dir.is_dir() and lang_dir.name != "templates":
                for project_dir in lang_dir.glob("*"):
                    if project_dir.is_dir():
                        resources.append(
                            types.Resource(
                                uri=f"project://{lang_dir.name}/{project_dir.name}",
                                name=f"{project_dir.name} ({lang_dir.name})",
                                description=f"{lang_dir.name}项目: {project_dir.name}",
                                mimeType="application/json"
                            )
                        )
    
    return resources

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """列出可用工具 - Continue客户端无条件调用的基础方法"""
    return [
        types.Tool(
            name="search_documentation",
            description="搜索文档内容",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索关键词"
                    },
                    "language": {
                        "type": "string",
                        "description": "编程语言（可选）",
                        "enum": ["Java", "GDScript", "all"]
                    }
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="list_projects", 
            description="列出所有项目",
            inputSchema={
                "type": "object",
                "properties": {
                    "language": {
                        "type": "string",
                        "description": "编程语言（可选）",
                        "enum": ["Java", "GDScript", "all"]
                    }
                }
            }
        ),
        types.Tool(
            name="get_project_info",
            description="获取项目详细信息", 
            inputSchema={
                "type": "object",
                "properties": {
                    "project_name": {
                        "type": "string",
                        "description": "项目名称"
                    },
                    "language": {
                        "type": "string",
                        "description": "编程语言"
                    }
                },
                "required": ["project_name"]
            }
        ),
        types.Tool(
            name="analyze_project_structure",
            description="分析项目结构和依赖关系",
            inputSchema={
                "type": "object", 
                "properties": {
                    "project_name": {
                        "type": "string",
                        "description": "项目名称"
                    },
                    "language": {
                        "type": "string",
                        "description": "编程语言"
                    }
                },
                "required": ["project_name"]
            }
        ),
        types.Tool(
            name="check_documentation_quality",
            description="检查文档质量和完整性",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_name": {
                        "type": "string", 
                        "description": "项目名称"
                    },
                    "language": {
                        "type": "string",
                        "description": "编程语言"
                    }
                },
                "required": ["project_name"]
            }
        ),
        types.Tool(
            name="create_documentation",
            description="创建项目文档",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_name": {
                        "type": "string",
                        "description": "项目名称"
                    },
                    "language": {
                        "type": "string",
                        "description": "编程语言"
                    },
                    "template": {
                        "type": "string",
                        "description": "使用的模板",
                        "enum": ["project-readme", "api-doc", "module-doc"]
                    }
                },
                "required": ["project_name", "language", "template"]
            }
        )
    ]

# ========== 场景2: 资源模板加载相关方法 ==========

@server.list_resource_templates()
async def handle_list_resource_templates() -> list[types.ResourceTemplate]:
    """列出资源模板 - 解决Continue的"resource templates"加载问题"""
    return [
        types.ResourceTemplate(
            uriTemplate="template://{template_name}",
            name="Documentation Template",
            description="文档模板集合",
            mimeType="text/markdown"
        ),
        types.ResourceTemplate(
            uriTemplate="project://{language}/{project_name}",
            name="Project Resource",
            description="项目资源",
            mimeType="application/json"
        )
    ]

# ========== Continue特有的listPrompts方法 ==========

@server.list_prompts()
async def handle_list_prompts() -> list[types.Prompt]:
    """列出可用提示 - Continue客户端期望的方法"""
    return [
        types.Prompt(
            name="documentation_review",
            description="审查项目文档质量",
            arguments=[
                types.PromptArgument(
                    name="project_name",
                    description="项目名称",
                    required=True
                ),
                types.PromptArgument(
                    name="language", 
                    description="编程语言",
                    required=True
                )
            ]
        ),
        types.Prompt(
            name="generate_api_docs",
            description="生成API文档",
            arguments=[
                types.PromptArgument(
                    name="project_name",
                    description="项目名称", 
                    required=True
                ),
                types.PromptArgument(
                    name="language",
                    description="编程语言",
                    required=True
                )
            ]
        ),
        types.Prompt(
            name="analyze_project",
            description="分析项目结构和依赖",
            arguments=[
                types.PromptArgument(
                    name="project_name",
                    description="项目名称",
                    required=True
                )
            ]
        )
    ]

# ========== 资源读取处理器 ==========

@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """读取资源内容"""
    if uri.startswith("template://"):
        template_name = uri.replace("template://", "")
        
        templates = {
            "project-readme": """# Project README Template

## 项目概述
简要描述项目的目的和功能。

## 技术栈
- 编程语言: {language}
- 主要框架: {framework}
- 数据库: {database}
- 其他依赖: {dependencies}

## 安装和运行
\`\`\`bash
# 安装依赖
{install_command}

# 运行项目
{run_command}
\`\`\`

## API文档
详细的API接口说明。

## 贡献指南
如何为项目做出贡献。

## 许可证
{license}
""",
            "api-doc": """# API Documentation Template

## 概述
API接口文档说明。

## 认证
描述认证方式。

## 端点列表

### GET /api/{endpoint}
**描述**: 获取数据
**参数**: 
- \`param1\`: 参数说明
**响应**: 
\`\`\`json
{
  "status": "success",
  "data": {}
}
\`\`\`

### POST /api/{endpoint}
**描述**: 创建数据
**请求体**:
\`\`\`json
{
  "field1": "value1",
  "field2": "value2"
}
\`\`\`
**响应**:
\`\`\`json
{
  "status": "success",
  "id": "new_id"
}
\`\`\`
""",
            "module-doc": """# Module Documentation Template

## 模块概述
模块的功能和用途说明。

## 接口列表

### 类名
**描述**: 类的作用

**方法**:
- \`method1()\`: 方法说明
- \`method2()\`: 方法说明

**示例**:
\`\`\`python
# 使用示例
\`\`\`

### 函数
**描述**: 函数的作用

**参数**:
- \`param1\`: 参数说明
- \`param2\`: 参数说明

**返回值**: 返回值说明

**示例**:
\`\`\`python
# 使用示例
\`\`\`
""",
            "coding-standards": """# Coding Standards Template

## 代码规范

### 命名规范
- 变量名: 小写字母和下划线
- 函数名: 小写字母和下划线
- 类名: 大驼峰命名法
- 常量: 大写字母和下划线

### 代码格式
- 缩进: 4个空格
- 行长度: 不超过100字符
- 空行: 函数之间用2个空行分隔

### 注释规范
- 文件头注释
- 函数注释
- 行内注释

### 错误处理
- 异常处理
- 日志记录
- 错误恢复
"""
        }
        
        return templates.get(template_name, f"Template not found: {template_name}")
    
    elif uri.startswith("project://"):
        # 处理项目资源
        parts = uri.replace("project://", "").split("/")
        if len(parts) == 2:
            lang, project = parts
            project_path = mcp_root / lang / project
            
            if project_path.exists():
                project_info = {
                    "language": lang,
                    "project": project,
                    "path": str(project_path),
                    "files": [],
                    "documentation": []
                }
                
                # 读取项目文件信息
                for file_path in project_path.rglob("*"):
                    if file_path.is_file():
                        project_info["files"].append({
                            "name": file_path.name,
                            "path": str(file_path.relative_to(project_path)),
                            "size": file_path.stat().st_size,
                            "type": file_path.suffix
                        })
                        
                        # 收集文档文件
                        if file_path.suffix in ['.md', '.txt', '.rst']:
                            try:
                                content = file_path.read_text(encoding='utf-8')
                                project_info["documentation"].append({
                                    "file": str(file_path.relative_to(project_path)),
                                    "preview": content[:200] + "..." if len(content) > 200 else content
                                })
                            except:
                                pass
                
                return json.dumps(project_info, ensure_ascii=False, indent=2)
    
    return f"Resource not found: {uri}"

# ========== 工具调用处理器 ==========

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """调用工具"""
    if name == "search_documentation":
        query = arguments.get("query", "").lower()
        language = arguments.get("language", "all")
        results = []
        
        if mcp_root.exists():
            for lang_dir in mcp_root.glob("*"):
                if lang_dir.is_dir() and lang_dir.name != "templates":
                    if language != "all" and language != lang_dir.name:
                        continue
                        
                    for project_dir in lang_dir.glob("*"):
                        if project_dir.is_dir():
                            for file_path in project_dir.rglob("*.md"):
                                if file_path.exists():
                                    try:
                                        content = file_path.read_text(encoding='utf-8')
                                        if query in content.lower():
                                            results.append({
                                                "language": lang_dir.name,
                                                "project": project_dir.name,
                                                "file": str(file_path.relative_to(project_dir)),
                                                "match": query,
                                                "preview": content[:300] + "..." if len(content) > 300 else content
                                            })
                                    except:
                                        pass
        
        return [types.TextContent(
            type="text", 
            text=json.dumps({"query": query, "language": language, "results": results}, ensure_ascii=False, indent=2)
        )]
    
    elif name == "list_projects":
        language = arguments.get("language", "all")
        projects = []
        
        if mcp_root.exists():
            for lang_dir in mcp_root.glob("*"):
                if lang_dir.is_dir() and lang_dir.name != "templates":
                    if language != "all" and language != lang_dir.name:
                        continue
                        
                    for project_dir in lang_dir.glob("*"):
                        if project_dir.is_dir():
                            projects.append({
                                "language": lang_dir.name,
                                "project": project_dir.name,
                                "path": str(project_dir),
                                "files_count": len(list(project_dir.rglob("*")))
                            })
        
        return [types.TextContent(
            type="text",
            text=json.dumps({"language": language, "projects": projects}, ensure_ascii=False, indent=2)
        )]
    
    elif name == "get_project_info":
        project_name = arguments.get("project_name", "")
        language = arguments.get("language", "")
        
        project_info = {"project": project_name, "language": language, "found": False}
        
        if mcp_root.exists():
            search_dirs = []
            if language:
                search_dirs = [mcp_root / language]
            else:
                search_dirs = [d for d in mcp_root.glob("*") if d.is_dir() and d.name != "templates"]
            
            for lang_dir in search_dirs:
                project_dir = lang_dir / project_name
                if project_dir.exists():
                    project_info.update({
                        "found": True,
                        "language": lang_dir.name,
                        "path": str(project_dir),
                        "files": []
                    })
                    
                    # 读取所有文件信息
                    for file_path in project_dir.rglob("*"):
                        if file_path.is_file():
                            project_info["files"].append({
                                "name": file_path.name,
                                "path": str(file_path.relative_to(project_dir)),
                                "size": file_path.stat().st_size,
                                "type": file_path.suffix
                            })
                    
                    # 读取README
                    readme_path = project_dir / "README.md"
                    if readme_path.exists():
                        try:
                            project_info["readme"] = readme_path.read_text(encoding='utf-8')
                        except:
                            project_info["readme"] = "Error reading README"
                    
                    break
        
        return [types.TextContent(
            type="text",
            text=json.dumps(project_info, ensure_ascii=False, indent=2)
        )]
    
    elif name == "analyze_project_structure":
        project_name = arguments.get("project_name", "")
        language = arguments.get("language", "")
        
        analysis = {"project": project_name, "language": language, "found": False}
        
        if mcp_root.exists():
            search_dirs = []
            if language:
                search_dirs = [mcp_root / language]
            else:
                search_dirs = [d for d in mcp_root.glob("*") if d.is_dir() and d.name != "templates"]
            
            for lang_dir in search_dirs:
                project_dir = lang_dir / project_name
                if project_dir.exists():
                    analysis.update({
                        "found": True,
                        "language": lang_dir.name,
                        "structure": [],
                        "statistics": {
                            "total_files": 0,
                            "total_dirs": 0,
                            "file_types": {}
                        }
                    })
                    
                    for item in project_dir.rglob("*"):
                        if item.is_file():
                            analysis["structure"].append({
                                "type": "file",
                                "name": item.name,
                                "path": str(item.relative_to(project_dir)),
                                "size": item.stat().st_size
                            })
                            analysis["statistics"]["total_files"] += 1
                            
                            # 统计文件类型
                            ext = item.suffix or "no_extension"
                            analysis["statistics"]["file_types"][ext] = analysis["statistics"]["file_types"].get(ext, 0) + 1
                            
                        elif item.is_dir():
                            analysis["structure"].append({
                                "type": "directory", 
                                "name": item.name,
                                "path": str(item.relative_to(project_dir))
                            })
                            analysis["statistics"]["total_dirs"] += 1
                    
                    break
        
        return [types.TextContent(
            type="text",
            text=json.dumps(analysis, ensure_ascii=False, indent=2)
        )]
    
    elif name == "check_documentation_quality":
        project_name = arguments.get("project_name", "")
        language = arguments.get("language", "")
        
        quality_report = {"project": project_name, "language": language, "found": False}
        
        if mcp_root.exists():
            search_dirs = []
            if language:
                search_dirs = [mcp_root / language]
            else:
                search_dirs = [d for d in mcp_root.glob("*") if d.is_dir() and d.name != "templates"]
            
            for lang_dir in search_dirs:
                project_dir = lang_dir / project_name
                if project_dir.exists():
                    quality_report.update({
                        "found": True,
                        "language": lang_dir.name,
                        "checks": [],
                        "score": 0,
                        "max_score": 10
                    })
                    
                    # 检查README
                    readme_path = project_dir / "README.md"
                    if readme_path.exists():
                        quality_report["checks"].append({
                            "type": "readme",
                            "status": "present",
                            "size": readme_path.stat().st_size,
                            "score": 3
                        })
                        quality_report["score"] += 3
                    else:
                        quality_report["checks"].append({
                            "type": "readme",
                            "status": "missing",
                            "score": 0
                        })
                    
                    # 检查API文档
                    api_docs = list(project_dir.glob("*api*.md")) + list(project_dir.glob("*API*.md"))
                    if api_docs:
                        quality_report["checks"].append({
                            "type": "api_documentation",
                            "status": "present",
                            "files": [f.name for f in api_docs],
                            "score": 2
                        })
                        quality_report["score"] += 2
                    else:
                        quality_report["checks"].append({
                            "type": "api_documentation",
                            "status": "missing",
                            "score": 0
                        })
                    
                    # 检查其他文档文件
                    doc_files = list(project_dir.glob("*.md"))
                    if len(doc_files) >= 2:
                        quality_report["checks"].append({
                            "type": "documentation_files",
                            "status": "good",
                            "count": len(doc_files),
                            "files": [f.name for f in doc_files],
                            "score": 2
                        })
                        quality_report["score"] += 2
                    elif len(doc_files) == 1:
                        quality_report["checks"].append({
                            "type": "documentation_files",
                            "status": "basic",
                            "count": len(doc_files),
                            "files": [f.name for f in doc_files],
                            "score": 1
                        })
                        quality_report["score"] += 1
                    else:
                        quality_report["checks"].append({
                            "type": "documentation_files",
                            "status": "missing",
                            "count": 0,
                            "score": 0
                        })
                    
                    # 检查代码注释
                    code_files = []
                    for ext in ['.py', '.java', '.gd', '.js', '.ts']:
                        code_files.extend(list(project_dir.rglob(f"*{ext}")))
                    
                    if code_files:
                        quality_report["checks"].append({
                            "type": "code_files",
                            "status": "present",
                            "count": len(code_files),
                            "score": 1
                        })
                        quality_report["score"] += 1
                    else:
                        quality_report["checks"].append({
                            "type": "code_files",
                            "status": "missing",
                            "score": 0
                        })
                    
                    # 检查项目结构
                    if (project_dir / "src").exists() or (project_dir / "lib").exists() or (project_dir / "app").exists():
                        quality_report["checks"].append({
                            "type": "project_structure",
                            "status": "good",
                            "score": 2
                        })
                        quality_report["score"] += 2
                    else:
                        quality_report["checks"].append({
                            "type": "project_structure",
                            "status": "basic",
                            "score": 1
                        })
                        quality_report["score"] += 1
                    
                    break
        
        return [types.TextContent(
            type="text",
            text=json.dumps(quality_report, ensure_ascii=False, indent=2)
        )]
    
    elif name == "create_documentation":
        project_name = arguments.get("project_name", "")
        language = arguments.get("language", "")
        template = arguments.get("template", "")
        
        result = {
            "project": project_name,
            "language": language,
            "template": template,
            "created": False,
            "message": ""
        }
        
        if mcp_root.exists():
            for lang_dir in mcp_root.glob("*"):
                if lang_dir.is_dir() and lang_dir.name == language:
                    project_dir = lang_dir / project_name
                    if project_dir.exists():
                        # 根据模板创建文档
                        template_content = await handle_read_resource(f"template://{template}")
                        
                        if template == "project-readme":
                            doc_path = project_dir / "README.md"
                        elif template == "api-doc":
                            doc_path = project_dir / "API.md"
                        elif template == "module-doc":
                            doc_path = project_dir / "MODULE.md"
                        else:
                            doc_path = project_dir / f"{template.upper()}.md"
                        
                        try:
                            # 替换模板变量
                            content = template_content.format(
                                language=language,
                                framework="",
                                database="",
                                dependencies="",
                                install_command="",
                                run_command="",
                                license="MIT",
                                endpoint="example"
                            )
                            
                            doc_path.write_text(content, encoding='utf-8')
                            result.update({
                                "created": True,
                                "message": f"文档已创建: {doc_path}",
                                "path": str(doc_path)
                            })
                        except Exception as e:
                            result["message"] = f"创建文档失败: {e}"
                        
                        break
            else:
                result["message"] = f"语言目录不存在: {language}"
        else:
            result["message"] = f"MCP根目录不存在: {mcp_root}"
        
        return [types.TextContent(
            type="text",
            text=json.dumps(result, ensure_ascii=False, indent=2)
        )]
    
    return [types.TextContent(type="text", text=f"Unknown tool: {name}")]

# ========== 提示调用处理器 ==========

@server.get_prompt()
async def handle_get_prompt(name: str, arguments: dict) -> list[types.PromptMessage]:
    """获取提示内容 - Continue期望的方法"""
    if name == "documentation_review":
        return [
            types.PromptMessage(
                role="user",
                content=types.TextContent(
                    type="text",
                    text=f"""请审查项目 {arguments.get('project_name', '')} ({arguments.get('language', '')}) 的文档质量：

1. 检查README文件的完整性
2. 评估API文档的详细程度
3. 分析代码注释的质量
4. 提供改进建议

请提供详细的审查报告和改进建议。"""
                )
            )
        ]
    elif name == "generate_api_docs":
        return [
            types.PromptMessage(
                role="user",
                content=types.TextContent(
                    type="text",
                    text=f"""为项目 {arguments.get('project_name', '')} ({arguments.get('language', '')}) 生成API文档：

1. 分析项目结构
2. 识别API端点
3. 生成详细的接口文档
4. 包含请求/响应示例

请生成完整的API文档。"""
                )
            )
        ]
    elif name == "analyze_project":
        return [
            types.PromptMessage(
                role="user",
                content=types.TextContent(
                    type="text",
                    text=f"""分析项目 {arguments.get('project_name', '')} 的结构和依赖：

1. 分析项目架构
2. 识别主要组件
3. 分析依赖关系
4. 评估代码组织

请提供详细的项目分析报告。"""
                )
            )
        ]
    else:
        return [
            types.PromptMessage(
                role="user",
                content=types.TextContent(
                    type="text",
                    text=f"Unknown prompt: {name}"
                )
            )
        ]

async def main():
    """主函数"""
    print("Starting Continue Fully Compatible MCP Server...", file=sys.stderr)
    print(f"MCP Root: {mcp_root}", file=sys.stderr)
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="mcp-documentation",
                server_version="2.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
