---
name: lark-base
version: 1.2.3
description: "飞书多维表格操作：建表、字段、记录、视图、公式/lookup、表单、仪表盘、workflow、角色权限。"
metadata:
  requires:
    bins: ["lark-cli"]
  cliHelp: "lark-cli base --help"
---

# base

## 何时使用

使用本 skill：

- 用户明确提到 Base / 多维表格 / bitable，或给出 `/base/` 链接。
- 用户要在 Base 内建表、改表、管理字段、写记录、查记录、配视图。
- 用户要在 Base 内做公式字段、lookup 字段、跨表计算、派生指标、筛选聚合、TopN、统计分析。
- 用户要管理 Base 表单、仪表盘、workflow、高级权限或角色。
- 用户要把旧 Base 聚合式命令或旧写法迁移到当前 `lark-cli base +...` shortcut。

不要使用本 skill：

- 只是认证、初始化配置、切换身份、处理 scope 或权限授权恢复，转 `lark-shared`。
- 把本地 Excel / CSV / `.base` 导入成 Base，转 `lark-cli drive +import --type bitable`。
- 泛化数据分析、字段设计、公式讨论，但没有 Base/多维表格上下文。

## 使用边界

- Base 业务操作只使用 `lark-cli base +...` shortcut，不使用旧聚合式 `+table / +field / +record / +view / +history / +workspace`。
- 执行 update 前必须先查当前 shortcut 的 `--help` 或对应 reference。若命令要求完整配置，首次请求必须基于可信的当前配置执行 read-modify-write：只修改用户明确指定的内容，保留其他仍适用的可写配置，并按命令要求的结构提交。若命令支持局部／delta update，按其契约提交最小合法 payload；不得以不完整请求试错补参。
- 用户要把 Excel / CSV / `.base` 导入成 Base 时，先转 `lark-cli drive +import --type bitable`，导入完成后再回到 Base 命令。
- 认证、初始化、scope、身份切换、权限不足恢复属于 `lark-shared`；Base 文档只保留会影响 Base 路径选择的权限规则。

## 先获取 Base Token 和所需 ID

进入任何需要目标 Base 的 shortcut 前，必须先拿到可用的 `base_token`，以及当前任务需要的 `table_id` / `view_id` / `record_id` / `form_id` / `dashboard_id` / `workflow_id` 等真实 ID；不要把完整 URL、wiki token、workspace token 或孤立 raw token 直接当作 `--base-token`。

- 用户输入 URL 或分享链接：先运行 `lark-cli base +url-resolve --url "<url>" --as user`，用返回的 `base_token` 和相关 ID 继续后续命令。
- 用户输入 Base 标题、关键词或不确定名称：先运行 `lark-cli base +title-resolve --title "<keyword>" --as user`；`--title` 传入标题中的短关键词，不超过 30 个字符；过长标题先取最有区分度的短关键词；多候选时先让用户消歧，不要猜。
- 文档嵌入 Base 标签：直接读取 `<bitable>` / `<base_refer>` 的 `token` 作为 `--base-token`，`table-id` 作为 `--table-id`，`view-id` 作为 `--view-id`；孤立 raw token 不走 `+url-resolve`。
- 仍无法定位且用户不是要新建 Base 时，先反问用户要操作哪一个 Base；用户要新建时才用 `+base-create`。

## 快速路由

| 用户目标 | 优先命令 | 何时读 reference |
|---|---|---|
| 查 Base 本体 | `+base-get` | 用返回确认 Base 名称、owner、权限和可继续操作的 token |
| 创建/复制 Base | `+base-create` / `+base-copy` | 新建时强烈推荐用 `--table-name` + `--fields` 同时配置新 Base 里唯一一个初始数据表的 name 和 schema；写入后报告新 Base 标识和 `permission_grant` |
| 查看 Base 内资源目录 | `+base-block-list` | 想先了解一个 Base 里有哪些 table/docx/dashboard/workflow/folder 时优先用它；返回 ID 关系和 fewshot 看 `--help` |
| 管理 Base 内资源目录 | `+base-block-create/move/rename/delete` | 创建或整理 Base 直接管理的 folder/table/docx/dashboard/workflow；资源内容继续用对应命令 |
| 管理数据表 | `+table-list/get/create/update/delete` | 处理 table 的列出、详情、创建、重命名和删除 |
| 列/查/删字段 | `+field-list/get/delete/search-options` | 写入前用 list/get 确认字段类型、选项、ID；删除前确认目标字段 |
| 创建/更新字段 | `+field-create` / `+field-update` | 必读 [lark-base-field-json.md](references/lark-base-field-json.md)；公式读 [formula-field-guide.md](references/formula-field-guide.md)；lookup 读 [lookup-field-guide.md](references/lookup-field-guide.md)；命令细节读 [lark-base-field-create.md](references/lark-base-field-create.md) / [lark-base-field-update.md](references/lark-base-field-update.md) |
| 读记录明细 | `+record-get` / `+record-list` / `+record-search` | 涉及筛选、排序、Top/Bottom N、聚合、多表关联、全局结论时读 [lark-base-data-analysis-sop.md](references/lark-base-data-analysis-sop.md) |
| 写记录 | `+record-upsert` / `+record-batch-create` / `+record-batch-update` | 必读 [lark-base-record-upsert.md](references/lark-base-record-upsert.md) / [lark-base-record-batch-create.md](references/lark-base-record-batch-create.md) / [lark-base-record-batch-update.md](references/lark-base-record-batch-update.md) 和 [lark-base-cell-value.md](references/lark-base-cell-value.md) |
| 附件字段 | `+record-upload-attachment` / `+record-download-attachment` / `+record-remove-attachment` | 附件不要伪造成普通 CellValue；上传走本地文件，下载/删除按 file token 或字段定位 |
| 删除记录 / 分享记录链接 / 历史 | `+record-delete` / `+record-share-link-create` / `+record-history-list` | 删除前确认 record；分享链接最多 100 条；历史读 [lark-base-record-history-list.md](references/lark-base-record-history-list.md)，只查单条记录，不做整表审计 |
| 管理视图 | `+view-*` | `+view-set-filter` 读 [lark-base-view-set-filter.md](references/lark-base-view-set-filter.md)；其余配置先 get 现状，再按返回结构更新 |
| 一次性聚合统计 | `+data-query` | 必读 [lark-base-data-analysis-sop.md](references/lark-base-data-analysis-sop.md) 和入口 [lark-base-data-query-guide.md](references/lark-base-data-query-guide.md)；完整 DSL 再读 [lark-base-data-query.md](references/lark-base-data-query.md) |
| 公式字段 | `+field-create/update --json '{"type":"formula",...}'` | 必读 [formula-field-guide.md](references/formula-field-guide.md)，读后再加隐藏确认 flag `--i-have-read-guide` |
| Lookup 字段 | `+field-create/update --json '{"type":"lookup",...}'` | 必读 [lookup-field-guide.md](references/lookup-field-guide.md)，读后再加隐藏确认 flag `--i-have-read-guide` |
| 表单提交 | `+form-submit` | 先读 [lark-base-form-detail.md](references/lark-base-form-detail.md) 获取题目、filter 和附件所需 `base_token`；提交 JSON 读 [lark-base-form-submit.md](references/lark-base-form-submit.md) |
| 表单题目创建/更新 | `+form-questions-create` / `+form-questions-update` | 读 [lark-base-form-questions-create.md](references/lark-base-form-questions-create.md) / [lark-base-form-questions-update.md](references/lark-base-form-questions-update.md) |
| 其他表单管理 | `+form-list/get/detail/create/update/delete` / `+form-questions-list/delete` | `+form-detail` 读 [lark-base-form-detail.md](references/lark-base-form-detail.md)；删除前确认目标表单 |
| 仪表盘与组件 | `+dashboard-*` / `+dashboard-block-*` | 提到图表/看板/block 时先读 [lark-base-dashboard.md](references/lark-base-dashboard.md)；组件 `data_config` 读 [dashboard-block-data-config.md](references/dashboard-block-data-config.md)；读取图表计算结果用 `+dashboard-block-get-data` |
| Workflow | `+workflow-*` | 创建/更新或理解 steps 时读入口 [lark-base-workflow-guide.md](references/lark-base-workflow-guide.md) 和 steps JSON SSOT [lark-base-workflow-schema.md](references/lark-base-workflow-schema.md)；list/get/enable/disable 只处理 workflow ID 与启停状态 |
| 高级权限与角色 | `+advperm-*` / `+role-*` | 角色操作先读入口 [lark-base-role-guide.md](references/lark-base-role-guide.md)；角色 create/update 或解读完整配置再读权限 JSON SSOT [role-config.md](references/role-config.md)；系统角色不可删除；关闭高级权限会影响自定义角色 |

## Base 心智模型

- Base 曾用名 Bitable；返回字段、错误或旧文档里的 `bitable` 多为历史兼容，不代表应改走裸 API 或另一套命令。
- `+base-block-list` 是查看一个 Base 内资源目录的新入口：它列出这个 Base 直接管理的 `folder/table/docx/dashboard/workflow`，适合先判断 Base 里有什么，再决定走 table、dashboard、workflow 或 docx 命令。
- `base-block` 只负责资源目录管理，包括创建资源、移动到 folder、重命名和删除；具体资源内容仍走 table/dashboard/workflow 命令。
- 新建 Base 时，强烈推荐一次性执行 `lark-cli base +base-create --name "<base>" --table-name "<table>" --fields '<field-json-array>'`，同时配置新 Base 里唯一一个初始数据表的 name 和 schema；使用 `--fields` 前先读 [lark-base-field-json.md](references/lark-base-field-json.md) 或复用 `+field-create` 的字段 JSON 形状，不要猜字段属性。
- `+base-create` 不传 `--table-name` 和 `--fields` 时，会创建一个默认 schema 的初始数据表。
- 表、字段、视图、workflow、dashboard block 的名称和 ID 必须来自真实返回，不要凭用户口述猜。
- 存储字段可写；系统字段、`formula`、`lookup` 只读；附件字段走专用 attachment 命令。
- 一次性原始记录查询优先用 `+record-list` / `+record-search` 的 filter/sort；聚合分析优先用 `+data-query`；需要长期显示在表中时，才新增 `formula` / `lookup` 字段。
