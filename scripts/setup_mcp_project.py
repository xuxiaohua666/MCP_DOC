#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交互式脚本：初始化新的语言 / 项目到 MCP 文档目录。
运行方式：python scripts/setup_mcp_project.py
"""

from pathlib import Path
import json
import textwrap

BASE_DIR = Path(__file__).resolve().parents[1]
CONFIG_FILE = BASE_DIR / "mcp-server" / "mcp-config.json"
DOCS_ROOT = BASE_DIR / "mcp-docs"


def ask(prompt: str, default: str | None = None) -> str:
    suffix = f" [{default}]" if default else ""
    answer = input(f"{prompt}{suffix}: ").strip()
    return answer or (default or "")


def ensure_language(language_name: str, display_name: str, description: str, extensions: list[str]) -> str:
    with CONFIG_FILE.open("r", encoding="utf-8") as f:
        config = json.load(f)

    languages = config.get("supported_languages", [])
    for lang in languages:
        if lang["name"] == language_name:
            print(f"✔️ 语言 {language_name} 已存在")
            return lang["display_name"]

    entry = {
        "name": language_name,
        "display_name": display_name,
        "description": description,
        "file_extensions": extensions,
        "template_suffix": language_name
    }
    languages.append(entry)
    config["supported_languages"] = languages

    with CONFIG_FILE.open("w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    print(f"✅ 已新增语言条目 [{language_name}]")
    return display_name


def create_project(language_display: str, project_name: str) -> Path:
    project_dir = DOCS_ROOT / language_display / project_name
    project_dir.mkdir(parents=True, exist_ok=True)
    (project_dir / "modules").mkdir(exist_ok=True)

    summary = ask("项目一句话描述", "项目简介")
    owner = ask("负责人/团队", "Team")
    repo = ask("Git 仓库地址", "https://github.com/your-org/your-project.git")
    status = ask("项目状态", "active")
    contacts = [c.strip() for c in ask("维护人邮箱 (逗号分隔)", "someone@example.com").split(",") if c.strip()]

    project_info = {
        "project_metadata": {
            "name": project_name,
            "summary": summary,
            "language": ask("语言标识（与 mcp-config 中一致）", language_display.lower()),
            "owner_team": owner,
            "status": status,
            "documentation_contacts": contacts,
            "repositories": [{"type": "git", "url": repo}],
            "links": [
                {
                    "name": ask("常用链接名称", "生产环境"),
                    "url": ask("常用链接地址", "https://prod.example.com"),
                    "description": ask("链接描述", "生产环境入口")
                }
            ],
            "tags": [t.strip() for t in ask("标签 (逗号分隔)", language_display.lower()).split(",") if t.strip()]
        }
    }

    with (project_dir / "project-info.json").open("w", encoding="utf-8") as f:
        json.dump(project_info, f, indent=2, ensure_ascii=False)

    readme_content = textwrap.dedent(f"""
    # {project_name}

    ## 概述
    - 介绍：{summary}
    - 技术栈：{ask("技术栈说明", "待完善")}

    ## 目录结构
    ```
    {project_name}/
      ├── src/
      ├── README.md
      └── ...
    ```

    ## 快速开始
    ```bash
    # 安装依赖
    ...
    # 启动
    ...
    ```

    ## 部署与运维
    - CI/CD：{ask("CI/CD 描述", "待完善")}
    - 环境变量：...

    ## 监控与告警
    - 监控面板：{ask("监控面板地址", "https://monitor.example.com")}
    - 日志位置：...

    ## 常见问题
    1. ...
    """).strip()

    with (project_dir / "README.md").open("w", encoding="utf-8") as f:
        f.write(readme_content + "\n")

    print(f"✅ 已创建项目目录：{project_dir}")
    return project_dir


def maybe_add_module(project_dir: Path) -> None:
    if ask("是否创建示例模块？(y/n)", "n").lower() != "y":
        return

    module_name = ask("模块名称", "module")
    module_dir = project_dir / "modules" / module_name
    module_dir.mkdir(parents=True, exist_ok=True)

    module_meta = {
        "module_metadata": {
            "name": module_name,
            "description": ask("模块简介", "模块描述"),
            "status": ask("模块状态", "stable"),
            "owners": [ask("模块负责人", "module-owner")]
        },
        "technical_details": {
            "entry_file": ask("模块入口文件", "src/index.js"),
            "dependencies": {
                "internal": [],
                "external": [
                    {"library": dep.strip()} for dep in ask("外部依赖(逗号分隔)", "").split(",") if dep.strip()
                ]
            }
        }
    }

    with (module_dir / "metadata.json").open("w", encoding="utf-8") as f:
        json.dump(module_meta, f, indent=2, ensure_ascii=False)

    module_readme = textwrap.dedent(f"""
    # {module_name} 模块

    ## 职责
    - {ask("模块职责描述", "说明模块负责的功能")}

    ## 接口/能力
    - ...

    ## 注意事项
    - ...
    """).strip()

    with (module_dir / "README.md").open("w", encoding="utf-8") as f:
        f.write(module_readme + "\n")

    print(f"✅ 已添加模块：{module_name}")


def main():
    language_name = ask("语言标识（如 node、go、rust）", "node").strip()
    display_name = ask("语言显示名称（如 NodeJS、Go）", language_name.capitalize())
    description = ask("语言描述", f"{display_name} 项目")
    extensions = [ext.strip() for ext in ask("文件扩展名 (逗号分隔)", ".js,.ts").split(",") if ext.strip()]

    display_name = ensure_language(language_name, display_name, description, extensions)

    project_name = ask("项目名称", "demo-project")
    project_dir = create_project(display_name, project_name)
    maybe_add_module(project_dir)

    print("\n🎉 MCP 文档结构已准备就绪！后续步骤：")
    print("1. 将实际 README、技术文档同步到上述目录。")
    print("2. 启动 MCP 服务：")
    print("   - HTTP 模式：python start.py --mode http --host 0.0.0.0 --port 7778")
    print("   - STDIO 模式：command=python, args=['start.py','--mode','mcp','--skip-checks'], cwd=仓库路径")
    print("3. 在 Cursor / Trae 中刷新服务器，即可看到新项目。")


if __name__ == "__main__":
    main()
