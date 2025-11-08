# 新项目创建指南（PHP / Java）

本文档演示如何基于 `mcp-docs` 目录与模板体系创建新的项目文档，分别以 PHP 与 Java 为例。流程适用于所有语言，核心步骤包括：复制模板、完善 `project-info.json`、添加 README / 模块文档，并在 `mcp-config.json` 中登记。

---

## 目录概览

```
mcp-docs/
├── templates/
│   ├── project-template.md
│   ├── module-template.md
│   ├── api-template.md
│   ├── metadata.json
│   └── project-info.json
├── Java/
│   └── example-web-service/
└── GDScript/
    └── example-game-project/
```

---

## 通用步骤

1. **确定语言目录**
   - 若已有语言目录（如 `Java/`），直接在其下创建新项目。
   - 若是新增语言（如 PHP），先阅读 `docs/standards/language-extension-guide.md`，然后：
     1. 在 `mcp-docs` 下创建 `PHP/` 目录。
     2. 在 `mcp-docs/mcp-config.json` 的 `supported_languages` 中添加：
        ```json
        {
          "name": "php",
          "display_name": "PHP"
        }
        ```
2. **复制模板文件**
   - 拷贝 `templates/project-info.json` 至目标项目根目录，改名为 `project-info.json`。
   - 使用 `templates/project-template.md` 生成项目 `README.md`。
   - 若有模块，复制 `templates/module-template.md` 并放在子目录内，配套 `metadata.json`。
3. **填写项目信息**
   - 修改 `project-info.json` 中的 `project_metadata`、`modules` 等字段。
   - 更新 README，补充背景、架构、部署、API 等信息。
4. **更新配置**
   - 确保 `mcp-docs/mcp-config.json` 中对应语言条目存在。
   - 必要时运行 `python mcp-server/scripts/template-processor.py` 生成初始文档骨架。
5. **测试**
   - 启动文档服务器：`python start.py --server-type rest --skip-checks`.
   - 打开 `http://localhost:7778/projects` 验证新项目是否出现。

---

## 示例：创建 PHP 项目

假设项目名称为 `payment-service`，目录结构如下：

```
mcp-docs/
└── PHP/
    └── payment-service/
        ├── README.md
        ├── project-info.json
        └── modules/
            └── payment-core/
                ├── README.md
                └── metadata.json
```

### 操作步骤

1. **创建目录**
   ```bash
   mkdir -p mcp-docs/PHP/payment-service/modules/payment-core
   ```
2. **复制模板**
   ```bash
   cp mcp-docs/templates/project-info.json mcp-docs/PHP/payment-service/project-info.json
   cp mcp-docs/templates/project-template.md mcp-docs/PHP/payment-service/README.md
   cp mcp-docs/templates/module-template.md mcp-docs/PHP/payment-service/modules/payment-core/README.md
   cp mcp-docs/templates/metadata.json mcp-docs/PHP/payment-service/modules/payment-core/metadata.json
   ```
3. **编辑 `project-info.json`（示例片段）**
   ```json
   {
     "project_metadata": {
       "name": "payment-service",
       "summary": "PHP 实现的支付中心服务",
       "language": "php",
       "owner_team": "Fintech Platform",
       "status": "in_production"
     },
     "modules": [
       {
         "name": "payment-core",
         "summary": "订单支付与账单结算逻辑"
       }
     ]
   }
   ```
4. **完善 README**
   - 描述项目目标、技术栈（PHP 8、Laravel 等）、部署方式、接口说明。
5. **维护模块文档**
   - 在 `modules/payment-core/README.md` 中写出模块设计、依赖、接口表。
6. **运行质量检查（可选）**
   ```bash
   python mcp-server/scripts/quality-checker.py --mcp-root mcp-docs --project php/payment-service
   ```

---

## 示例：创建 Java 项目

目标项目 `order-service`，结构如下：

```
mcp-docs/
└── Java/
    └── order-service/
        ├── README.md
        ├── project-info.json
        └── modules/
            └── order-api/
                ├── README.md
                └── metadata.json
```

### 操作步骤

1. **复制现有示例为模板**
   ```bash
   cp -R mcp-docs/Java/example-web-service mcp-docs/Java/order-service
   ```
   或按上述通用方法自建目录并复制模板。
2. **更新项目信息**
   - 修改 `project-info.json` 中的 `name`、`summary`、`tags` 等字段。
   - 调整 README：技术栈（Spring Boot）、数据库、API 路由、部署方式。
3. **维护模块信息**
   - 若存在多个微服务模块，可在 `modules/` 下按模块拆分文档。
4. **同步配置**
   - 确保 `mcp-docs/mcp-config.json` 已包含 `Java` 语言，并在需要时更新 `supported_languages` 的元数据（如标签、Docs 路径）。
5. **校验**
   - 重启文档服务器，访问 `http://localhost:7778/projects/java/order-service` 确认内容。

---

## 自动化脚本推荐

| 场景 | 命令 |
| ---- | ---- |
| 生成模板骨架 | `python mcp-server/scripts/template-processor.py --project-path mcp-docs/PHP/payment-service --language php` |
| 质量检查 | `python mcp-server/scripts/quality-checker.py --mcp-root mcp-docs --project php/payment-service` |
| 生成性能报告 | `python mcp-server/scripts/performance-monitor.py --action report --output performance-report.json` |

---

## 提交前检查清单

- [ ] `project-info.json` 字段填写完整且合法。
- [ ] README 内容覆盖背景、架构、部署、接口、运维等信息。
- [ ] `mcp-config.json` 已登记语言/项目。
- [ ] 运行质量检查脚本，确认无严重告警。
- [ ] 通过 MCP 工具和资源接口可以检索到新项目内容。

完成以上步骤后，新项目即可被 MCP 文档服务器识别，并在 Cursor、Trae 等集成环境中使用。 

