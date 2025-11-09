# Cursor / Trae 规则配置指南

本文档说明如何在 Cursor、Trae 中配置规则与命令，让日常聊天自动遵循 MCP 项目的文档规范。

---

## 1. 功能概览

- **User Rules**：全局规则，作用于你在 Cursor/Trae 中的所有会话。
- **Project Rules**：只对当前仓库生效，可放置 MCP 专属约定。
- **Project Commands / User Commands**：可重用的指令模板（相当于快捷方式）。
- **Memories**：可选功能，用于保存对话中抽取的事实。

> 规则设置入口：`Settings → Rules, Memories, Commands`（Cursor）或 Trae 对应的 MCP 设置界面。

---

## 2. 推荐配置

### 2.1 User Rules（通用写作规范）

在 User Rules 中添加如下内容，作为所有项目通用的文档写作要求：

```
# Documentation Author Rules

## 总体目标
- 任何涉及文档输出的回答，都要遵循此规则。
- 如果当前仓库存在 Project Rules，则优先遵循 Project Rules；无冲突时执行本规则。

## 写作要求
1. 使用 Markdown；至少包含两级标题。
2. 开头写 2-3 句概述，说明背景与目标。
3. 正文建议包含：架构/模块概览、功能要点、操作步骤或 API、风险与后续工作（缺失信息写 TODO）。
4. 每个代码块前说明用途，代码内带注释。
5. 列表统一使用 `-`，保持句式一致。
6. 引用外部链接时使用 `[名称](URL)` 格式。

## 工作流程
- 用户请求“生成/更新文档”时，先复述关键点，再按规范输出。
- 信息不足时，先列出缺失项并提示需要的输入，然后给出草稿。
- 输出结尾添加 “Next Steps”，提示后续操作（如更新文件、运行脚本）。
```

### 2.2 Project Rules（MCP 专属约定）

在本仓库的 Project Rules 中添加：

```
# MCP Documentation Project Rules

1. 撰写或修改文档前，必须查阅以下文件并遵循模板/字段要求：
   - docs/standards/documentation-guide.md
   - docs/project-setup-guide.md
   - docs/GETTING_STARTED.md 的 “3. 一问一答初始化新语言/项目”
   - docs/integration-guide.md 的 “使用 `process_request` 统一生成文档” 章节

2. 所有项目文档写入 `mcp-docs/<DisplayName>/<Project>/`；模块文档写入 `modules/<module>/`。

3. 处理文档需求时优先调用 MCP 工具：
   - `process_request` 获取规则摘要与操作步骤。
   - `search_documentation` / `analyze_project_structure` 辅助查找或验证。

4. 输出中明确列出需修改/新增的文件路径，并提醒同步更新：
   - `README.md`
   - `project-info.json`
   - `modules/<module>/metadata.json` 等。

5. 项目 README 需遵循仓库模板：概述、目录结构、快速开始、部署/运维、监控与告警、常见问题等章节必须存在；缺失信息填入 TODO。

6. 若信息不足，先提示缺失项；待补充后再给出完整文档草稿。
```

### 2.3 Project Command（快捷调用示例）

可在 Project Commands 中新增一条：

- **Name**：`Doc: process_request`
- **Prompt**：
  ```
  调用 MCP 工具 process_request，intent 为 "{{intent}}"，language "{{language}}", project "{{project}}"，返回结果后整理执行计划并提示需要修改的文件。
  ```
- 启用 “Ask for input”，定义 `intent`、`language`、`project` 为参数。

这样在命令面板中即可快速触发标准流程。

---

## 3. 使用流程建议

1. **初始化**：在项目中打开 Cursor/Trae，先设置上述 User Rules 与 Project Rules。
2. **处理需求**：
   - 在聊天中调用 `Doc: process_request` 命令或手动输入 `call tool process_request …`。
   - 按返回的 `rules`、`steps` 编辑 `mcp-docs/` 下的文档文件。
   - 如需补充资料，调用 `search_documentation`、`analyze_project_structure`。
3. **提交前检查**：运行 `python mcp-server/scripts/quality-checker.py --mcp-root mcp-docs` 或 `mcp-auto-update.py --once`，确保元数据与结构符合规范。
4. **与其他项目共享经验**：若想在不同仓库复用，只需在各自的 Project Rules 中引入对应的模板或链接到本指南。

---

通过在 Cursor/Trae 中配置以上规则，即可确保每次对话、生成文档时都自动遵循 MCP 项目的约定，减少重复提醒和手动审核的工作量。 

