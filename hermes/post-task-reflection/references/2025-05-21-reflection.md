# 2025-05-21: 实习文件分析任务复盘

## 任务概述
分析用户 2025年6月底-8月初（维信诺/数之联实习期间）的所有电脑文件。

## 错误清单

### ❌ execute_code sandbox 无 pandas
- 现象: ModuleNotFoundError
- 浪费: 2 次调用
- 正确做法: Excel 读取一律用 terminal + 系统 python3

### ❌ 微信 Container 目录递归超时
- 现象: find/ls 反复 timeout (10-180s)
- 浪费: 约 5 次调用
- 正确做法: 只做顶层 ls，不递归。已知加密，应尽早告知用户

### ❌ .xlsx 文件引擎选择错误
- 现象: xlrd 对 .xlsx 报 Unsupported format
- 浪费: 3 次调用
- 正确做法: .xlsx 先试 openpyxl，失败试 xlrd，再失败跳过

### ❌ 重复尝试已知会失败的操作
- 浪费: 3 次调用
- 正确做法: 同类错误 2 次后立即换策略

## 成功做法

### ✅ vision_analyze 分析截屏 (12张全部成功)
- 信息量极大：MES平台、云桌面、任务分配、屏幕测试
- 结论: 截屏分析是文件考古最高效手段

### ✅ xlrd 直接读取大型 .xls 文件
- 比 pandas 更稳定，特别对大文件

### ✅ sqlite3 读取 iFLYAssistant 数据库
- translator.db 包含翻译历史，揭示 AI/ML 工作内容

## 效率: 35 calls, 22 有效, 13 浪费 (37%)

## 改进规则
1. 超时错误 2 次后立即放弃该路径
2. execute_code 需要第三方包时直接用 terminal
3. 微信数据一开始就告知限制
4. 截屏分析优先于文件内容分析
