# 晨间规划系统 — 8 款竞品 UX 模式分析

> 调研对象：Structured, TeuxDeux, Any.do Moment, Todoist, Things 3, Notion 模板, Reflect.app, Motion/Morgen

## 核心发现

### 推荐模式

| 模式 | 来源 | 实现方式 |
|------|------|---------|
| 分步引导 | Any.do Moment | 每步一个决策 + 进度条 |
| Top 3 聚焦 | Notion/TeuxDeux | 限制 MIT 为 3 项 |
| 昨日滚存 | TeuxDeux/Any.do | 自动带入未完成任务 |
| 内联编辑 | Things 3 | 不弹窗，卡片内展开 |
| Quick Add | Todoist | 单输入框 + Enter 即添加 |
| 暖色调 | SyncLife | 鼠尾草绿 #7E8F7A + 陶土橙 #C38A72 |
| 语音输入 | Any.do/Reflect | Web Speech API 可选按钮 |
| 微动效 | Things 3 | CSS transition 提升品质感 |

### 反模式（必须避免）

1. 一次展示太多输入框 → 用户不知从何下手 → 分步展示
2. 每次操作确认弹窗 → 打断心流 → 内联操作 + 撤销机制
3. 强制精确时间规划 → 增加焦虑 → 可选的简化时间轴
4. 忘记移动端适配 → 按钮太小 → 最小 44px 触摸目标
5. 冷冰冰的 UI → 晨间不适合冷色调 → 暖色调 + 友好文案
6. 没有空状态设计 → 新用户迷茫 → 预填充示例 + 引导文案

## 产品分析要点

### Structured
- 纵向时间轴 + "现在"指示线
- 模板系统减少重复输入
- 任务自动滚存

### TeuxDeux
- 极简双列布局（5 工作日 + Someday）
- 点击空白直接输入（inline editing）
- 未完成自动滚到明天

### Any.do Moment
- 全屏沉浸式分步引导
- 每步一张卡片，聚焦一个决策
- 语音输入作为一等公民

### Todoist
- 顶部固定 Quick Add 输入框
- 自然语言解析（@项目 #标签 p1 优先级）
- 零模态输入

### Things 3
- 内联展开面板（不跳转）
- "随时"任务池 → 拖拽到"今天"
- 弹性动画提升手感

### Notion 模板
- Top 3 优先级 + 待办清单 + 时间轴
- 模块化单页布局
- 数据库多视图切换

### Reflect.app
- 规划 + 日记合并在同一每日笔记
- 双向链接自动关联
- 连续天数热力图激励

### Motion/Morgen
- AI 自动排程 vs 手动时间阻塞
- 辅助决策 ≠ 替代决策
