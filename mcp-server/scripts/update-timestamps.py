#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP文档时间戳更新工具
基于Git变更自动更新文档时间戳
"""

import os
import json
import subprocess
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set
import argparse

logger = logging.getLogger(__name__)

class TimestampUpdater:
    """时间戳更新器"""
    
    def __init__(self, mcp_root: str):
        self.mcp_root = Path(mcp_root)
        self.current_time = datetime.now()
        
    def get_git_changed_files(self, staged_only: bool = False) -> Set[str]:
        """获取Git变更的文件"""
        try:
            if staged_only:
                # 只获取暂存区的文件
                cmd = ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"]
            else:
                # 获取所有变更的文件
                cmd = ["git", "diff", "HEAD~1", "--name-only", "--diff-filter=ACM"]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            files = set()
            
            for line in result.stdout.strip().split('\n'):
                if line:
                    files.add(line)
            
            return files
        
        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to get git changes: {e}")
            return set()
    
    def get_commit_info(self) -> Dict[str, str]:
        """获取提交信息"""
        try:
            # 获取最新提交信息
            cmd = ["git", "log", "-1", "--format=%H|%an|%ae|%ai|%s"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            if result.stdout.strip():
                parts = result.stdout.strip().split('|')
                return {
                    "commit_hash": parts[0][:8],  # 短hash
                    "author_name": parts[1],
                    "author_email": parts[2],
                    "commit_date": parts[3],
                    "commit_message": parts[4]
                }
        except subprocess.CalledProcessError:
            logger.warning("Failed to get commit info")
        
        return {
            "commit_hash": "unknown",
            "author_name": "unknown", 
            "author_email": "unknown",
            "commit_date": self.current_time.isoformat(),
            "commit_message": "unknown"
        }
    
    def should_update_file(self, file_path: Path, changed_files: Set[str]) -> bool:
        """判断是否需要更新文件时间戳"""
        file_str = str(file_path.relative_to(self.mcp_root))
        
        # 直接修改的文件需要更新
        if file_str in changed_files:
            return True
        
        # 检查是否为项目级元数据文件，且项目目录下有文件修改
        if file_path.name == "project-info.json":
            project_dir = file_path.parent
            for changed_file in changed_files:
                if changed_file.startswith(str(project_dir.relative_to(self.mcp_root))):
                    return True
        
        # 检查是否为模块级元数据文件，且模块目录下有文件修改
        if file_path.name == "metadata.json":
            module_dir = file_path.parent
            for changed_file in changed_files:
                if changed_file.startswith(str(module_dir.relative_to(self.mcp_root))):
                    return True
        
        return False
    
    def update_project_metadata(self, file_path: Path, commit_info: Dict[str, str]) -> bool:
        """更新项目元数据时间戳"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 更新时间戳
            if "project_metadata" in data:
                data["project_metadata"]["last_updated"] = self.current_time.strftime("%Y-%m-%d")
            
            if "mcp_metadata" in data:
                data["mcp_metadata"]["last_ai_update"] = self.current_time.isoformat() + "Z"
                data["mcp_metadata"]["last_commit"] = commit_info["commit_hash"]
                data["mcp_metadata"]["last_author"] = commit_info["author_name"]
            
            # 保存文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Updated project metadata: {file_path}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to update project metadata {file_path}: {e}")
            return False
    
    def update_module_metadata(self, file_path: Path, commit_info: Dict[str, str]) -> bool:
        """更新模块元数据时间戳"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 更新时间戳
            if "module_metadata" in data:
                data["module_metadata"]["last_updated"] = self.current_time.strftime("%Y-%m-%d")
            
            if "mcp_metadata" in data:
                data["mcp_metadata"]["last_ai_update"] = self.current_time.isoformat() + "Z"
                data["mcp_metadata"]["last_commit"] = commit_info["commit_hash"]
                data["mcp_metadata"]["last_author"] = commit_info["author_name"]
            
            # 保存文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Updated module metadata: {file_path}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to update module metadata {file_path}: {e}")
            return False
    
    def update_readme_timestamp(self, file_path: Path) -> bool:
        """更新README文件中的时间戳"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 查找并替换时间戳行
            import re
            timestamp_pattern = r'\*此文档由MCP文档服务器.*最后更新时间: [^*]*\*'
            new_timestamp = f"*此文档由MCP文档服务器自动维护，最后更新时间: {self.current_time.strftime('%Y-%m-%d')}*"
            
            if re.search(timestamp_pattern, content):
                content = re.sub(timestamp_pattern, new_timestamp, content)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                logger.info(f"Updated README timestamp: {file_path}")
                return True
        
        except Exception as e:
            logger.error(f"Failed to update README timestamp {file_path}: {e}")
        
        return False
    
    def run_update(self, git_staged: bool = False, files: List[str] = None) -> Dict[str, int]:
        """运行时间戳更新"""
        logger.info("Starting timestamp update...")
        
        # 获取变更文件
        if files:
            changed_files = set(files)
        else:
            changed_files = self.get_git_changed_files(git_staged)
        
        if not changed_files:
            logger.info("No changed files found")
            return {"updated": 0, "errors": 0}
        
        logger.info(f"Found {len(changed_files)} changed files")
        
        # 获取提交信息
        commit_info = self.get_commit_info()
        
        updated_count = 0
        error_count = 0
        
        # 更新项目级元数据
        for project_file in self.mcp_root.rglob("project-info.json"):
            if self.should_update_file(project_file, changed_files):
                if self.update_project_metadata(project_file, commit_info):
                    updated_count += 1
                else:
                    error_count += 1
        
        # 更新模块级元数据
        for module_file in self.mcp_root.rglob("metadata.json"):
            if self.should_update_file(module_file, changed_files):
                if self.update_module_metadata(module_file, commit_info):
                    updated_count += 1
                else:
                    error_count += 1
        
        # 更新README文件时间戳
        for readme_file in self.mcp_root.rglob("README.md"):
            if self.should_update_file(readme_file, changed_files):
                if self.update_readme_timestamp(readme_file):
                    updated_count += 1
                else:
                    error_count += 1
        
        logger.info(f"Timestamp update completed: {updated_count} updated, {error_count} errors")
        
        return {"updated": updated_count, "errors": error_count}
    
    def generate_changelog_entry(self, commit_info: Dict[str, str], changed_files: Set[str]) -> Dict[str, str]:
        """生成变更日志条目"""
        # 分析变更类型
        change_types = set()
        
        for file in changed_files:
            if file.endswith('.md'):
                change_types.add('documentation')
            elif file.endswith('.json'):
                change_types.add('metadata')
            elif any(file.endswith(ext) for ext in ['.java', '.gd', '.py', '.js']):
                change_types.add('code')
            else:
                change_types.add('other')
        
        # 生成变更描述
        if 'code' in change_types:
            change_desc = 'Code and documentation updates'
        elif 'documentation' in change_types and 'metadata' in change_types:
            change_desc = 'Documentation and metadata updates'
        elif 'documentation' in change_types:
            change_desc = 'Documentation updates'
        elif 'metadata' in change_types:
            change_desc = 'Metadata updates'
        else:
            change_desc = 'Project updates'
        
        return {
            "date": commit_info["commit_date"][:10],  # YYYY-MM-DD
            "version": "auto-generated",
            "type": "update",
            "description": change_desc,
            "commit": commit_info["commit_hash"],
            "author": commit_info["author_name"],
            "files_changed": len(changed_files)
        }

def main():
    parser = argparse.ArgumentParser(description="MCP Documentation Timestamp Updater")
    parser.add_argument("--mcp-root", default=".", help="MCP root directory")
    parser.add_argument("--git-staged", action="store_true", help="Only update staged files")
    parser.add_argument("--files", nargs="*", help="Specific files to check")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # 配置日志
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format='%(levelname)s: %(message)s')
    
    # 创建更新器
    updater = TimestampUpdater(args.mcp_root)
    
    # 运行更新
    result = updater.run_update(args.git_staged, args.files)
    
    # 输出结果
    if result["updated"] > 0:
        print(f"✅ Updated {result['updated']} files")
    
    if result["errors"] > 0:
        print(f"❌ {result['errors']} errors occurred")
        return 1
    
    if result["updated"] == 0 and result["errors"] == 0:
        print("ℹ️ No files needed updating")
    
    return 0

if __name__ == "__main__":
    exit(main())
