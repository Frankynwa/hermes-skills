# 金融学论文验证模式

## 顶级期刊层级

- **T1 顶刊**：Journal of Finance (JF), Journal of Financial Economics (JFE), Review of Financial Studies (RFS), Journal of Political Economy (JPE), Econometrica
- **T2 权威**：Journal of Financial Markets (JFM), Journal of Business, Financial Analysts Journal
- **T3 综述**：Annual Review of Financial Economics, Journal of Economic Perspectives

## DOI 验证流程

1. OpenAlex 按精确标题搜索找到 DOI
2. Crossref 验证 DOI + 获取被引次数

```python
# Step 1: OpenAlex 按标题搜索
url = f"https://api.openalex.org/works?search={urllib.parse.quote(exact_title)}&per_page=1"
# 返回 doi 字段

# Step 2: Crossref 验证
url = f"https://api.crossref.org/works/{doi}"
# 返回 is-referenced-by-count（被引次数）
```

## 关键论文（已验证）

| 论文 | 期刊 | 被引 | DOI |
|------|------|------|-----|
| Frazzini & Lamont (2008) Dumb Money | JFE | 712 | 10.1016/j.jfineco.2007.07.001 |
| Coval & Stafford (2007) Asset Fire Sales | JFE | 1398 | 10.1016/j.jfineco.2006.09.007 |
| Lou & Polk (2022) Comomentum | RFS | 82 | 10.1093/rfs/hhab117 |
| Barber & Odean (2000) Trading Is Hazardous | JF | 2937 | 10.1111/0022-1082.00226 |
| Baker & Wurgler (2006) Investor Sentiment | JF | 6193 | 10.1111/j.1540-6261.2006.00885.x |
| Kaniel, Saar & Titman (2008) Individual Investors | JF | 976 | 10.1111/j.1540-6261.2008.01316.x |
| Berk & Green (2004) Rational Markets | JPE | 2177 | 10.1086/424739 |
| Wermers (1999) Mutual Fund Herding | JF | 1699 | 10.1111/0022-1082.00118 |
| Kacperczyk, Sialm & Zheng (2005) Industry Concentration | JF | 1169 | 10.1111/j.1540-6261.2005.00785.x |
| Cremers & Petajisto (2009) Active Share | RFS | 1585 | 10.1093/rfs/hhp057 |
| Brunnermeier & Nagel (2004) Hedge Funds & Tech Bubble | JF | 1156 | 10.1111/j.1540-6261.2004.00690.x |
| Ben-David et al. (2012) Hedge Fund Crisis | RFS | 349 | 10.1093/rfs/hhr114 |
| Amihud (2002) Illiquidity | JFM | 10434 | 10.1016/s1386-4181(01)00024-6 |

## 不要猜测 DOI

OpenAlex 的 DOI 猜测经常返回错误论文（如猜测 IET GTD 的连续编号返回无关论文）。必须通过搜索找到正确 DOI 后再验证。