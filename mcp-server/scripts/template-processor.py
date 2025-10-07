#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP模板处理器
自动替换模板中的占位符变量并从代码中提取信息
"""

import os
import re
import json
import ast
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import argparse

logger = logging.getLogger(__name__)

class CodeAnalyzer:
    """代码分析器，用于从源代码中提取信息"""
    
    def __init__(self, language: str):
        self.language = language.lower()
    
    def analyze_java_file(self, file_path: Path) -> Dict[str, Any]:
        """分析Java文件"""
        info = {
            "classes": [],
            "methods": [],
            "imports": [],
            "package": ""
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取包名
            package_match = re.search(r'package\s+([^;]+);', content)
            if package_match:
                info["package"] = package_match.group(1).strip()
            
            # 提取导入
            import_matches = re.findall(r'import\s+([^;]+);', content)
            info["imports"] = [imp.strip() for imp in import_matches]
            
            # 提取类定义
            class_pattern = r'(?:public\s+)?(?:abstract\s+)?class\s+(\w+)(?:\s+extends\s+\w+)?(?:\s+implements\s+[\w,\s]+)?'
            class_matches = re.finditer(class_pattern, content)
            for match in class_matches:
                class_name = match.group(1)
                info["classes"].append({
                    "name": class_name,
                    "type": "class"
                })
            
            # 提取方法定义（简化版）
            method_pattern = r'(?:public|private|protected)\s+(?:static\s+)?(?:\w+\s+)*(\w+)\s*\([^)]*\)'
            method_matches = re.finditer(method_pattern, content)
            for match in method_matches:
                method_name = match.group(1)
                if method_name not in ['class', 'interface', 'enum']:  # 排除关键字
                    info["methods"].append({
                        "name": method_name
                    })
        
        except Exception as e:
            logger.warning(f"Failed to analyze Java file {file_path}: {e}")
        
        return info
    
    def analyze_gdscript_file(self, file_path: Path) -> Dict[str, Any]:
        """分析GDScript文件"""
        info = {
            "classes": [],
            "functions": [],
            "signals": [],
            "exports": [],
            "extends": ""
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line in lines:
                line = line.strip()
                
                # 提取继承关系
                if line.startswith('extends '):
                    info["extends"] = line.replace('extends ', '').strip()
                
                # 提取类名
                if line.startswith('class_name '):
                    class_name = line.replace('class_name ', '').strip()
                    info["classes"].append({
                        "name": class_name,
                        "type": "class"
                    })
                
                # 提取函数
                if line.startswith('func '):
                    func_match = re.match(r'func\s+(\w+)', line)
                    if func_match:
                        info["functions"].append({
                            "name": func_match.group(1)
                        })
                
                # 提取信号
                if line.startswith('signal '):
                    signal_match = re.match(r'signal\s+(\w+)', line)
                    if signal_match:
                        info["signals"].append({
                            "name": signal_match.group(1)
                        })
                
                # 提取导出变量
                if line.startswith('@export') or line.startswith('export'):
                    # 查找下一行的变量定义
                    var_match = re.search(r'var\s+(\w+)', line)
                    if var_match:
                        info["exports"].append({
                            "name": var_match.group(1)
                        })
        
        except Exception as e:
            logger.warning(f"Failed to analyze GDScript file {file_path}: {e}")
        
        return info
    
    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """根据语言分析文件"""
        if self.language == "java" and file_path.suffix == ".java":
            return self.analyze_java_file(file_path)
        elif self.language == "gdscript" and file_path.suffix == ".gd":
            return self.analyze_gdscript_file(file_path)
        else:
            return {}

class TemplateProcessor:
    """模板处理器"""
    
    def __init__(self, mcp_root: str):
        self.mcp_root = Path(mcp_root)
        self.templates_dir = self.mcp_root / "templates"
        
    def load_template(self, template_name: str) -> str:
        """加载模板文件"""
        template_path = self.templates_dir / template_name
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")
        
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def extract_project_info(self, project_path: Path, language: str) -> Dict[str, Any]:
        """从项目代码中提取信息"""
        analyzer = CodeAnalyzer(language)
        project_info = {
            "name": project_path.name,
            "language": language,
            "classes": [],
            "functions": [],
            "files": [],
            "dependencies": set(),
            "created_date": datetime.now().strftime("%Y-%m-%d"),
            "last_updated": datetime.now().strftime("%Y-%m-%d")
        }
        
        # 扫描项目文件
        extensions = {
            "java": [".java"],
            "gdscript": [".gd"]
        }
        
        target_extensions = extensions.get(language, [])
        
        for ext in target_extensions:
            for file_path in project_path.rglob(f"*{ext}"):
                file_info = analyzer.analyze_file(file_path)
                project_info["files"].append(str(file_path.relative_to(project_path)))
                
                # 聚合类和方法信息
                project_info["classes"].extend(file_info.get("classes", []))
                if language == "java":
                    project_info["functions"].extend(file_info.get("methods", []))
                    project_info["dependencies"].update(file_info.get("imports", []))
                elif language == "gdscript":
                    project_info["functions"].extend(file_info.get("functions", []))
        
        # 转换dependencies为列表
        project_info["dependencies"] = list(project_info["dependencies"])
        
        return project_info
    
    def create_variable_context(self, project_info: Dict[str, Any], module_info: Dict[str, Any] = None) -> Dict[str, str]:
        """创建模板变量上下文"""
        context = {
            # 项目级变量
            "project_name": project_info.get("name", ""),
            "language": project_info.get("language", ""),
            "created_date": project_info.get("created_date", ""),
            "last_updated": project_info.get("last_updated", ""),
            "timestamp": datetime.now().isoformat() + "Z",
            
            # 技术栈信息
            "framework": self._guess_framework(project_info),
            "database": self._guess_database(project_info),
            "dependencies": ", ".join(project_info.get("dependencies", [])[:3]),  # 前3个依赖
            
            # 统计信息
            "class_count": str(len(project_info.get("classes", []))),
            "function_count": str(len(project_info.get("functions", []))),
            "file_count": str(len(project_info.get("files", [])))
        }
        
        # 模块级变量
        if module_info:
            context.update({
                "module_name": module_info.get("name", ""),
                "module_description": module_info.get("description", ""),
                "module_version": module_info.get("version", "1.0.0")
            })
        
        return context
    
    def _guess_framework(self, project_info: Dict[str, Any]) -> str:
        """猜测使用的框架"""
        dependencies = project_info.get("dependencies", [])
        
        if any("spring" in dep.lower() for dep in dependencies):
            return "Spring Boot"
        elif any("godot" in dep.lower() for dep in dependencies):
            return "Godot Engine"
        elif project_info.get("language") == "java":
            return "Java Standard"
        elif project_info.get("language") == "gdscript":
            return "Godot Engine"
        else:
            return "Unknown"
    
    def _guess_database(self, project_info: Dict[str, Any]) -> str:
        """猜测使用的数据库"""
        dependencies = project_info.get("dependencies", [])
        
        if any("mysql" in dep.lower() for dep in dependencies):
            return "MySQL"
        elif any("postgresql" in dep.lower() for dep in dependencies):
            return "PostgreSQL"
        elif any("sqlite" in dep.lower() for dep in dependencies):
            return "SQLite"
        elif any("h2" in dep.lower() for dep in dependencies):
            return "H2"
        else:
            return "Not specified"
    
    def replace_variables(self, template: str, context: Dict[str, str]) -> str:
        """替换模板中的变量"""
        result = template
        
        # 替换 {variable} 格式的变量
        for key, value in context.items():
            placeholder = f"{{{key}}}"
            result = result.replace(placeholder, str(value))
        
        return result
    
    def process_project_template(self, project_path: Path, language: str, output_path: Path = None) -> str:
        """处理项目模板"""
        if output_path is None:
            output_path = project_path / "README.md"
        
        # 提取项目信息
        project_info = self.extract_project_info(project_path, language)
        
        # 加载模板
        template = self.load_template("project-template.md")
        
        # 创建变量上下文
        context = self.create_variable_context(project_info)
        
        # 替换变量
        result = self.replace_variables(template, context)
        
        # 保存结果
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result)
        
        logger.info(f"Generated project documentation: {output_path}")
        return result
    
    def process_module_template(self, module_path: Path, language: str, output_path: Path = None) -> str:
        """处理模块模板"""
        if output_path is None:
            output_path = module_path / "README.md"
        
        # 提取模块信息
        module_info = {
            "name": module_path.name,
            "description": f"{module_path.name} module",
            "version": "1.0.0"
        }
        
        # 提取父项目信息
        project_path = module_path.parent
        project_info = self.extract_project_info(project_path, language)
        
        # 加载模板
        template = self.load_template("module-template.md")
        
        # 创建变量上下文
        context = self.create_variable_context(project_info, module_info)
        
        # 替换变量
        result = self.replace_variables(template, context)
        
        # 保存结果
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result)
        
        logger.info(f"Generated module documentation: {output_path}")
        return result
    
    def process_metadata_template(self, target_path: Path, template_type: str, **kwargs) -> Dict:
        """处理元数据模板"""
        template_name = f"{template_type}.json" if template_type in ["metadata", "project-info"] else f"{template_type}-template.json"
        
        # 加载模板
        template_path = self.templates_dir / template_name
        with open(template_path, 'r', encoding='utf-8') as f:
            template_data = json.load(f)
        
        # 创建上下文
        context = {
            "timestamp": datetime.now().isoformat() + "Z",
            "date": datetime.now().strftime("%Y-%m-%d"),
            **kwargs
        }
        
        # 递归替换模板中的变量
        def replace_in_dict(obj):
            if isinstance(obj, dict):
                return {k: replace_in_dict(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [replace_in_dict(item) for item in obj]
            elif isinstance(obj, str):
                result = obj
                for key, value in context.items():
                    placeholder = f"{{{key}}}"
                    result = result.replace(placeholder, str(value))
                return result
            else:
                return obj
        
        result = replace_in_dict(template_data)
        
        # 保存结果
        output_path = target_path / template_name.replace("-template", "")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Generated metadata: {output_path}")
        return result

def main():
    parser = argparse.ArgumentParser(description="MCP Template Processor")
    parser.add_argument("--mcp-root", default=".", help="MCP root directory")
    parser.add_argument("--project-path", required=True, help="Project path to process")
    parser.add_argument("--language", required=True, choices=["java", "gdscript"], help="Programming language")
    parser.add_argument("--template-type", choices=["project", "module", "metadata"], default="project", help="Template type to process")
    parser.add_argument("--output", help="Output file path")
    
    args = parser.parse_args()
    
    processor = TemplateProcessor(args.mcp_root)
    project_path = Path(args.project_path)
    
    if args.template_type == "project":
        output_path = Path(args.output) if args.output else None
        processor.process_project_template(project_path, args.language, output_path)
    elif args.template_type == "module":
        output_path = Path(args.output) if args.output else None
        processor.process_module_template(project_path, args.language, output_path)
    elif args.template_type == "metadata":
        processor.process_metadata_template(project_path, "project-info", 
                                          project_name=project_path.name,
                                          language=args.language)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
