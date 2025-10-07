#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP文档服务器实现
基于Model Context Protocol提供文档管理服务
"""

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence
from dataclasses import asdict

# MCP相关导入
try:
    from mcp import types
    from mcp.server import Server
    from mcp.server.models import InitializationOptions
    import mcp.server.stdio
    from mcp.types import (
        Resource,
        Tool,
        TextContent,
        ImageContent,
        EmbeddedResource,
    )
except ImportError:
    print("MCP library not found. Please install with: pip install mcp")
    print("For now, we'll create a basic HTTP server implementation.")

import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# 如果没有MCP库，使用FastAPI实现基本的文档服务器
class MCPDocumentServer:
    """MCP文档服务器实现"""
    
    def __init__(self, mcp_root: str):
        self.mcp_root = Path(mcp_root)
        self.app = FastAPI(
            title="MCP Documentation Server",
            description="AI辅助开发文档管理系统",
            version="1.0.0"
        )
        self.setup_routes()
        
        # 加载配置
        try:
            with open(self.mcp_root / "mcp-config.json", 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load config: {e}")
            self.config = {"supported_languages": []}
    
    def setup_routes(self):
        """设置API路由"""
        
        @self.app.get("/")
        async def root():
            return {
                "name": "MCP Documentation Server",
                "version": "1.0.0",
                "description": "AI辅助开发文档管理系统",
                "endpoints": [
                    "/languages",
                    "/projects",
                    "/projects/{language}",
                    "/projects/{language}/{project}",
                    "/modules/{language}/{project}",
                    "/search",
                    "/health"
                ]
            }
        
        @self.app.get("/health")
        async def health_check():
            return {
                "status": "healthy",
                "mcp_root": str(self.mcp_root),
                "languages": len(self.config.get("supported_languages", [])),
                "timestamp": self._get_timestamp()
            }
        
        @self.app.get("/languages")
        async def get_languages():
            """获取支持的编程语言"""
            return {
                "languages": self.config.get("supported_languages", []),
                "total": len(self.config.get("supported_languages", []))
            }
        
        @self.app.get("/projects")
        async def get_all_projects():
            """获取所有项目列表"""
            projects = []
            
            for lang_config in self.config.get("supported_languages", []):
                lang_dir = self.mcp_root / lang_config["display_name"]
                if lang_dir.exists():
                    for project_dir in lang_dir.iterdir():
                        if project_dir.is_dir():
                            project_info = self._load_project_info(project_dir)
                            if project_info:
                                projects.append({
                                    "language": lang_config["name"],
                                    "language_display": lang_config["display_name"],
                                    "name": project_dir.name,
                                    "path": str(project_dir.relative_to(self.mcp_root)),
                                    **project_info.get("project_metadata", {})
                                })
            
            return {"projects": projects, "total": len(projects)}
        
        @self.app.get("/projects/{language}")
        async def get_projects_by_language(language: str):
            """获取特定语言的项目"""
            # 查找语言配置
            lang_config = None
            for lang in self.config.get("supported_languages", []):
                if lang["name"] == language:
                    lang_config = lang
                    break
            
            if not lang_config:
                raise HTTPException(status_code=404, detail=f"Language '{language}' not supported")
            
            lang_dir = self.mcp_root / lang_config["display_name"]
            if not lang_dir.exists():
                return {"projects": [], "total": 0}
            
            projects = []
            for project_dir in lang_dir.iterdir():
                if project_dir.is_dir():
                    project_info = self._load_project_info(project_dir)
                    if project_info:
                        projects.append({
                            "name": project_dir.name,
                            "path": str(project_dir.relative_to(self.mcp_root)),
                            **project_info.get("project_metadata", {})
                        })
            
            return {"language": language, "projects": projects, "total": len(projects)}
        
        @self.app.get("/projects/{language}/{project}")
        async def get_project_details(language: str, project: str):
            """获取项目详细信息"""
            project_path = self._get_project_path(language, project)
            if not project_path or not project_path.exists():
                raise HTTPException(status_code=404, detail="Project not found")
            
            # 加载项目信息
            project_info = self._load_project_info(project_path)
            if not project_info:
                raise HTTPException(status_code=404, detail="Project metadata not found")
            
            # 加载README
            readme_path = project_path / "README.md"
            readme_content = ""
            if readme_path.exists():
                with open(readme_path, 'r', encoding='utf-8') as f:
                    readme_content = f.read()
            
            # 获取模块列表
            modules = []
            for module_dir in project_path.iterdir():
                if module_dir.is_dir() and (module_dir / "metadata.json").exists():
                    module_metadata = self._load_json_file(module_dir / "metadata.json")
                    if module_metadata:
                        modules.append({
                            "name": module_dir.name,
                            "path": str(module_dir.relative_to(self.mcp_root)),
                            **module_metadata.get("module_metadata", {})
                        })
            
            return {
                "project_info": project_info,
                "readme": readme_content,
                "modules": modules,
                "module_count": len(modules)
            }
        
        @self.app.get("/modules/{language}/{project}")
        async def get_project_modules(language: str, project: str):
            """获取项目的所有模块"""
            project_path = self._get_project_path(language, project)
            if not project_path or not project_path.exists():
                raise HTTPException(status_code=404, detail="Project not found")
            
            modules = []
            for module_dir in project_path.iterdir():
                if module_dir.is_dir():
                    metadata_file = module_dir / "metadata.json"
                    readme_file = module_dir / "README.md"
                    
                    if metadata_file.exists():
                        metadata = self._load_json_file(metadata_file)
                        readme_content = ""
                        
                        if readme_file.exists():
                            with open(readme_file, 'r', encoding='utf-8') as f:
                                readme_content = f.read()[:500] + "..." if len(f.read()) > 500 else f.read()
                        
                        modules.append({
                            "name": module_dir.name,
                            "path": str(module_dir.relative_to(self.mcp_root)),
                            "metadata": metadata,
                            "readme_preview": readme_content
                        })
            
            return {
                "language": language,
                "project": project,
                "modules": modules,
                "total": len(modules)
            }
        
        @self.app.get("/search")
        async def search_documentation(
            q: str = Query(..., description="搜索查询"),
            language: Optional[str] = Query(None, description="限制搜索的语言"),
            project: Optional[str] = Query(None, description="限制搜索的项目")
        ):
            """搜索文档内容"""
            results = []
            search_terms = q.lower().split()
            
            # 遍历所有项目进行搜索
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
                    results.extend(self._search_in_directory(
                        project_dir, search_terms, lang_config["name"], project_dir.name
                    ))
            
            # 按相关性排序
            results.sort(key=lambda x: x["score"], reverse=True)
            
            return {
                "query": q,
                "results": results[:50],  # 限制返回结果数量
                "total": len(results)
            }
    
    def _get_timestamp(self):
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _get_project_path(self, language: str, project: str) -> Optional[Path]:
        """获取项目路径"""
        # 查找语言配置
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
    
    def _load_project_info(self, project_dir: Path) -> Optional[Dict]:
        """加载项目信息"""
        project_info_file = project_dir / "project-info.json"
        return self._load_json_file(project_info_file)
    
    def _search_in_directory(self, directory: Path, search_terms: List[str], 
                           language: str, project: str) -> List[Dict]:
        """在目录中搜索"""
        results = []
        
        # 搜索文档文件
        for file_path in directory.rglob("*.md"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                
                # 计算相关性分数
                score = 0
                for term in search_terms:
                    score += content.count(term)
                
                if score > 0:
                    results.append({
                        "type": "markdown",
                        "language": language,
                        "project": project,
                        "file": file_path.name,
                        "path": str(file_path.relative_to(self.mcp_root)),
                        "score": score,
                        "preview": self._get_content_preview(file_path, search_terms[0])
                    })
            
            except Exception as e:
                logger.warning(f"Failed to search in {file_path}: {e}")
        
        # 搜索JSON元数据
        for file_path in directory.rglob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                
                score = 0
                for term in search_terms:
                    score += content.count(term)
                
                if score > 0:
                    results.append({
                        "type": "metadata",
                        "language": language,
                        "project": project,
                        "file": file_path.name,
                        "path": str(file_path.relative_to(self.mcp_root)),
                        "score": score,
                        "preview": "元数据文件匹配"
                    })
            
            except Exception as e:
                logger.warning(f"Failed to search in {file_path}: {e}")
        
        return results
    
    def _get_content_preview(self, file_path: Path, search_term: str, context_size: int = 100) -> str:
        """获取内容预览"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 查找搜索词的位置
            lower_content = content.lower()
            pos = lower_content.find(search_term.lower())
            
            if pos == -1:
                return content[:200] + "..." if len(content) > 200 else content
            
            # 提取上下文
            start = max(0, pos - context_size)
            end = min(len(content), pos + len(search_term) + context_size)
            preview = content[start:end]
            
            if start > 0:
                preview = "..." + preview
            if end < len(content):
                preview = preview + "..."
            
            return preview
            
        except Exception:
            return "无法生成预览"
    
    def run(self, host: str = "127.0.0.1", port: int = 8000):
        """运行服务器"""
        logger.info(f"Starting MCP Documentation Server at http://{host}:{port}")
        logger.info(f"MCP Root: {self.mcp_root}")
        logger.info(f"Supported languages: {len(self.config.get('supported_languages', []))}")
        
        uvicorn.run(self.app, host=host, port=port, log_level="info")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP Documentation Server")
    parser.add_argument("--mcp-root", default=".", help="MCP root directory")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    # 配置日志
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format='%(levelname)s: %(message)s')
    
    # 启动服务器
    server = MCPDocumentServer(args.mcp_root)
    server.run(args.host, args.port)


if __name__ == "__main__":
    main()
