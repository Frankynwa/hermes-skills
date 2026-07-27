# GitHub 开源项目

## CBDB（中国历代人物传记资料库）相关

| 项目 | 说明 | 活跃度 | 用途 |
|------|------|--------|------|
| [cbdb_sqlite](https://github.com/cbdb-project/cbdb_sqlite) | CBDB SQLite 数据库 | ✅ 活跃 | **首选**：直接用 SQL 查询人物 |
| [cbdb-web](https://github.com/boan-anbo/cbdb-web) | CBDB 桌面/Web 应用 | ✅ 2025 | 可视化探索 |
| [biogref_CBDB](https://github.com/cbdb-project/biogref_CBDB) | CBDB 人物引用数据 | ✅ 活跃 | 官方数据同步 |
| [cbdb-json](https://github.com/dHumanities/cbdb-json) | CBDB JSON 格式 | ⚠️ 2020 | 轻量查询 |
| [CBDB_visual](https://github.com/queenieluo/CBDB_visual) | CBDB 家谱可视化 | ✅ 2026 | 家族关系图 |
| [dana-cbdb](https://github.com/beijingren/dana-cbdb) | CBDB 工具集 | ⚠️ 2014 | 辅助工具 |

## 数字人文项目

| 项目 | 说明 |
|------|------|
| [Digital-Humanities-101](https://github.com/XueyinJessica/Digital-Humanities-101) | 数字人文 Python 教程（中国历史） |
| [shuzirenwen](https://github.com/XueyinJessica/shuzirenwen) | 数字人文入门网站 |
| [printed-traces](https://github.com/CarlosYinn/printed-traces) | 中国移民儿童研究（1880-1885） |

## 已知但无 GitHub 的在线工具

| 工具 | 网址 | 说明 |
|------|------|------|
| MARKUS | dh.chinese-empires.eu/markus | 古籍半自动标注 |
| DocuSky | docusky.org.tw | 台湾大学古籍数据库 |
| CHGIS | chgis.fas.harvard.edu | 中国历史地理信息系统 |

## 快速开始：用 CBDB SQLite 查人物

```bash
# 1. 克隆数据库
git clone https://github.com/cbdb-project/cbdb_sqlite.git
cd cbdb_sqlite

# 2. 查询人物（示例：查周秉文）
sqlite3 cbdb.sqlite "SELECT c_name, c_birthyear, c_deathyear, c_index_addr_id FROM biog_main WHERE c_name LIKE '%周秉文%';"

# 3. 查科举信息
sqlite3 cbdb.sqlite "SELECT * FROM keju WHERE c_name LIKE '%周秉文%';"

# 4. 查官职
sqlite3 cbdb.sqlite "SELECT * FROM office WHERE c_name LIKE '%周秉文%';"
```
