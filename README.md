# Hermes Skills

> Personal skill collection for [Hermes Agent](https://github.com/NousResearch/hermes-agent) — **38 skills** across **35 categories**.

## 📋 Overview

- **🔧 DevOps** — 1 skill
- **🔥 Grill Me** — 1 skill
- **🔥 Grill with Docs** — 1 skill
- **⚙️ Hermes Operations** — 3 skills
- **🖨️ HTML to PDF** — 1 skill
- **🏗️ Codebase Architecture** — 1 skill
- **📋 Lark Approval** — 1 skill
- **📱 Lark Apps** — 1 skill
- **🕐 Lark Attendance** — 1 skill
- **🗄️ Lark Base** — 1 skill
- **📅 Lark Calendar** — 1 skill
- **📦 lark-cli-pitfalls** — 1 skill
- **👤 Lark Contact** — 1 skill
- **📄 Lark Doc** — 1 skill
- **☁️ Lark Drive** — 1 skill
- **🔔 Lark Event** — 1 skill
- **💬 Lark IM** — 1 skill
- **📧 Lark Mail** — 1 skill
- **📝 Lark Markdown** — 1 skill
- **🎙️ Lark Minutes** — 1 skill
- **🎯 Lark OKR** — 1 skill
- **🔍 Lark OpenAPI Explorer** — 1 skill
- **🔗 Lark Shared** — 1 skill
- **📊 Lark Sheets** — 1 skill
- **🛠️ Lark Skill Maker** — 1 skill
- **📽️ Lark Slides** — 1 skill
- **✅ Lark Task** — 1 skill
- **📹 Lark VC** — 1 skill
- **🤖 Lark VC Agent** — 1 skill
- **🎨 Lark Whiteboard** — 1 skill
- **📚 Lark Wiki** — 1 skill
- **📋 Meeting Summary** — 1 skill
- **📊 Standup Report** — 1 skill
- **⚡ Productivity** — 1 skill
- **💻 Software Development** — 2 skills

---

## 🔧 DevOps

- **`embedded-hw-sw-gap-analysis`** — Use when integrating embedded Linux software with custom hardware — systematically cross-reference schematics, SoC datasheets, UI design PDFs, and codebase to extract hardware information gaps that block deployment.
  `devops/embedded-hw-sw-gap-analysis/`


## 🔥 Grill Me

- **`grill-me`** — A relentless interview to sharpen a plan or design.
  `grill-me/`


## 🔥 Grill with Docs

- **`grill-with-docs`** — A relentless interview to sharpen a plan or design, which also creates docs (ADR's and glossary) as we go.
  `grill-with-docs/`


## ⚙️ Hermes Operations

- **`hermes-operations`** — Operate, configure, and maintain Hermes Agent — model benchmarking, web UI integration, skill library management (sync, audit, cleanup), and memory optimization. Use when choosing models, connecting web frontends, syncing skills across devices, au...
  `hermes/hermes-operations/`

- **`hermes-session-lifecycle-debugging`** — Debug Hermes Agent session context loss, lifecycle issues, and gateway restart problems by correlating session files, agent logs, gateway code, and the sessions registry.
  `hermes/hermes-session-lifecycle-debugging/`

- **`smart-model-switch`** — Smart model switching between MiMo (daily), Qwen (complex agent tasks), and DeepSeek (coding/budget) based on task complexity. Uses the agent's own judgment to suggest switching models via /model command.
  `hermes/smart-model-switch/`


## 🖨️ HTML to PDF

- **`html-to-pdf-macos`** — Convert HTML or Markdown documents to PDF on macOS. Use xhtml2pdf as the primary method — weasyprint fails due to missing pango system libraries.
  `html-to-pdf-macos/`


## 🏗️ Codebase Architecture

- **`improve-codebase-architecture`** — Scan a codebase for deepening opportunities, present them as a visual HTML report, then grill through whichever one you pick.
  `improve-codebase-architecture/`


## 📋 Lark Approval

- **`lark-approval`** — 飞书审批 API：审批实例、审批任务管理。
  `lark-approval/`


## 📱 Lark Apps

- **`lark-apps`** — 把本地 HTML 文件或目录部署到飞书妙搭（Miaoda），生成一个公网可访问的应用及其链接（URL）。当用户要创建 HTML 或要把 HTML、静态网站或 Web demo 发布成公网可访问的链接 / 可分享链接、设置应用共享范围，或提到妙搭 / Miaoda 时使用。凡产出可独立访问的 HTML 产物都属本 skill 的潜在归宿，是否真要部署由 skill 内部协议判断。不用于：上传普通文件到云空间/云盘/云存储（用 lark-drive）、编辑飞书云文档内容（用 lark-doc）...
  `lark-apps/`


## 🕐 Lark Attendance

- **`lark-attendance`** — 飞书考勤打卡：查询自己的考勤打卡记录
  `lark-attendance/`


## 🗄️ Lark Base

- **`lark-base`** — 当需要用 lark-cli 操作飞书多维表格（Base）时调用：搜索 Base、建表、字段管理、记录读写、记录分享链接、视图配置、历史查询，以及角色/表单/仪表盘管理/工作流；也适用于把旧的 +table / +field / +record 写法改成当前命令写法。涉及字段设计、公式字段、查找引用、跨表计算、行级派生指标、数据分析需求时也必须使用本 skill。
  `lark-base/`


## 📅 Lark Calendar

- **`lark-calendar`** — 飞书日历（calendar）：提供日历与日程（会议）的全面管理能力。核心场景包括：查看/搜索日程、创建/更新日程、管理参会人、查询忙闲状态及推荐空闲时段、查询/搜索与预定会议室。注意：涉及【预约日程/会议】或【查询/预定会议室】时，必须先读取 references/lark-calendar-schedule-meeting.md 工作流！高频操作请优先使用 Shortcuts：+agenda（快速概览今日/近期行程）、+create（创建日程并按需邀请参会人及预定会议室）、+update...
  `lark-calendar/`


## 📦 lark-cli-pitfalls

- **`lark-cli-pitfalls`** — Session-discovered pitfalls, workflows, capability map, and evolution directions for lark-cli. Supplements hub-installed lark-shared with real-world gotchas, official capability reference, and doc-access techniques.
  `lark-cli-pitfalls/`


## 👤 Lark Contact

- **`lark-contact`** — 飞书 / Lark 通讯录,用于按姓名 / 邮箱把员工解析成 open_id,以及按 open_id 反查员工的姓名 / 部门 / 邮箱 / 联系方式。当用户说出某人姓名而下一步需要发消息 / 加群 / 排日程时,先用本 skill 把姓名换成 ID;当输出里出现 open_id 需要展示成姓名给用户看,或用户直接询问某人的部门 / 邮箱 / 联系方式时,用本 skill 查。不负责部门树遍历、按部门列员工、组织架构图,这类需求走原生 OpenAPI。
  `lark-contact/`


## 📄 Lark Doc

- **`lark-doc`** — 飞书云文档 / Docx / 知识库 Wiki 文档（v2）：创建、打开、读取、获取、查看、总结、整理、改写、翻译、审阅和编辑飞书文档内容。当用户给出飞书文档 URL/token，或说查看/读取/打开某个文档、提取文档内容、总结文档、生成/创建文档、追加/替换/删除/移动内容、调整排版、插入或下载文档图片/附件/素材/画板缩略图时使用。文档内容中出现嵌入电子表格、多维表格、需要将重要信息可视化为画板（含 SVG 画板）、引用或同步块时，也先用本 skill 读取和提取 token，再切到对...
  `lark-doc/`


## ☁️ Lark Drive

- **`lark-drive`** — 飞书云空间（云盘/云存储）：管理云空间（云盘/云存储）中的文件和文件夹。上传和下载文件、创建文件夹、复制/移动/删除文件、查看文件元数据、管理文档评论、管理文档权限、订阅用户评论变更事件、修改文件标题（docx、sheet、bitable、file、folder、wiki）；也负责把本地 Word/Markdown/Excel/CSV/PPTX 以及 Base 快照（.base）导入为飞书在线云文档（docx、sheet、bitable、slides）。当用户需要上传或下载文件、整理云空间...
  `lark-drive/`


## 🔔 Lark Event

- **`lark-event`** — Lark/Feishu real-time event listening / subscribing / consuming: stream events as NDJSON via `lark-cli event consume <EventKey>` (covers IM messages/reactions/chat changes, VC meeting ended, Minutes generated, etc.). Use for Lark bots, real-time m...
  `lark-event/`


## 💬 Lark IM

- **`lark-im`** — 飞书即时通讯：收发消息和管理群聊。发送和回复消息、搜索聊天记录、管理群聊成员、上传下载图片和文件（支持大文件分片下载）、管理表情回复、发送应用内/短信/电话加急。当用户需要发消息、查看或搜索聊天记录、下载聊天中的文件、查看群成员、搜索群、创建群聊或话题群、管理标记数据时使用。
  `lark-im/`


## 📧 Lark Mail

- **`lark-mail`** — 飞书邮箱 — draft, compose, send, reply, forward, read, and search emails; manage drafts, folders, labels, contacts, attachments, and mail rules. Use when user mentions 起草邮件, 写一封邮件, 拟邮件, 草稿, 发通知邮件, 发送邮件, 发邮件, 回复邮件, 转发邮件, 查看邮件, 看邮件, 读邮件, 搜索邮件, 查邮件, 收件箱,...
  `lark-mail/`


## 📝 Lark Markdown

- **`lark-markdown`** — 飞书 Markdown：查看、创建、上传、编辑和比较 Markdown 文件。当用户需要创建或编辑 Markdown 文件、读取、修改、局部 patch 或比较差异时使用。
  `lark-markdown/`


## 🎙️ Lark Minutes

- **`lark-minutes`** — 飞书妙记：妙记相关基本功能。1.查询妙记列表（按关键词/所有者/参与者/时间范围）；2.获取妙记基础信息（标题、封面、时长 等）；3.下载妙记音视频文件；4.获取妙记相关 AI 产物（总结、待办、章节）；5.上传音视频生成妙记，也支持将本地音视频文件转成纪要、逐字稿、文字稿、撰写文字等产物；6.更新妙记标题（重命名妙记）；7.替换妙记逐字稿中的说话人。遇到这类请求时，应优先使用本 skill。飞书妙记 URL 格式: http(s)://<host>/minutes/<minute-token>
  `lark-minutes/`


## 🎯 Lark OKR

- **`lark-okr`** — 飞书 OKR：管理目标与关键结果。查看和编辑 OKR 周期、目标（Objective）、关键结果（Key Result）、对齐关系、量化指标和进展记录。当用户需要查看或创建 OKR、管理目标和关键结果、查看对齐关系时使用。
  `lark-okr/`


## 🔍 Lark OpenAPI Explorer

- **`lark-openapi-explorer`** — 飞书/Lark 原生 OpenAPI 探索：从官方文档库中挖掘未经 CLI 封装的原生 OpenAPI 接口。当用户的需求无法被现有 lark-* skill 或 lark-cli 已注册命令满足，需要查找并调用原生飞书 OpenAPI 时使用。
  `lark-openapi-explorer/`


## 🔗 Lark Shared

- **`lark-shared`** — Use when first setting up lark-cli, running auth login, switching user/bot identity (--as), handling permission denied or scope errors, needing to update lark-cli, or seeing _notice in JSON output.
  `lark-shared/`


## 📊 Lark Sheets

- **`lark-sheets`** — 飞书电子表格：创建和操作电子表格。支持创建表格、创建/复制/删除/更新工作表、读写单元格、追加行数据、查找内容、导出文件。当用户需要创建电子表格、管理工作表、批量读写数据、在已知表格中查找内容、导出或下载表格时使用。若用户是想按名称或关键词搜索云空间（云盘/云存储）里的表格文件，请改用 lark-drive 的 drive +search 先定位资源。当用户给出 doubao.com 的 /sheets/ URL/token 时，也应直接使用本 skill，不要因为域名不是飞书而回退到 W...
  `lark-sheets/`


## 🛠️ Lark Skill Maker

- **`lark-skill-maker`** — 创建 lark-cli 的自定义 Skill。当用户需要把飞书 API 操作封装成可复用的 Skill（包装原子 API 或编排多步流程）时使用。
  `lark-skill-maker/`


## 📽️ Lark Slides

- **`lark-slides`** — 飞书幻灯片：创建和编辑幻灯片，接口通过 XML 协议通信。创建演示文稿、读取幻灯片内容、管理幻灯片页面（创建、删除、读取、局部替换）。当用户需要创建或编辑幻灯片、读取或修改单个页面时使用。当用户给出 doubao.com 的 /slides/ URL/token 时，也应直接使用本 skill，不要因为域名不是飞书而回退到 WebFetch；路由依据是 URL 路径模式和 token，而不是域名。
  `lark-slides/`


## ✅ Lark Task

- **`lark-task`** — 飞书任务：管理任务、清单和任务智能体。创建待办任务、查看和更新任务状态、拆分子任务、组织任务清单、分配协作成员、上传任务附件、注册或注销任务智能体、更新任务智能体的主页数据、写入智能体任务记录。当用户需要创建待办事项、查看任务列表、跟踪任务进度、管理项目清单或给他人分配任务、为任务上传附件文件、注册注销任务智能体、更新智能体主页数据、写入任务记录时使用。
  `lark-task/`


## 📹 Lark VC

- **`lark-vc`** — 飞书视频会议：搜索历史会议、查询会议纪要产物（总结、待办、章节、逐字稿）、查询会议参会人快照。1. 查询已经结束的会议数量或详情时使用本技能（如历史日期｜昨天｜上周｜今天已经开过的会议等场景），查询未开始的会议日程使用 lark-calendar 技能。2. 支持通过关键词、时间范围、组织者、参与者、会议室等筛选条件搜索会议。3. 获取或整理会议纪要、逐字稿、录制产物时使用本技能。4. 查询“谁参加过某会议”“参会人列表”等参会人快照信息用 vc meeting get --with-pa...
  `lark-vc/`


## 🤖 Lark VC Agent

- **`lark-vc-agent`** — 飞书视频会议：让机器人代当前用户加入/离开正在进行的会议，并读取会议期间的实时事件（参会人加入与离开、发言、聊天、屏幕共享等）。1. 用户提供 9 位会议号、要求代为入会或离会时使用 +meeting-join / +meeting-leave——会真实产生入会/离会记录。2. 会议进行中用户想知道“谁加入了”“谁离开了”“谁在发言”“有人共享屏幕吗”等会中动态时，机器人入会后用 +meeting-events 读取事件时间线。3. 典型场景：参会机器人、会中助手、代为旁听、代为参会。前提...
  `lark-vc-agent/`


## 🎨 Lark Whiteboard

- **`lark-whiteboard`** — >
  `lark-whiteboard/`


## 📚 Lark Wiki

- **`lark-wiki`** — 飞书知识库：管理知识空间、空间成员和文档节点。创建和查询知识空间、查看和管理空间成员、管理节点层级结构、在知识库中组织文档和快捷方式。当用户需要在知识库中查找或创建文档、浏览知识空间结构、查看或管理空间成员、移动或复制节点时使用。当用户给出 doubao.com 的 /wiki/ URL/token 时，也应直接使用本 skill，不要因为域名不是飞书而回退到 WebFetch；路由依据是 URL 路径模式和 token，而不是域名。
  `lark-wiki/`


## 📋 Meeting Summary

- **`lark-workflow-meeting-summary`** — 会议纪要整理工作流：汇总指定时间范围内的会议纪要并生成结构化报告。当用户需要整理会议纪要、生成会议周报、回顾一段时间内的会议内容时使用。
  `lark-workflow-meeting-summary/`


## 📊 Standup Report

- **`lark-workflow-standup-report`** — 日程待办摘要：编排 calendar +agenda 和 task +get-my-tasks，生成指定日期的日程与未完成任务摘要。适用于了解今天/明天/本周的安排。
  `lark-workflow-standup-report/`


## ⚡ Productivity

- **`cron-skill-recommendation`** — Automated cron job for Hermes Agent skill discovery, research, and reporting to Feishu multi-dimensional tables. Use when setting up or running scheduled skill curation/recommendation workflows.
  `productivity/cron-skill-recommendation/`


## 💻 Software Development

- **`embedded-lvgl-arm`** — Use when developing LVGL v9 UIs for ARM Linux embedded systems (RK3568, Buildroot, DRM/KMS). Covers cross-compilation, GUI Guider designer workflow, device tree, backlight, and init scripts.
  `software-development/embedded-lvgl-arm/`

- **`lvgl-embedded-linux`** — Develop LVGL v9 UI apps for embedded Linux (RK3568/Buildroot) with macOS SDL2 simulator. Use when building LVGL UI, porting to ARM boards, setting up cross-compilation, fixing SDL2 rendering issues on macOS, or configuring LVGL drivers (DRM/fbdev/...
  `software-development/lvgl-embedded-linux/`


---

## 🔄 Sync to Another Device

```bash
git clone git@github.com:Frankynwa/hermes-skills.git ~/.hermes/skills
```
On either device, after making changes:
```bash
cd ~/.hermes/skills
git add -A && git commit -m "update skills" && git push
git pull  # on the other device
```
