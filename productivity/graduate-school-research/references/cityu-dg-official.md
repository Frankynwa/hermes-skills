# 港城东莞 (CityU-DG) — Official Admission Data

Source: pga.cityu-dg.edu.cn (official graduate admissions portal), accessed July 2026

## Programs (10 MSc programs, all taught/coursework)

| # | Program (CN) | Program (EN) | Relevant for |
|---|---|---|---|
| 1 | 人工智能 | Artificial Intelligence | ✅ AI major |
| 2 | 计算机科学 | Computer Science | ✅ AI major |
| 3 | 数据科学 | Data Science | ✅ AI/quant |
| 4 | 商业及数据分析 | Business and Data Analytics | ✅ Quant finance |
| 5 | 商务资讯系统 | Business Information Systems | 🟡 |
| 6 | 电机与电子工程学 | Electrical & Electronic Eng | |
| 7 | 工程管理学 | Engineering Management | |
| 8 | 材料工程及纳米科技 | Materials Eng & Nanotech | |
| 9 | 生物医学工程 | Biomedical Engineering | |
| 10 | 创新新业 | Innovation & Entrepreneurship | |

## Admission Requirements (FAQ page, verbatim)

### Academic
> "持有获认可的内地、港澳台或海外大学所颁授的学士学位；或持有其他获大学承认的同等学历。"
> "应届毕业本科生如能在开学前取得所需学历资格，亦可提交申请。"

**⚠️ NO GPA MINIMUM STATED.** Only requires a recognized bachelor's degree.

### English Language
- **CET-6: 425分/合格** ← easiest option for mainland students
- TOEFL: 550 (paper) / 79 (iBT) — institution code D693
- IELTS (Academic): 6.0 overall
- Exempt if bachelor's was English-medium instruction
- TOEFL/IELTS scores valid for 2 years

### Other
- Recommendation letters required ("需提交相关推荐证明")
- Cross-major application allowed ("允许跨专业申请")
- Teaching language: English primary, some courses in Mandarin

## Degree & Post-Graduation Benefits
- **Degree awarded**: 香港城市大学硕士学位证书 (CityU Hong Kong Master's degree — SAME as HK campus)
- **IANG visa**: Graduates get 2-year Hong Kong IANG work visa
- 80% faculty from CityU HK, 70% from 35 countries/regions

## Campus Info
- Location: 松山湖, Dongguan, Guangdong
- Opened: September 2024
- First graduation: 2026 (already held)
- Contact: admissions@cityu-dg.edu.cn, 0769-21183030/3033

## Key Takeaways for Low-GPA Applicants
1. No stated GPA minimum — apply and let holistic review work
2. CET-6 425 is enough — no need for IELTS if you have CET-6
3. New campus (2024) still building enrollment — more flexible
4. Same CityU HK degree as the Hong Kong campus
5. Cross-major allowed — no restriction on undergraduate major

## Website Navigation Notes
- Main site (cityu-dg.edu.cn) is heavily JS-rendered, curl cannot extract content
- Graduate portal: **pga.cityu-dg.edu.cn** — works better with browser
- FAQ page: pga.cityu-dg.edu.cn/faq — use JS console to expand accordion tabs:
  ```javascript
  document.querySelectorAll('[role="tab"]')[N].click(); // N=3 for admission req
  document.querySelectorAll('[role="tabpanel"]')[N].textContent; // read content
  ```
- Individual program pages may not have separate URLs; content is on the main portal page
