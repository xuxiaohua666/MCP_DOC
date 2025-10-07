#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP文档质量检查器
检查链接有效性、代码示例验证、元数据完整性等
"""

import os
import re
import json
import requests
import subprocess
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import argparse
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class QualityIssue:
    """质量问题类"""
    
    def __init__(self, file_path: str, issue_type: str, description: str, line_number: int = None):
        self.file_path = file_path
        self.issue_type = issue_type
        self.description = description
        self.line_number = line_number
        self.timestamp = datetime.now()
    
    def __str__(self):
        line_info = f" (line {self.line_number})" if self.line_number else ""
        return f"[{self.issue_type}] {self.file_path}{line_info}: {self.description}"

class LinkChecker:
    """链接检查器"""
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MCP Documentation Quality Checker/1.0'
        })
    
    def check_url(self, url: str) -> Tuple[bool, str]:
        """检查URL是否有效"""
        try:
            # 跳过本地文件链接
            if url.startswith('#') or url.startswith('./') or url.startswith('../'):
                return True, "Local link"
            
            # 跳过mailto链接
            if url.startswith('mailto:'):
                return True, "Email link"
            
            response = self.session.head(url, timeout=self.timeout, allow_redirects=True)
            if response.status_code < 400:
                return True, f"OK ({response.status_code})"
            else:
                return False, f"HTTP {response.status_code}"
        
        except requests.exceptions.RequestException as e:
            return False, str(e)
    
    def find_links_in_markdown(self, content: str) -> List[Tuple[str, int]]:
        """在Markdown内容中查找链接"""
        links = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # 查找Markdown链接格式 [text](url)
            markdown_links = re.findall(r'\[([^\]]*)\]\(([^)]+)\)', line)
            for text, url in markdown_links:
                links.append((url, line_num))
            
            # 查找直接的HTTP链接
            http_links = re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', line)
            for url in http_links:
                links.append((url, line_num))
        
        return links

class CodeValidator:
    """代码示例验证器"""
    
    def __init__(self):
        self.supported_languages = {
            'java': self._validate_java_code,
            'gdscript': self._validate_gdscript_code,
            'python': self._validate_python_code,
            'javascript': self._validate_javascript_code,
            'json': self._validate_json_code
        }
    
    def find_code_blocks(self, content: str) -> List[Tuple[str, str, int]]:
        """查找代码块"""
        code_blocks = []
        lines = content.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith('```'):
                # 提取语言标识
                language = line[3:].strip().split()[0].lower() if len(line) > 3 else ''
                start_line = i + 1
                i += 1
                code_lines = []
                
                # 查找结束标记
                while i < len(lines) and not lines[i].strip().startswith('```'):
                    code_lines.append(lines[i])
                    i += 1
                
                if i < len(lines):  # 找到结束标记
                    code = '\n'.join(code_lines)
                    code_blocks.append((language, code, start_line))
            
            i += 1
        
        return code_blocks
    
    def _validate_java_code(self, code: str) -> List[str]:
        """验证Java代码"""
        issues = []
        
        # 基本语法检查
        if not re.search(r'class\s+\w+|interface\s+\w+|enum\s+\w+', code):
            if '{' in code and '}' in code:
                issues.append("代码块缺少类声明")
        
        # 检查括号匹配
        if code.count('{') != code.count('}'):
            issues.append("大括号不匹配")
        
        if code.count('(') != code.count(')'):
            issues.append("圆括号不匹配")
        
        # 检查常见语法错误
        if re.search(r';\s*\n\s*}', code):
            issues.append("可能存在多余的分号")
        
        return issues
    
    def _validate_gdscript_code(self, code: str) -> List[str]:
        """验证GDScript代码"""
        issues = []
        lines = code.split('\n')
        
        # 检查缩进一致性
        indent_levels = []
        for line in lines:
            if line.strip():
                indent = len(line) - len(line.lstrip())
                if indent > 0:
                    indent_levels.append(indent)
        
        if indent_levels and len(set(indent_levels)) > 1:
            # 检查是否使用一致的缩进
            if not all(level % 4 == 0 or level % 2 == 0 for level in indent_levels):
                issues.append("缩进不一致")
        
        # 检查函数定义格式
        for line in lines:
            if line.strip().startswith('func '):
                if not re.match(r'^\s*func\s+\w+\([^)]*\)\s*(?:->\s*\w+)?\s*:', line.strip()):
                    issues.append(f"函数定义格式错误: {line.strip()}")
        
        return issues
    
    def _validate_python_code(self, code: str) -> List[str]:
        """验证Python代码"""
        issues = []
        
        try:
            ast.parse(code)
        except SyntaxError as e:
            issues.append(f"Python语法错误: {e}")
        
        return issues
    
    def _validate_javascript_code(self, code: str) -> List[str]:
        """验证JavaScript代码"""
        issues = []
        
        # 检查括号匹配
        if code.count('{') != code.count('}'):
            issues.append("大括号不匹配")
        
        if code.count('(') != code.count(')'):
            issues.append("圆括号不匹配")
        
        if code.count('[') != code.count(']'):
            issues.append("方括号不匹配")
        
        return issues
    
    def _validate_json_code(self, code: str) -> List[str]:
        """验证JSON代码"""
        issues = []
        
        try:
            json.loads(code)
        except json.JSONDecodeError as e:
            issues.append(f"JSON格式错误: {e}")
        
        return issues
    
    def validate_code_block(self, language: str, code: str) -> List[str]:
        """验证代码块"""
        if language in self.supported_languages:
            return self.supported_languages[language](code)
        else:
            return []  # 不支持的语言跳过验证

class MetadataValidator:
    """元数据验证器"""
    
    def __init__(self):
        self.required_project_fields = {
            "project_metadata": ["name", "version", "language", "description"],
            "mcp_metadata": ["generated_by", "schema_version"]
        }
        
        self.required_module_fields = {
            "module_metadata": ["name", "description", "status"],
            "mcp_metadata": ["generated_by", "schema_version"]
        }
    
    def validate_project_metadata(self, metadata: Dict) -> List[str]:
        """验证项目元数据"""
        issues = []
        
        for section, fields in self.required_project_fields.items():
            if section not in metadata:
                issues.append(f"缺少必需的节: {section}")
                continue
            
            section_data = metadata[section]
            for field in fields:
                if field not in section_data:
                    issues.append(f"缺少必需的字段: {section}.{field}")
                elif not section_data[field]:
                    issues.append(f"字段不能为空: {section}.{field}")
        
        # 验证版本格式
        if "project_metadata" in metadata and "version" in metadata["project_metadata"]:
            version = metadata["project_metadata"]["version"]
            if not re.match(r'^\d+\.\d+\.\d+', version):
                issues.append(f"版本格式错误: {version}")
        
        return issues
    
    def validate_module_metadata(self, metadata: Dict) -> List[str]:
        """验证模块元数据"""
        issues = []
        
        for section, fields in self.required_module_fields.items():
            if section not in metadata:
                issues.append(f"缺少必需的节: {section}")
                continue
            
            section_data = metadata[section]
            for field in fields:
                if field not in section_data:
                    issues.append(f"缺少必需的字段: {section}.{field}")
                elif not section_data[field]:
                    issues.append(f"字段不能为空: {section}.{field}")
        
        # 验证状态值
        if ("module_metadata" in metadata and 
            "status" in metadata["module_metadata"]):
            status = metadata["module_metadata"]["status"]
            valid_statuses = ["active", "deprecated", "planned", "under_development"]
            if status not in valid_statuses:
                issues.append(f"无效的状态值: {status}")
        
        return issues

class DocumentationQualityChecker:
    """文档质量检查器主类"""
    
    def __init__(self, mcp_root: str):
        self.mcp_root = Path(mcp_root)
        self.link_checker = LinkChecker()
        self.code_validator = CodeValidator()
        self.metadata_validator = MetadataValidator()
        self.issues: List[QualityIssue] = []
    
    def check_markdown_file(self, file_path: Path) -> None:
        """检查Markdown文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            self.issues.append(QualityIssue(
                str(file_path), "FILE_ERROR", f"无法读取文件: {e}"
            ))
            return
        
        # 检查链接
        links = self.link_checker.find_links_in_markdown(content)
        for url, line_num in links:
            is_valid, message = self.link_checker.check_url(url)
            if not is_valid:
                self.issues.append(QualityIssue(
                    str(file_path), "BROKEN_LINK", 
                    f"链接无效 '{url}': {message}", line_num
                ))
        
        # 检查代码块
        code_blocks = self.code_validator.find_code_blocks(content)
        for language, code, line_num in code_blocks:
            if language:  # 只检查有语言标识的代码块
                validation_issues = self.code_validator.validate_code_block(language, code)
                for issue in validation_issues:
                    self.issues.append(QualityIssue(
                        str(file_path), "CODE_ERROR", 
                        f"{language}代码问题: {issue}", line_num
                    ))
        
        # 检查文档结构
        self._check_document_structure(file_path, content)
    
    def _check_document_structure(self, file_path: Path, content: str) -> None:
        """检查文档结构"""
        lines = content.split('\n')
        
        # 检查是否有标题
        has_h1 = any(line.startswith('# ') for line in lines)
        if not has_h1:
            self.issues.append(QualityIssue(
                str(file_path), "STRUCTURE", "文档缺少主标题(# 标题)"
            ))
        
        # 检查是否有多个H1标题
        h1_count = sum(1 for line in lines if line.startswith('# '))
        if h1_count > 1:
            self.issues.append(QualityIssue(
                str(file_path), "STRUCTURE", f"文档有多个主标题({h1_count}个)"
            ))
    
    def check_json_file(self, file_path: Path, file_type: str = "unknown") -> None:
        """检查JSON文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            self.issues.append(QualityIssue(
                str(file_path), "JSON_ERROR", f"JSON格式错误: {e}"
            ))
            return
        except Exception as e:
            self.issues.append(QualityIssue(
                str(file_path), "FILE_ERROR", f"无法读取文件: {e}"
            ))
            return
        
        # 根据文件类型验证元数据
        if file_type == "project":
            validation_issues = self.metadata_validator.validate_project_metadata(data)
        elif file_type == "module":
            validation_issues = self.metadata_validator.validate_module_metadata(data)
        else:
            validation_issues = []
        
        for issue in validation_issues:
            self.issues.append(QualityIssue(
                str(file_path), "METADATA_ERROR", issue
            ))
    
    def check_directory(self, directory: Path) -> None:
        """检查目录中的所有文档"""
        logger.info(f"检查目录: {directory}")
        
        # 检查Markdown文件
        for md_file in directory.rglob("*.md"):
            logger.debug(f"检查Markdown文件: {md_file}")
            self.check_markdown_file(md_file)
        
        # 检查JSON元数据文件
        for json_file in directory.rglob("*.json"):
            logger.debug(f"检查JSON文件: {json_file}")
            if json_file.name == "project-info.json":
                self.check_json_file(json_file, "project")
            elif json_file.name == "metadata.json":
                self.check_json_file(json_file, "module")
            else:
                self.check_json_file(json_file, "unknown")
    
    def run_quality_check(self) -> Dict:
        """运行质量检查"""
        logger.info("开始文档质量检查")
        self.issues.clear()
        
        # 检查整个MCP目录
        self.check_directory(self.mcp_root)
        
        # 生成报告
        report = self._generate_report()
        
        logger.info(f"质量检查完成，发现 {len(self.issues)} 个问题")
        return report
    
    def _generate_report(self) -> Dict:
        """生成质量检查报告"""
        issue_types = {}
        issue_files = {}
        
        for issue in self.issues:
            # 按类型分组
            if issue.issue_type not in issue_types:
                issue_types[issue.issue_type] = []
            issue_types[issue.issue_type].append(issue)
            
            # 按文件分组
            if issue.file_path not in issue_files:
                issue_files[issue.file_path] = []
            issue_files[issue.file_path].append(issue)
        
        return {
            "total_issues": len(self.issues),
            "issue_types": {k: len(v) for k, v in issue_types.items()},
            "issue_files": {k: len(v) for k, v in issue_files.items()},
            "issues": [str(issue) for issue in self.issues],
            "generated_at": datetime.now().isoformat()
        }
    
    def save_report(self, report: Dict, output_file: Path) -> None:
        """保存质量检查报告"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        logger.info(f"质量检查报告已保存至: {output_file}")

def main():
    parser = argparse.ArgumentParser(description="MCP Documentation Quality Checker")
    parser.add_argument("--mcp-root", default=".", help="MCP root directory")
    parser.add_argument("--output", help="Output report file")
    parser.add_argument("--check-links", action="store_true", help="Check external links (slower)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # 配置日志
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format='%(levelname)s: %(message)s')
    
    # 创建检查器
    checker = DocumentationQualityChecker(args.mcp_root)
    
    # 如果不检查外部链接，跳过链接验证
    if not args.check_links:
        checker.link_checker = None
    
    # 运行质量检查
    report = checker.run_quality_check()
    
    # 输出结果
    print(f"\n=== MCP文档质量检查报告 ===")
    print(f"检查时间: {report['generated_at']}")
    print(f"总问题数: {report['total_issues']}")
    
    if report['total_issues'] > 0:
        print(f"\n问题类型分布:")
        for issue_type, count in report['issue_types'].items():
            print(f"  {issue_type}: {count}")
        
        print(f"\n所有问题:")
        for issue in report['issues']:
            print(f"  {issue}")
    else:
        print("✅ 未发现质量问题")
    
    # 保存报告
    if args.output:
        output_path = Path(args.output)
        checker.save_report(report, output_path)
    else:
        # 默认保存到MCP目录
        output_path = Path(args.mcp_root) / "quality-report.json"
        checker.save_report(report, output_path)
    
    # 返回适当的退出码
    return 1 if report['total_issues'] > 0 else 0

if __name__ == "__main__":
    import ast
    exit(main())
