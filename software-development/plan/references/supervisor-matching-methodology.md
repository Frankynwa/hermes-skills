# 学术导师匹配方法论

> 此文件记录在 MUST（澳门科技大学）量化方向导师搜寻中形成的通用方法论。

## 数据源选择

| 数据源 | 中国教授覆盖率 | 原因 |
|--------|--------------|------|
| OpenAlex（直接名字搜索） | ~5% | 中文名消歧差 |
| **OpenAlex（机构优先搜索）** | **30-60%** | 先拉机构全部作者，再本地匹配 |
| Semantic Scholar | ~10% | 机构信息缺失，不索引中文名 |
| **大学官网爬取** | **100%** | 教授自维护、包含研究方向和精选论文 |

**最佳策略：官网爬取（100%基础数据）+ OpenAlex机构优先搜索（学术指标补充）。**

### OpenAlex 机构优先搜索（v3 方法，2026-06验证）

直接用中文名搜 OpenAlex 命中率极低（3/62=5%）。改进方法：

1. 用 ROR ID 拉取该机构**全部作者**（一次批量请求，~3000人）
2. 在本地做名字匹配（5级策略：英文名精确→模糊→中文名→姓氏拼音→API fallback）
3. 命中率从 5% 提升到 30%+

```python
# 核心代码模式
url = f"{OPENALEX_BASE}/authors?filter=last_known_institutions.ror:{ROR_ID}&per_page=200&cursor={cursor}"
# 缓存所有结果，然后本地匹配
```

**注意：** OpenAlex 限速约 10 req/s（未认证），批量拉取时要 100-150ms 延迟。被 429 后不要重试，等 15-30 分钟。

## 方法：爬取 + 论文标题关键词匹配

### Step 1: 爬取教授个人页面
- 获取：姓名、职称、邮箱、研究方向、论文列表、科研经费
- 注意：不同教授的页面 HTML 结构可能不同，section 标题可能有变体

### Step 2: 搜索论文标题中的关键词
- 一级关键词（直接量化金融）：algorithmic trading, stock prediction, portfolio optimization, option pricing, volatility, financial time series
- 二级关键词（方法相关）：reinforcement learning, bandit, online learning, forecasting, prediction
- 关键词列表需要包含专业的学术术语：semimartingale, microstructure noise, stochastic volatility, realized Laplace transform 等

### Step 3: 交叉验证
- 研究方向描述 + 论文标题 + 科研经费 = 三维确认
- 如果论文标题匹配但研究方向描述不符 → 可能是方法迁移（如网络领域的 bandit 算法可迁移到量化金融）
- 如果研究方向匹配但论文列表为空 → 爬虫可能有 bug（参见下文）

## 爬虫 Bug 模式：Section Header 变体

大学官网个人页面中，同一内容的 section 标题可能因教授而异：
- `Academic Publication (selected)` vs `Academic Publication`
- `Research Grants` 可能完全不被索引

**处理方法**：
1. 把所有已知变体加入 SECTION_HEADERS 列表
2. 在结果解析时，对变体做 OR 匹配：
   ```python
   if 'Academic Publication (selected)' in sections:
       pubs_raw = sections['Academic Publication (selected)']
   elif 'Academic Publication' in sections:
       pubs_raw = sections['Academic Publication']
   ```
3. 爬完后验证：检查哪些教授论文数为 0，手动核对其个人页面
