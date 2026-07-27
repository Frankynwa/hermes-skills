---
name: odyssey-morning-card
description: 奥德赛晨间卡片系统——基于96篇论文的循证每日规划。脚本在 ~/scripts/odyssey.py，Web面板在 ~/projects/odyssey-dashboard/。飞书仅支持button+select_static（不支持input）。
---

# Odyssey 晨间卡片系统

## 核心设计原则（13条金线）

1. 早晨 7:00 推送（PFC 认知高峰 + 皮质醇觉醒反应）
2. 每日 ≤3 项核心意图（工作记忆 4±1 容量）
3. if-then 格式强制（元分析 d=0.65）
4. 障碍预判 + 应对计划（WOOP 心理对照）
5. 情绪检测先行 → 自适应降级
6. 过程目标为主（新手阶段）
7. "选择"而非"必须"的语言（SDT 自主性）
8. 跳过不归零（Lally 66天渐近曲线）
9. 格式一致性 + 保留主动决策（Graybiel 习惯回路）
10. 预期体验 > 打卡快感（Knutson 多巴胺预测误差）
11. 温暖简洁的中国化设计
12. 卡片 = 认知假体（Sweller 认知负荷 + 蔡格尼克效应）
13. 身份声明用名词（Bryan "be a voter" 效应 + DMN 自我一致性）

## 系统架构

```
飞书端（通知）          Web 端（交互）           数据层
cron 7:00 推送          Flask localhost:5100     state.json
  文本卡片               4步渐进式表单            morning_records
  ↓ 链接                 ↓ 保存                  ↓
  用户点开 → 浏览器     用户填写 → POST         晚间对话引用
```

## Flask Web 面板（方案 C，当前方向）

路径：`~/projects/odyssey-dashboard/`
- `app.py` — Flask 后端（~150 行），端口 5100
- `templates/index.html` — 单页前端，mobile-first

**4 步渐进式表单：**
1. 状态检查 + 昨日回顾（带入未完成 MIT）
2. 今日最重要的 3 件事（if-then 格式）
3. 障碍 & 应对 + 掌控感/愉悦感 + 习惯锚点
4. 时间框架 + 心理追踪 + 完成规划

启动：`cd ~/projects/odyssey-dashboard && python3 app.py`

**已验证** (2026-07-27)：Flask 3.1.0 + Python 3.x，端口 5100，四步UX全部可渲染。
注意：端口 5100 可能被其他 python 进程占用，启动前先 `lsof -i :5100` 检查并 kill。

### API 端点

| 方法 | 路径 | 用途 |
|------|------|------|
| GET | `/` | 渲染 index.html |
| GET | `/api/state?date=YYYY-MM-DD` | 当天记录 + 昨日MIT + 心理快照 + 连续低能量天数 |
| POST | `/api/state` | 保存（字段：date, state, mits, obstacle, cope_plan, mastery, pleasure, habit_anchor） |
| GET | `/api/history` | 最近30天记录摘要 |
| GET | `/api/psych` | 心理趋势（30天状态值 + psych_snapshot） |

### 数据同步验证

Web面板与 `odyssey.py` 共享 `~/.hermes/overnight/state.json`，`morning_records[date_str]` 存储每日记录。
POST提交后用 `cat ~/.hermes/overnight/state.json | jq '.morning_records["YYYY-MM-DD"]'` 验证写入。

⚠️ **浏览器自动化 pitfall**：Selenium/Playwright 点击 `<button onclick="nextStep()">` 有时不触发 onclick。用 `browser_console` 直接调用 `nextStep()` 绕过。实际用户手动点击无此问题。

## ⚠️ 设计铁律

1. **先对齐再动手**：任何涉及第三方 API 的设计，必须先验证约束再画 mockup。不要假设"有按钮就有输入框"。
2. **不要凭空画 mockup**：像论文筛选一样——"看起来应该支持"≠"实际支持"。用最小测试卡片验证后再写代码。
3. **不要和用户争**：用户说"我答过了"就接受，查找证据而不是争辩。

## UX 设计原则（来自 8 款竞品调研）

- **分步引导**：4 步渐进式，每步一个决策（参考 Any.do Moment）
- **Top 3 聚焦**：每日 ≤3 项 MIT（Cowan 工作记忆 4±1）
- **暖色调**：鼠尾草绿 + 陶土橙，晨间 PFC 敏感期（参考 SyncLife）
- **昨日滚存**：自动带入未完成 MIT，不惩罚（参考 TeuxDeux）
- **内联编辑**：不弹窗，保持空间连续性（参考 Things 3）
- **语言框架**：用"你可以…"不用"你必须…"（SDT 自主性）

详见 `references/ux-research-8-products.md`

## 脚本命令

| 命令 | 用途 |
|------|------|
| `python3 odyssey.py morning` | 生成纯文本晨间卡片（cron 推送） |
| `echo "回复" \| python3 odyssey.py parse-reply` | 解析用户文本回复到 state.json |
| `python3 odyssey.py evening` | 生成晚间对话问题 |
| Flask 面板 | `~/projects/odyssey-dashboard/app.py`，端口 5100 |

## ⚠️ 飞书交互卡片 API 限制（已踩坑验证）

### 飞书卡片不支持 input 元素

`div` 的 `extra` 字段只支持：`img` `button` `select_static` `select_person` `overflow` `date_picker` `picker_date` `picker_time` `picker_datetime`

错误：`div's extra must be one of the following elements` (ErrCode: 11310)

### value 字段必须是 dict

✅ `"value": {"odyssey_action": "state", "state": "1"}`
❌ `"value": json.dumps({"odyssey_action": "state", "state": "1"})`

错误：`expected typing.Dict[str, typing.Any] but was <class 'str'> at field: value`

### 飞书可用组件总结

| 组件 | 用途 | 限制 |
|------|------|------|
| `action` + `button` | 状态选择、提交、跳过 | value 必须 dict |
| `select_static` | 下拉选择（障碍类型） | value 必须 dict |
| `markdown` | 文本展示 | 无交互 |
| `hr` / `note` | 分隔 / 页脚 | — |

### 教训：实施前必须验证 API

不要假设"有按钮就有输入框"。飞书 API 文档是 SPA 渲染，curl 抓不到内容。最可靠的方式是**用 lark-cli 发一个最小测试卡片**验证。

## Gateway 集成

已修改 `gateway/platforms/feishu.py`：
- `_handle_odyssey_card_action()`：处理状态/下拉/跳过动作
- `_odyssey_response_card()`：构建替换卡片
- 需要重启 Gateway 后生效

## 研究文件

- `~/.hermes/overnight/odyssey-research.md`
- `~/.hermes/overnight/planning-templates.md`（v2 模板 + 理论回溯）
- `odyssey_round3_neuroscience.md`（52篇）
- `odyssey-competitive-analysis.md`（12款）