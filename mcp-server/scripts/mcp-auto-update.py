#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP文档服务器自动化脚本
监控代码变更并自动更新文档
"""

import os
import json
import time
import logging
import hashlib
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set
import argparse

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp-auto-update.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MCPAutoUpdater:
    """MCP文档服务器自动更新器"""
    
    def __init__(self, mcp_root: str):
        self.mcp_root = Path(mcp_root)
        self.config = self._load_config()
        self.languages = self._get_supported_languages()
        self.file_hashes = {}
        
    def _load_config(self) -> Dict:
        """加载MCP配置文件"""
        config_path = self.mcp_root / "mcp-config.json"
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {}
    
    def _get_supported_languages(self) -> List[str]:
        """获取支持的编程语言列表"""
        languages = []
        for lang_config in self.config.get("supported_languages", []):
            languages.append(lang_config["name"])
        return languages
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """计算文件哈希值"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception as e:
            logger.warning(f"Failed to calculate hash for {file_path}: {e}")
            return ""
    
    def scan_for_changes(self) -> Dict[str, Set[str]]:
        """扫描代码变更"""
        changes = {"modified": set(), "added": set(), "deleted": set()}
        
        # 扫描所有语言目录
        for language in self.languages:
            lang_dir = self.mcp_root / language
            if not lang_dir.exists():
                continue
                
            # 扫描项目目录
            for project_dir in lang_dir.iterdir():
                if not project_dir.is_dir():
                    continue
                    
                # 检查项目信息文件
                project_info = project_dir / "project-info.json"
                if project_info.exists():
                    current_hash = self._calculate_file_hash(project_info)
                    old_hash = self.file_hashes.get(str(project_info), "")
                    
                    if not old_hash:
                        changes["added"].add(str(project_dir))
                        logger.info(f"New project detected: {project_dir}")
                    elif current_hash != old_hash:
                        changes["modified"].add(str(project_dir))
                        logger.info(f"Project modified: {project_dir}")
                    
                    self.file_hashes[str(project_info)] = current_hash
                
                # 检查模块变更
                for module_dir in project_dir.iterdir():
                    if not module_dir.is_dir() or module_dir.name.startswith('.'):
                        continue
                    
                    metadata_file = module_dir / "metadata.json"
                    if metadata_file.exists():
                        current_hash = self._calculate_file_hash(metadata_file)
                        old_hash = self.file_hashes.get(str(metadata_file), "")
                        
                        if not old_hash:
                            changes["added"].add(str(module_dir))
                            logger.info(f"New module detected: {module_dir}")
                        elif current_hash != old_hash:
                            changes["modified"].add(str(module_dir))
                            logger.info(f"Module modified: {module_dir}")
                        
                        self.file_hashes[str(metadata_file)] = current_hash
        
        return changes
    
    def update_timestamps(self, paths: Set[str]) -> None:
        """更新文档时间戳"""
        current_time = datetime.now().isoformat() + "Z"
        
        for path in paths:
            path_obj = Path(path)
            
            # 更新项目级时间戳
            if path_obj.name in self.languages or "project-info.json" in path:
                project_info = path_obj / "project-info.json"
                if project_info.exists():
                    try:
                        with open(project_info, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        data["project_metadata"]["last_updated"] = current_time[:10]  # YYYY-MM-DD
                        data["mcp_metadata"]["last_ai_update"] = current_time
                        
                        with open(project_info, 'w', encoding='utf-8') as f:
                            json.dump(data, f, indent=2, ensure_ascii=False)
                        
                        logger.info(f"Updated timestamps in {project_info}")
                    except Exception as e:
                        logger.error(f"Failed to update {project_info}: {e}")
            
            # 更新模块级时间戳
            metadata_file = path_obj / "metadata.json"
            if metadata_file.exists():
                try:
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    data["module_metadata"]["last_updated"] = current_time[:10]
                    data["mcp_metadata"]["last_ai_update"] = current_time
                    
                    with open(metadata_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    
                    logger.info(f"Updated timestamps in {metadata_file}")
                except Exception as e:
                    logger.error(f"Failed to update {metadata_file}: {e}")
    
    def validate_documentation(self) -> List[str]:
        """验证文档格式和完整性"""
        issues = []
        
        for language in self.languages:
            lang_dir = self.mcp_root / language
            if not lang_dir.exists():
                issues.append(f"Language directory missing: {language}")
                continue
            
            for project_dir in lang_dir.iterdir():
                if not project_dir.is_dir():
                    continue
                
                # 检查必需文件
                required_files = ["README.md", "project-info.json"]
                for req_file in required_files:
                    if not (project_dir / req_file).exists():
                        issues.append(f"Missing required file: {project_dir / req_file}")
                
                # 验证project-info.json结构
                project_info = project_dir / "project-info.json"
                if project_info.exists():
                    try:
                        with open(project_info, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        required_keys = ["project_metadata", "mcp_metadata"]
                        for key in required_keys:
                            if key not in data:
                                issues.append(f"Missing key '{key}' in {project_info}")
                                
                    except json.JSONDecodeError as e:
                        issues.append(f"Invalid JSON in {project_info}: {e}")
                
                # 检查模块文档
                for module_dir in project_dir.iterdir():
                    if not module_dir.is_dir() or module_dir.name.startswith('.'):
                        continue
                    
                    module_required = ["README.md", "metadata.json"]
                    for req_file in module_required:
                        if not (module_dir / req_file).exists():
                            issues.append(f"Missing module file: {module_dir / req_file}")
        
        return issues
    
    def generate_dependency_graph(self) -> Dict:
        """生成项目依赖关系图"""
        dependency_graph = {
            "nodes": [],
            "edges": [],
            "generated_at": datetime.now().isoformat()
        }
        
        for language in self.languages:
            lang_dir = self.mcp_root / language
            if not lang_dir.exists():
                continue
            
            for project_dir in lang_dir.iterdir():
                if not project_dir.is_dir():
                    continue
                
                project_info = project_dir / "project-info.json"
                if not project_info.exists():
                    continue
                
                try:
                    with open(project_info, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    project_name = data["project_metadata"]["name"]
                    
                    # 添加项目节点
                    dependency_graph["nodes"].append({
                        "id": project_name,
                        "type": "project",
                        "language": language,
                        "description": data["project_metadata"].get("description", "")
                    })
                    
                    # 添加模块节点和依赖关系
                    for module in data.get("modules", []):
                        module_name = f"{project_name}.{module['name']}"
                        
                        dependency_graph["nodes"].append({
                            "id": module_name,
                            "type": "module",
                            "project": project_name,
                            "status": module.get("status", "unknown"),
                            "description": module.get("description", "")
                        })
                        
                        # 添加模块依赖边
                        for dep in module.get("dependencies", []):
                            dep_name = f"{project_name}.{dep}"
                            dependency_graph["edges"].append({
                                "from": module_name,
                                "to": dep_name,
                                "type": "depends_on"
                            })
                
                except Exception as e:
                    logger.error(f"Failed to process {project_info}: {e}")
        
        return dependency_graph
    
    def run_monitoring_cycle(self) -> None:
        """运行一次监控周期"""
        logger.info("Starting MCP documentation monitoring cycle")
        
        # 1. 扫描变更
        changes = self.scan_for_changes()
        
        if changes["modified"] or changes["added"]:
            logger.info(f"Changes detected: {len(changes['modified'])} modified, {len(changes['added'])} added")
            
            # 2. 更新时间戳
            all_changes = changes["modified"].union(changes["added"])
            self.update_timestamps(all_changes)
            
            # 3. 生成依赖关系图
            dependency_graph = self.generate_dependency_graph()
            graph_file = self.mcp_root / "dependency-graph.json"
            with open(graph_file, 'w', encoding='utf-8') as f:
                json.dump(dependency_graph, f, indent=2, ensure_ascii=False)
            logger.info(f"Updated dependency graph: {graph_file}")
        
        # 4. 验证文档
        issues = self.validate_documentation()
        if issues:
            logger.warning(f"Documentation issues found: {len(issues)}")
            for issue in issues:
                logger.warning(f"  - {issue}")
        else:
            logger.info("All documentation validation checks passed")
        
        logger.info("MCP documentation monitoring cycle completed")
    
    def run_continuous_monitoring(self, interval: int = 300) -> None:
        """持续监控模式"""
        logger.info(f"Starting continuous monitoring with {interval}s interval")
        
        try:
            while True:
                self.run_monitoring_cycle()
                logger.info(f"Sleeping for {interval} seconds...")
                time.sleep(interval)
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        except Exception as e:
            logger.error(f"Monitoring error: {e}")
            raise


def main():
    parser = argparse.ArgumentParser(description="MCP Documentation Auto-Updater")
    parser.add_argument("--mcp-root", default=".", help="MCP root directory")
    parser.add_argument("--interval", type=int, default=300, help="Monitoring interval in seconds")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    parser.add_argument("--validate-only", action="store_true", help="Only validate documentation")
    
    args = parser.parse_args()
    
    updater = MCPAutoUpdater(args.mcp_root)
    
    if args.validate_only:
        issues = updater.validate_documentation()
        if issues:
            print("Documentation issues found:")
            for issue in issues:
                print(f"  - {issue}")
            return 1
        else:
            print("All documentation validation checks passed")
            return 0
    
    if args.once:
        updater.run_monitoring_cycle()
    else:
        updater.run_continuous_monitoring(args.interval)


if __name__ == "__main__":
    main()
