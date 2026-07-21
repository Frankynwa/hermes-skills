# Daily Skill 推荐表格完整字段映射

## 表格信息

| 属性 | 值 |
|------|-----|
| Base Token | `JfJJbW0EaaukYqsUYA1cnlzondh` |
| Table ID | `tblyg5CbsoBoqgaX` |
| 身份 | `--as bot` |
| 表格链接 | https://my.feishu.cn/base/JfJJbW0EaaukYqsUYA1cnlzondh |

## 字段映射

| 序号 | 字段名 | 字段ID | 类型 | CellValue 写法 |
|------|--------|--------|------|---------------|
| 1 | Skill名称 | fld3HlyVs6 | text | 纯文本字符串 |
| 2 | 分类 | fldVxUfFsl | select | 选项名数组 `["分类名"]`（API返回和接受数组格式） |
| 3 | 评分 | fldxgvTaEy | number | 数字 1-5 |
| 4 | 日期 | fld08w0NXD | datetime | `"YYYY-MM-DD HH:mm:ss"` |
| 5 | 作者 | fldkJ8EOfh | text | 纯文本字符串 |
| 6 | 使用场景 | fldlM2Zgp6 | text | 纯文本字符串 |
| 7 | Skill链接 | fldZnnGOaD | text (url 样式) | URL 字符串 |
| 8 | 推荐理由 | fldQYhVgP2 | text | 纯文本字符串 |

## 分类选项（fldVxUfFsl 可选值）

| 选项名 | 颜色 |
|--------|------|
| 开发工具 | Blue |
| 创意设计 | Purple |
| 生产力 | Green |
| AI/ML | Orange |
| DevOps | Turquoise |
| 数据科学 | Carmine |
| 通信 | Wathet |
| 研究 | Yellow |
| 其他 | Gray |

## CellValue 关键规则

### datetime 字段
- 格式：`"YYYY-MM-DD HH:mm:ss"`
- 不要写相对时间（如"今天"、"昨天"）
- 不要写只有日期没有时间的值

### select 字段
- API 接受和返回数组格式：`["选项名"]`
- 写未知选项时平台可能自动新增（不推荐）
- 单选和多选都用数组格式

### number 字段
- 传 JSON number，不要传字符串
- 评分字段值为 1-5

### url 类型 text 字段
- 直接传 URL 字符串
- 飞书表格会按 URL 样式自动渲染为可点击链接
