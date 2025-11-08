#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
标准MCP协议文档服务器实现
使用官方MCP库实现Model Context Protocol
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

# 尝试导入官方MCP库
try:
    import mcp.types as types
    from mcp.server import NotificationOptions, Server
    from mcp.server.models import InitializationOptions
    import mcp.server.stdio
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("官方MCP库未安装。请运行: pip install mcp")

logger = logging.getLogger(__name__)

class MCPDocumentationServer:
    """MCP协议文档服务器"""
    
    def __init__(self, mcp_root: str):
        if not MCP_AVAILABLE:
            raise ImportError("MCP library is required for this server")
            
        self.mcp_root = Path(mcp_root)
        self.server = Server("mcp-documentation-server")
        
        # 加载配置
        self.config = self._load_config()
        
        # 注册handlers
        self._register_handlers()
    
    def _load_config(self) -> Dict:
        """加载MCP配置"""
        try:
            config_path = self.mcp_root / "mcp-config.json"
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load config: {e}")
            return {"supported_languages": []}
    
    def _register_handlers(self):
        """注册MCP消息处理器"""
        
        @self.server.list_resources()
        async def handle_list_resources() -> list[types.Resource]:
            """列出所有可用资源"""
            resources = []
            
            # 遍历所有语言和项目
            for lang_config in self.config.get("supported_languages", []):
                lang_dir = self.mcp_root / lang_config["display_name"]
                if not lang_dir.exists():
                    continue
                
                for project_dir in lang_dir.iterdir():
                    if not project_dir.is_dir():
                        continue
                    
                    project_name = project_dir.name
                    language = lang_config["name"]
                    
                    # 项目资源
                    resources.append(types.Resource(
                        uri=f"mcp-docs://project/{language}/{project_name}",
                        name=f"项目: {project_name} ({language})",
                        description=f"{language}项目的完整文档和元数据",
                        mimeType="application/json"
                    ))
                    
                    # 项目README
                    readme_path = project_dir / "README.md"
                    if readme_path.exists():
                        resources.append(types.Resource(
                            uri=f"mcp-docs://readme/{language}/{project_name}",
                            name=f"README: {project_name}",
                            description=f"{project_name}项目的README文档",
                            mimeType="text/markdown"
                        ))
                    
                    # 模块资源
                    for module_dir in project_dir.iterdir():
                        if module_dir.is_dir() and (module_dir / "metadata.json").exists():
                            module_name = module_dir.name
                            resources.append(types.Resource(
                                uri=f"mcp-docs://module/{language}/{project_name}/{module_name}",
                                name=f"模块: {module_name}",
                                description=f"{project_name}项目中的{module_name}模块",
                                mimeType="application/json"
                            ))
            
            return resources
        
        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> str:
            """读取资源内容"""
            try:
                # 解析URI
                if not uri.startswith("mcp-docs://"):
                    raise ValueError(f"不支持的URI格式: {uri}")
                
                path_parts = uri.replace("mcp-docs://", "").split("/")
                resource_type = path_parts[0]
                
                if resource_type == "project":
                    language, project = path_parts[1], path_parts[2]
                    return await self._read_project_resource(language, project)
                
                elif resource_type == "readme":
                    language, project = path_parts[1], path_parts[2]
                    return await self._read_readme_resource(language, project)
                
                elif resource_type == "module":
                    language, project, module = path_parts[1], path_parts[2], path_parts[3]
                    return await self._read_module_resource(language, project, module)
                
                else:
                    raise ValueError(f"未知资源类型: {resource_type}")
            
            except Exception as e:
                logger.error(f"读取资源失败 {uri}: {e}")
                raise
        
        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            """列出可用工具"""
            tools = [
                types.Tool(
                    name="search_documentation",
                    description="在文档中搜索特定内容",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "搜索查询字符串"
                            },
                            "language": {
                                "type": "string",
                                "description": "限制搜索的编程语言（可选）",
                                "enum": [lang["name"] for lang in self.config.get("supported_languages", [])]
                            },
                            "project": {
                                "type": "string",
                                "description": "限制搜索的项目（可选）"
                            }
                        },
                        "required": ["query"]
                    }
                ),
                types.Tool(
                    name="analyze_project_structure",
                    description="分析项目结构和依赖关系",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "language": {
                                "type": "string",
                                "description": "编程语言",
                                "enum": [lang["name"] for lang in self.config.get("supported_languages", [])]
                            },
                            "project": {
                                "type": "string",
                                "description": "项目名称"
                            }
                        },
                        "required": ["language", "project"]
                    }
                ),
                types.Tool(
                    name="check_documentation_quality",
                    description="检查文档质量和完整性",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "scope": {
                                "type": "string",
                                "description": "检查范围",
                                "enum": ["all", "project", "module"]
                            },
                            "language": {
                                "type": "string",
                                "description": "编程语言（scope为project或module时必需）"
                            },
                            "project": {
                                "type": "string",
                                "description": "项目名称（scope为project或module时必需）"
                            },
                            "module": {
                                "type": "string",
                                "description": "模块名称（scope为module时必需）"
                            }
                        },
                        "required": ["scope"]
                    }
                )
            ]
            
            return tools
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
            """执行工具调用"""
            try:
                if name == "search_documentation":
                    result = await self._search_documentation(**arguments)
                elif name == "analyze_project_structure":
                    result = await self._analyze_project_structure(**arguments)
                elif name == "check_documentation_quality":
                    result = await self._check_documentation_quality(**arguments)
                else:
                    raise ValueError(f"未知工具: {name}")
                
                return [types.TextContent(
                    type="text",
                    text=json.dumps(result, indent=2, ensure_ascii=False)
                )]
            
            except Exception as e:
                logger.error(f"工具调用失败 {name}: {e}")
                return [types.TextContent(
                    type="text",
                    text=f"错误: {str(e)}"
                )]
    
    async def _read_project_resource(self, language: str, project: str) -> str:
        """读取项目资源"""
        project_path = self._get_project_path(language, project)
        if not project_path or not project_path.exists():
            raise FileNotFoundError(f"项目未找到: {language}/{project}")
        
        # 加载项目信息
        project_info = self._load_json_file(project_path / "project-info.json")
        if not project_info:
            raise FileNotFoundError("项目元数据未找到")
        
        # 加载README
        readme_content = ""
        readme_path = project_path / "README.md"
        if readme_path.exists():
            with open(readme_path, 'r', encoding='utf-8') as f:
                readme_content = f.read()
        
        # 获取模块信息
        modules = []
        for module_dir in project_path.iterdir():
            if module_dir.is_dir() and (module_dir / "metadata.json").exists():
                module_metadata = self._load_json_file(module_dir / "metadata.json")
                if module_metadata:
                    modules.append({
                        "name": module_dir.name,
                        "metadata": module_metadata.get("module_metadata", {})
                    })
        
        result = {
            "project_info": project_info,
            "readme": readme_content,
            "modules": modules
        }
        
        return json.dumps(result, indent=2, ensure_ascii=False)
    
    async def _read_readme_resource(self, language: str, project: str) -> str:
        """读取README资源"""
        project_path = self._get_project_path(language, project)
        if not project_path:
            raise FileNotFoundError(f"项目未找到: {language}/{project}")
        
        readme_path = project_path / "README.md"
        if not readme_path.exists():
            raise FileNotFoundError("README.md未找到")
        
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    async def _read_module_resource(self, language: str, project: str, module: str) -> str:
        """读取模块资源"""
        project_path = self._get_project_path(language, project)
        if not project_path:
            raise FileNotFoundError(f"项目未找到: {language}/{project}")
        
        module_path = project_path / module
        if not module_path.exists():
            raise FileNotFoundError(f"模块未找到: {module}")
        
        # 加载模块元数据
        metadata = self._load_json_file(module_path / "metadata.json")
        
        # 加载模块README
        readme_content = ""
        readme_path = module_path / "README.md"
        if readme_path.exists():
            with open(readme_path, 'r', encoding='utf-8') as f:
                readme_content = f.read()
        
        result = {
            "metadata": metadata,
            "readme": readme_content
        }
        
        return json.dumps(result, indent=2, ensure_ascii=False)
    
    async def _search_documentation(self, query: str, language: str = None, project: str = None) -> Dict:
        """搜索文档"""
        results = []
        search_terms = query.lower().split()
        
        # 搜索逻辑（简化版）
        for lang_config in self.config.get("supported_languages", []):
            if language and lang_config["name"] != language:
                continue
                
            lang_dir = self.mcp_root / lang_config["display_name"]
            if not lang_dir.exists():
                continue
            
            for project_dir in lang_dir.iterdir():
                if not project_dir.is_dir():
                    continue
                if project and project_dir.name != project:
                    continue
                
                # 搜索项目文档
                for file_path in project_dir.rglob("*.md"):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read().lower()
                        
                        score = sum(content.count(term) for term in search_terms)
                        if score > 0:
                            results.append({
                                "language": lang_config["name"],
                                "project": project_dir.name,
                                "file": file_path.name,
                                "score": score,
                                "preview": content[:200] + "..."
                            })
                    except Exception:
                        continue
        
        results.sort(key=lambda x: x["score"], reverse=True)
        
        return {
            "query": query,
            "total_results": len(results),
            "results": results[:20]  # 限制结果数量
        }
    
    async def _analyze_project_structure(self, language: str, project: str) -> Dict:
        """分析项目结构"""
        project_path = self._get_project_path(language, project)
        if not project_path or not project_path.exists():
            raise FileNotFoundError(f"项目未找到: {language}/{project}")
        
        # 加载项目信息
        project_info = self._load_json_file(project_path / "project-info.json")
        if not project_info:
            raise FileNotFoundError("项目元数据未找到")
        
        modules = []
        dependencies = set()
        
        for module_dir in project_path.iterdir():
            if module_dir.is_dir() and (module_dir / "metadata.json").exists():
                module_metadata = self._load_json_file(module_dir / "metadata.json")
                if module_metadata:
                    module_info = module_metadata.get("module_metadata", {})
                    modules.append({
                        "name": module_dir.name,
                        "status": module_info.get("status", "unknown"),
                        "description": module_info.get("description", "")
                    })
                    
                    # 收集依赖
                    tech_details = module_metadata.get("technical_details", {})
                    deps = tech_details.get("dependencies", {})
                    if "external" in deps:
                        for dep in deps["external"]:
                            dependencies.add(dep.get("library", "unknown"))
        
        return {
            "project": project,
            "language": language,
            "modules": modules,
            "module_count": len(modules),
            "external_dependencies": list(dependencies),
            "dependency_count": len(dependencies)
        }
    
    async def _check_documentation_quality(self, scope: str, **kwargs) -> Dict:
        """检查文档质量"""
        # 这里可以集成质量检查脚本
        # 为了简化，返回基本信息
        
        issues = []
        total_files = 0
        
        if scope == "all":
            # 检查所有项目
            for lang_config in self.config.get("supported_languages", []):
                lang_dir = self.mcp_root / lang_config["display_name"]
                if lang_dir.exists():
                    for project_dir in lang_dir.iterdir():
                        if project_dir.is_dir():
                            total_files += len(list(project_dir.rglob("*.md")))
                            total_files += len(list(project_dir.rglob("*.json")))
        
        return {
            "scope": scope,
            "total_files_checked": total_files,
            "issues_found": len(issues),
            "issues": issues,
            "quality_score": max(0, 100 - len(issues) * 5)  # 简单评分
        }
    
    def _get_project_path(self, language: str, project: str) -> Optional[Path]:
        """获取项目路径"""
        for lang_config in self.config.get("supported_languages", []):
            if lang_config["name"] == language:
                return self.mcp_root / lang_config["display_name"] / project
        return None
    
    def _load_json_file(self, file_path: Path) -> Optional[Dict]:
        """加载JSON文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load {file_path}: {e}")
            return None
    
    async def run(self):
        """运行MCP服务器"""
        logger.info("Starting MCP Documentation Server")
        logger.info(f"MCP Root: {self.mcp_root}")
        
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="mcp-documentation-server",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )


async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP Documentation Protocol Server")
    parser.add_argument("--mcp-root", default=".", help="MCP root directory")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    # 配置日志
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format='%(levelname)s: %(message)s')
    
    if not MCP_AVAILABLE:
        print("错误: 需要安装官方MCP库")
        print("请运行: pip install mcp")
        return 1
    
    # 启动MCP服务器
    server = MCPDocumentationServer(args.mcp_root)
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
