#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP Git Hooks安装脚本
自动安装和配置Git hooks
"""

import os
import shutil
import stat
import logging
from pathlib import Path
import argparse

logger = logging.getLogger(__name__)

class GitHooksInstaller:
    """Git Hooks安装器"""
    
    def __init__(self, mcp_root: str):
        self.mcp_root = Path(mcp_root)
        self.git_hooks_dir = self.mcp_root / ".git" / "hooks"
        self.mcp_hooks_dir = self.mcp_root / "scripts" / "git-hooks"
        
    def check_git_repository(self) -> bool:
        """检查是否为Git仓库"""
        git_dir = self.mcp_root / ".git"
        if not git_dir.exists():
            logger.error(f"Not a git repository: {self.mcp_root}")
            return False
        
        if not self.git_hooks_dir.exists():
            logger.error(f"Git hooks directory not found: {self.git_hooks_dir}")
            return False
        
        return True
    
    def backup_existing_hook(self, hook_name: str) -> bool:
        """备份现有的hook"""
        existing_hook = self.git_hooks_dir / hook_name
        
        if existing_hook.exists():
            backup_path = self.git_hooks_dir / f"{hook_name}.backup"
            counter = 1
            
            # 如果备份文件已存在，使用递增编号
            while backup_path.exists():
                backup_path = self.git_hooks_dir / f"{hook_name}.backup.{counter}"
                counter += 1
            
            try:
                shutil.copy2(existing_hook, backup_path)
                logger.info(f"Backed up existing hook to: {backup_path}")
                return True
            except Exception as e:
                logger.error(f"Failed to backup hook {hook_name}: {e}")
                return False
        
        return True
    
    def install_hook(self, hook_name: str) -> bool:
        """安装单个hook"""
        source_hook = self.mcp_hooks_dir / hook_name
        target_hook = self.git_hooks_dir / hook_name
        
        if not source_hook.exists():
            logger.error(f"Hook source file not found: {source_hook}")
            return False
        
        # 备份现有hook
        if not self.backup_existing_hook(hook_name):
            return False
        
        try:
            # 复制hook文件
            shutil.copy2(source_hook, target_hook)
            
            # 设置可执行权限
            current_permissions = target_hook.stat().st_mode
            target_hook.chmod(current_permissions | stat.S_IEXEC)
            
            logger.info(f"Installed hook: {hook_name}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to install hook {hook_name}: {e}")
            return False
    
    def create_hook_wrapper(self, hook_name: str, python_script: str) -> bool:
        """创建Python脚本的shell包装器"""
        wrapper_content = f'''#!/bin/sh
# MCP Documentation Server Git Hook Wrapper
# Generated automatically - do not modify

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MCP_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# 检查Python环境
if command -v python3 >/dev/null 2>&1; then
    PYTHON=python3
elif command -v python >/dev/null 2>&1; then
    PYTHON=python
else
    echo "Error: Python not found. Please install Python 3."
    exit 1
fi

# 执行Python脚本
exec "$PYTHON" "$MCP_ROOT/scripts/{python_script}" "$@"
'''
        
        target_hook = self.git_hooks_dir / hook_name
        
        try:
            with open(target_hook, 'w', encoding='utf-8') as f:
                f.write(wrapper_content)
            
            # 设置可执行权限
            target_hook.chmod(0o755)
            
            logger.info(f"Created hook wrapper: {hook_name}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to create hook wrapper {hook_name}: {e}")
            return False
    
    def install_all_hooks(self) -> Dict[str, bool]:
        """安装所有hooks"""
        hooks_config = {
            "pre-commit": "pre-commit",  # Shell script
            "post-commit": ("post-commit.py", "wrapper"),  # Python script with wrapper
            "pre-push": ("pre-push.py", "wrapper")  # Python script with wrapper
        }
        
        results = {}
        
        for hook_name, config in hooks_config.items():
            if isinstance(config, str):
                # 直接复制shell脚本
                results[hook_name] = self.install_hook(config)
            else:
                # 创建Python脚本的包装器
                python_script, hook_type = config
                if hook_type == "wrapper":
                    results[hook_name] = self.create_hook_wrapper(hook_name, python_script)
        
        return results
    
    def uninstall_hooks(self) -> Dict[str, bool]:
        """卸载MCP hooks"""
        mcp_hooks = ["pre-commit", "post-commit", "pre-push"]
        results = {}
        
        for hook_name in mcp_hooks:
            hook_file = self.git_hooks_dir / hook_name
            
            if hook_file.exists():
                try:
                    # 检查是否为MCP hook
                    with open(hook_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if "MCP" in content or "MCP文档服务器" in content:
                        hook_file.unlink()
                        logger.info(f"Uninstalled MCP hook: {hook_name}")
                        
                        # 恢复备份
                        backup_file = self.git_hooks_dir / f"{hook_name}.backup"
                        if backup_file.exists():
                            shutil.move(backup_file, hook_file)
                            logger.info(f"Restored backup for: {hook_name}")
                        
                        results[hook_name] = True
                    else:
                        logger.warning(f"Hook {hook_name} does not appear to be an MCP hook, skipping")
                        results[hook_name] = False
                
                except Exception as e:
                    logger.error(f"Failed to uninstall hook {hook_name}: {e}")
                    results[hook_name] = False
            else:
                logger.info(f"Hook {hook_name} not found, nothing to uninstall")
                results[hook_name] = True
        
        return results
    
    def check_hooks_status(self) -> Dict[str, str]:
        """检查hooks状态"""
        mcp_hooks = ["pre-commit", "post-commit", "pre-push"]
        status = {}
        
        for hook_name in mcp_hooks:
            hook_file = self.git_hooks_dir / hook_name
            
            if not hook_file.exists():
                status[hook_name] = "not_installed"
            else:
                try:
                    with open(hook_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if "MCP" in content or "MCP文档服务器" in content:
                        if hook_file.stat().st_mode & stat.S_IEXEC:
                            status[hook_name] = "installed"
                        else:
                            status[hook_name] = "installed_not_executable"
                    else:
                        status[hook_name] = "other_hook_exists"
                
                except Exception as e:
                    status[hook_name] = f"error: {e}"
        
        return status

def main():
    parser = argparse.ArgumentParser(description="MCP Git Hooks Installer")
    parser.add_argument("--mcp-root", default=".", help="MCP root directory")
    parser.add_argument("--action", choices=["install", "uninstall", "status"], 
                       default="install", help="Action to perform")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # 配置日志
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format='%(levelname)s: %(message)s')
    
    # 创建安装器
    installer = GitHooksInstaller(args.mcp_root)
    
    # 检查Git仓库
    if not installer.check_git_repository():
        return 1
    
    if args.action == "status":
        status = installer.check_hooks_status()
        print("MCP Git Hooks Status:")
        for hook_name, hook_status in status.items():
            status_icon = {
                "installed": "✅",
                "not_installed": "❌", 
                "installed_not_executable": "⚠️",
                "other_hook_exists": "🔄"
            }.get(hook_status, "❓")
            
            print(f"  {status_icon} {hook_name}: {hook_status}")
    
    elif args.action == "install":
        print("Installing MCP Git hooks...")
        results = installer.install_all_hooks()
        
        success_count = sum(1 for success in results.values() if success)
        total_count = len(results)
        
        print(f"Installation completed: {success_count}/{total_count} hooks installed")
        
        for hook_name, success in results.items():
            status_icon = "✅" if success else "❌"
            print(f"  {status_icon} {hook_name}")
        
        if success_count == total_count:
            print("\n🎉 All hooks installed successfully!")
            print("MCP documentation will now be automatically updated on commits.")
        else:
            print(f"\n⚠️ {total_count - success_count} hooks failed to install.")
            return 1
    
    elif args.action == "uninstall":
        print("Uninstalling MCP Git hooks...")
        results = installer.uninstall_hooks()
        
        success_count = sum(1 for success in results.values() if success)
        total_count = len(results)
        
        print(f"Uninstallation completed: {success_count}/{total_count} hooks removed")
        
        for hook_name, success in results.items():
            status_icon = "✅" if success else "❌"
            print(f"  {status_icon} {hook_name}")
    
    return 0

if __name__ == "__main__":
    from typing import Dict
    exit(main())
