# 飞书 CLI 官方能力地图 & 进化方向

> 来源: https://open.feishu.cn/document/mcp_open_tools/overview-of-lark-agent-integration-capabilities
> 抓取时间: 2026-06-02

## 三大架构层

| 层 | 能力 | 形态 | 说明 |
|----|------|------|------|
| 凭据层 | 一键创建飞书应用 | Web 扫码 SDK (Node/Py/Java/Go) | 快速获取 App ID + App Secret，预置权限和事件订阅 |
| 交互层 | Channel SDK | SDK (Node/Py/Java/Go) | 群聊/单聊/文档评论收发消息，流式回复，卡片交互 |
| 执行层 | 飞书 CLI | CLI (`npx @larksuite/cli@latest install`) | 操作文档/日历/表格/邮件/任务等业务对象 |

## 17 个业务域能力

| 业务域 | 能力 |
|--------|------|
| 消息与群组 | 搜索消息和群聊、发消息、回复话题、管理成员与表情回应、收发图片文件 |
| 云文档 | 创建文档、读取内容、更新正文、插入图片附件、搜索云文档 |
| 云空间 | 上传下载文件、整理目录、导入导出文档、管理权限、处理评论 |
| 电子表格 | 创建表格、读写单元格、批量追加、查找替换、筛选视图、导出下载 |
| 多维表格 | 管理数据表、字段、记录、视图、表单、仪表盘、自动化与权限角色 |
| 日历 | 查日程、约会议、查忙闲、推荐时间、预定会议室、回复邀约 |
| 视频会议 | 搜索会议、获取纪要和逐字稿、关联日程文档 |
| 妙记 | 搜索妙记、下载音视频、获取总结待办章节 |
| 邮箱 | 搜索、读取、起草、发送、回复、转发、归档邮件，管理文件夹标签规则 |
| 任务 | 创建任务、更新状态、拆分子任务、管理清单和协作成员 |
| 知识库 | 查询空间、管理成员、管理节点和文档层级 |
| 通讯录 | 查询用户、搜索同事、查看部门 |
| 幻灯片 | 创建演示文稿、读取页面内容、增删幻灯片 |
| 画板 | 读取画板、导出图片、用 DSL/PlantUML/Mermaid 更新画板 |
| OKR | 查看周期、管理目标与关键结果、维护对齐关系和量化指标 |
| 审批 | 查询审批实例、处理审批任务 |
| 考勤 | 查询考勤打卡记录 |

## Channel SDK 关键能力（未被 lark-cli 完整覆盖）

- **流式回复** (`channel.stream()`) — 边推理边刷新卡片，类似 ChatGPT 体验
- **卡片交互回调** — 按钮/表单/下拉点击事件直接送到 Agent
- **文档评论 @bot** — 用户在文档里 @bot 提问，Agent 直接回复评论
- **内置安全策略** — 消息去重、防刷屏、会话串行化、单聊/群聊策略拦截

Channel SDK 不覆盖：Agent runtime、多用户隔离、Session/上下文持久化、凭据存储。

## 一键创建应用的预置权限清单

Bot 身份权限：
- `contact:contact.base:readonly` — 通讯录基本信息
- `im:chat:create/read/update` — 群管理
- `im:message:*` — 消息收发全系列（send, readonly, pins, reactions, update）
- `im:message.group_at_msg:readonly` / `im:message.p2p_msg:readonly` — @消息和私聊
- `im:resource` — 图片文件资源
- `im:chat.members:bot_access` — 机器人进/出群事件
- `docx:document:create/readonly/write_only` — 文档读写
- `docx:document.block:convert` — 文本转文档块
- `docs:document.comment:*` — 文档评论 CRUD
- `drive:drive.metadata:readonly` — 云空间元数据
- `cardkit:card:read/write` — 卡片读写
- `application:application:self_manage` — 应用自身管理
- `application:bot.menu:write` — 机器人菜单

User 身份权限：`offline_access`（持续访问已授权数据）

事件订阅（WebSocket 长连接）：
- `im.message.receive_v1` — 接收消息
- `im.message.reaction.created_v1` / `deleted_v1` — 表情回应
- `im.chat.member.bot.added_v1` / `deleted_v1` — 机器人进/出群
- `drive.notice.comment_add_v1` — 文档评论通知
- `card.action.trigger` — 卡片交互回调

## 官方 5 大场景案例

1. **会后待办一键清** — 妙记→提取待办→发文档/约会议/做调研。进阶：Wake Word 唤醒词。
2. **人机共创文档评审** — AI 起草→用户评论→AI 修改迭代；或用户写→AI review 评论。
3. **跨时区智能约会** — 拉群成员→查忙闲→考虑时区→推荐时间→建会。
4. **会议数据分析** — 拉日历→打标签→写多维表格→生成仪表盘。
5. **未读邮件智能分类** — 扫描未读→按优先级分类→摘要推送群聊→起草回复。

## Wake Word（唤醒词指令）

设置触发词（如"龙虾龙虾"），开会时随口说指令，会后 Agent 从妙记逐字稿中识别触发词、提取为最高优先级待办并自动执行。

实现路径：监听 lark-minutes 逐字稿 → 关键词匹配 → 提取指令 → 触发对应 skill。

## 许愿池

飞书 CLI 有官方许愿池，可提交新能力需求或 +1：
- 填表许愿: https://bytedance.larkoffice.com/share/base/form/shrcnFYECazRm9hPygXwLkEhmKf
- 投票表格: https://bytedance.larkoffice.com/base/Ebxvb6usfakMENs2GHIcL5Ern2f
