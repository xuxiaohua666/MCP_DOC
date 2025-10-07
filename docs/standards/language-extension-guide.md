# MCP文档服务器 - 多语言扩展指南

## 概述
本指南说明如何为MCP文档服务器添加新的编程语言支持，包括配置更新、模板定制、代码分析器扩展等。

## 添加新语言的步骤

### 1. 更新MCP配置

编辑 `mcp-config.json` 文件，在 `supported_languages` 数组中添加新语言：

```json
{
  "name": "python",
  "display_name": "Python",
  "description": "Python编程语言开发",
  "file_extensions": [".py"],
  "template_suffix": "python",
  "logging_framework": "logging",
  "test_framework": "pytest"
}
```

#### 配置字段说明
- `name`: 语言标识符，用于内部引用
- `display_name`: 显示名称
- `description`: 语言描述
- `file_extensions`: 文件扩展名列表
- `template_suffix`: 模板后缀名
- `logging_framework`: 推荐的日志框架
- `test_framework`: 推荐的测试框架

### 2. 创建语言目录

在MCP根目录下创建对应的语言目录：

```bash
mkdir Python
```

### 3. 创建语言特定模板

#### 3.1 项目文档模板
创建 `templates/project-template-python.md`（可选，如果需要语言特定模板）：

```markdown
# {项目名称}

## 项目概述
<!-- Python项目的特定描述格式 -->

## 技术栈
- **Python版本**: {python_version}
- **主要框架**: {framework}
- **包管理**: {package_manager}

## 虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

## 依赖管理
```bash
pip install -r requirements.txt
```

## 代码规范
- 遵循PEP 8编码标准
- 使用类型提示 (Type Hints)
- 日志使用英文，注释使用中文
- 日志级别最低使用info

## 测试
```bash
pytest tests/ -v --cov
```
```

#### 3.2 模块文档模板
创建 `templates/module-template-python.md`：

```markdown
# {模块名称}

## 模块概述
<!-- Python模块的功能说明 -->

## 主要类和函数

### {主要类名}
```python
class {主要类名}:
    """中文注释：类的功能说明"""
    
    def {主要方法}(self, param: {类型}) -> {返回类型}:
        """中文注释：方法功能说明
        
        Args:
            param: 参数说明
            
        Returns:
            返回值说明
        """
        logger.info("Method execution started")
        # 中文注释：实现逻辑
        pass
```

## 使用示例
```python
# 中文注释：使用示例
from {模块名称} import {主要类名}

instance = {主要类名}()
result = instance.{主要方法}(参数)
```

## 异常处理
```python
try:
    # 中文注释：可能出错的操作
    result = some_operation()
    logger.info("Operation completed successfully")
except SpecificException as e:
    logger.error("Operation failed: %s", str(e))
    raise
```
```

### 4. 扩展代码分析器

编辑 `scripts/template-processor.py`，在 `CodeAnalyzer` 类中添加新语言的分析方法：

```python
def analyze_python_file(self, file_path: Path) -> Dict[str, Any]:
    """分析Python文件"""
    info = {
        "classes": [],
        "functions": [],
        "imports": [],
        "decorators": []
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 使用AST分析Python代码
        import ast
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                info["classes"].append({
                    "name": node.name,
                    "type": "class",
                    "line": node.lineno
                })
            elif isinstance(node, ast.FunctionDef):
                info["functions"].append({
                    "name": node.name,
                    "args": [arg.arg for arg in node.args.args],
                    "line": node.lineno
                })
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    info["imports"].append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    info["imports"].append(node.module)
    
    except Exception as e:
        logger.warning(f"Failed to analyze Python file {file_path}: {e}")
    
    return info
```

然后在 `analyze_file` 方法中添加对新语言的支持：

```python
def analyze_file(self, file_path: Path) -> Dict[str, Any]:
    """根据语言分析文件"""
    if self.language == "python" and file_path.suffix == ".py":
        return self.analyze_python_file(file_path)
    # ... 其他语言的条件
    else:
        return {}
```

### 5. 更新质量检查器

编辑 `scripts/quality-checker.py`，在 `CodeValidator` 类中添加新语言的验证方法：

```python
def _validate_python_code(self, code: str) -> List[str]:
    """验证Python代码"""
    issues = []
    
    try:
        # 使用AST检查语法
        import ast
        ast.parse(code)
    except SyntaxError as e:
        issues.append(f"Python语法错误: {e}")
    
    # 检查代码风格
    lines = code.split('\n')
    for i, line in enumerate(lines, 1):
        # 检查行长度
        if len(line) > 88:  # PEP 8建议
            issues.append(f"第{i}行过长 ({len(line)} > 88 字符)")
        
        # 检查缩进
        if line.strip() and not line.startswith('#'):
            indent = len(line) - len(line.lstrip())
            if indent % 4 != 0:
                issues.append(f"第{i}行缩进不是4的倍数")
    
    return issues
```

更新 `supported_languages` 字典：

```python
self.supported_languages = {
    'java': self._validate_java_code,
    'gdscript': self._validate_gdscript_code,
    'python': self._validate_python_code,  # 新增
    # ... 其他语言
}
```

### 6. 创建语言扩展工具

创建 `scripts/add-language.py`：

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP语言扩展工具
自动添加新编程语言支持
"""

import json
import logging
from pathlib import Path
from typing import Dict, List
import argparse

logger = logging.getLogger(__name__)

class LanguageExtender:
    """语言扩展器"""
    
    def __init__(self, mcp_root: str):
        self.mcp_root = Path(mcp_root)
        self.config_file = self.mcp_root / "mcp-config.json"
        
    def add_language(self, language_config: Dict) -> bool:
        """添加新语言支持"""
        try:
            # 读取配置文件
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 检查语言是否已存在
            existing_names = {lang["name"] for lang in config["supported_languages"]}
            if language_config["name"] in existing_names:
                logger.warning(f"Language '{language_config['name']}' already exists")
                return False
            
            # 添加新语言
            config["supported_languages"].append(language_config)
            
            # 保存配置文件
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            # 创建语言目录
            lang_dir = self.mcp_root / language_config["display_name"]
            lang_dir.mkdir(exist_ok=True)
            
            logger.info(f"Successfully added language: {language_config['display_name']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add language: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description="MCP Language Extender")
    parser.add_argument("--name", required=True, help="Language identifier")
    parser.add_argument("--display-name", required=True, help="Display name")
    parser.add_argument("--description", required=True, help="Language description")
    parser.add_argument("--extensions", nargs="+", required=True, help="File extensions")
    parser.add_argument("--logging-framework", help="Logging framework")
    parser.add_argument("--test-framework", help="Test framework")
    parser.add_argument("--mcp-root", default=".", help="MCP root directory")
    
    args = parser.parse_args()
    
    language_config = {
        "name": args.name,
        "display_name": args.display_name,
        "description": args.description,
        "file_extensions": args.extensions,
        "template_suffix": args.name,
        "logging_framework": args.logging_framework or "standard",
        "test_framework": args.test_framework or "standard"
    }
    
    extender = LanguageExtender(args.mcp_root)
    
    if extender.add_language(language_config):
        print(f"✅ Successfully added {args.display_name} support")
        print(f"📁 Created directory: {args.display_name}/")
        print(f"⚙️ Updated configuration in mcp-config.json")
        print(f"📝 Next steps:")
        print(f"   1. Create language-specific templates if needed")
        print(f"   2. Extend code analyzer in template-processor.py")
        print(f"   3. Add validation rules in quality-checker.py")
    else:
        print(f"❌ Failed to add {args.display_name} support")
        return 1
    
    return 0

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    exit(main())
```

## 语言特定配置

### Python示例
```json
{
  "name": "python",
  "display_name": "Python",
  "description": "Python编程语言开发",
  "file_extensions": [".py"],
  "template_suffix": "python",
  "logging_framework": "logging",
  "test_framework": "pytest",
  "style_guide": "PEP 8",
  "package_manager": "pip",
  "virtual_env": "venv"
}
```

### TypeScript示例
```json
{
  "name": "typescript",
  "display_name": "TypeScript",
  "description": "TypeScript web应用开发",
  "file_extensions": [".ts", ".tsx"],
  "template_suffix": "typescript",
  "logging_framework": "winston",
  "test_framework": "jest",
  "style_guide": "ESLint",
  "package_manager": "npm",
  "build_tool": "webpack"
}
```

### Go示例
```json
{
  "name": "go",
  "display_name": "Go",
  "description": "Go语言服务端开发",
  "file_extensions": [".go"],
  "template_suffix": "go",
  "logging_framework": "logrus",
  "test_framework": "testing",
  "style_guide": "gofmt",
  "package_manager": "go mod",
  "build_tool": "go build"
}
```

## 模板变量扩展

对于新语言，可能需要添加特定的模板变量。在 `template-processor.py` 中的 `create_variable_context` 方法中添加：

```python
def create_variable_context(self, project_info: Dict[str, Any], module_info: Dict[str, Any] = None) -> Dict[str, str]:
    context = {
        # 通用变量
        # ...
    }
    
    # 语言特定变量
    if project_info.get("language") == "python":
        context.update({
            "python_version": self._detect_python_version(project_info),
            "package_manager": "pip",
            "virtual_env_command": "python -m venv"
        })
    elif project_info.get("language") == "typescript":
        context.update({
            "node_version": self._detect_node_version(project_info),
            "package_manager": "npm",
            "build_command": "npm run build"
        })
    
    return context
```

## 测试新语言支持

添加新语言后，建议进行以下测试：

1. **配置验证**
   ```bash
   python scripts/mcp-auto-update.py --validate-only
   ```

2. **模板处理测试**
   ```bash
   python scripts/template-processor.py --language python --project-path ./Python/test-project
   ```

3. **质量检查测试**
   ```bash
   python scripts/quality-checker.py --mcp-root .
   ```

## 最佳实践

### 1. 语言分析器
- 使用语言原生的AST解析器（如Python的ast模块）
- 提取关键信息：类、函数、导入、注释
- 处理语言特定的语法特性

### 2. 代码验证
- 检查语法正确性
- 验证代码风格（如Python的PEP 8）
- 检查最佳实践（如错误处理模式）

### 3. 模板定制
- 包含语言特定的项目结构
- 提供合适的代码示例
- 说明语言特有的工具和流程

### 4. 文档规范
- 遵循语言社区的文档标准
- 包含语言特定的安装和配置说明
- 提供常见问题和解决方案

## 扩展清单

添加新语言支持时，请确保完成以下任务：

- [ ] 更新 `mcp-config.json` 配置
- [ ] 创建语言目录
- [ ] 扩展代码分析器
- [ ] 添加代码验证规则
- [ ] 创建语言特定模板（如需要）
- [ ] 更新文档模板变量
- [ ] 添加示例项目
- [ ] 测试所有功能
- [ ] 更新用户文档

---
*遵循此指南可以确保新语言与MCP文档服务器的完美集成*
