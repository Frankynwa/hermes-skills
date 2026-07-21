---
name: graduate-school-research
description: "Research and evaluate graduate school options for international students, especially those with low GPA or non-traditional backgrounds. Covers 15+ countries, professor lookup, GPA policy analysis, MPhil vs MSc distinction, HK/mainland joint-venture campuses, and application strategy."
tags: [graduate-school, admissions, GPA, MPhil, PhD, professor-research, application-strategy, international-students, study-abroad, university-research]
triggers: ["graduate school", "grad school", "master application", "PhD application", "where can I apply", "GPA too low", "professor outreach", "套磁", "研究生申请", "留学", "CityU-DG", "HKUST-GZ", "港城东莞", "港科大广州"]
---

# Graduate School Research & Application Strategy

## When to Use
- User asks "where can I apply with my GPA?"
- User needs professor background research for potential supervisors
- User asks about MSc vs MPhil vs PhD admission differences
- User needs school-by-school comparison for graduate applications
- User asks about GPA cutoff flexibility or professor discretion

## User Context (CRITICAL)
- **Mainland Chinese student** at MUST (澳门科技大学), NOT a Macau local
- BSAI (人工智能) major, student ID: 1230027498
- GPA: <2.5/4.0 (self-reported, significant constraint)
- Strong project portfolio: AlphaSeeker (quantitative finance), psych-nlp (psychological NLP engine), Python/AI skills
- Target direction: AI + quantitative finance
- No GRE/TOEFL yet, limited preparation time
- Has professor 王黎 (Li Wang) as potential research supervisor at MUST

## Core Framework: Taught vs Research Degrees

### The #1 Distinction Most Students Miss
**Taught Master's (MSc/MEng)** = hard GPA cutoffs, professor has NO admission discretion, centralized filtering by admissions office. Below minimum = auto-reject.

**Research Master's (MPhil) / PhD** = professor has significant discretion, GPA is "suggested minimum" not hard cutoff, professor can nominate students below stated threshold through formal exception mechanisms.

**This distinction is the key to the entire strategy for low-GPA students.**

### Professor Discretion Mechanisms (by region)
| Region | Taught MSc | Research MPhil/PhD |
|--------|-----------|-------------------|
| HK (all 5 universities) | Hard cutoff | ✅ Formal exception policy, professor nomination |
| HK Mainland campuses (CityU-DG, HKUST-GZ, CUHK-SZ) | Moderate | ✅ High discretion (newer = more flexible) |
| Australia | Moderate (some holistic) | ✅ Supervisor agreement = key factor |
| Singapore (NUS/NTU) | Hard cutoff | 🟡 Limited, still competitive |
| Singapore (SMU/SUTD) | Moderate | 🟡 More holistic |
| Canada (top: UofT/UBC/Waterloo) | Hard cutoff (SGS floor ~3.0) | 🟡 "Special case" admission possible |
| Canada (mid: UdeM/McMaster/UAlberta) | Moderate | ✅ Professor can petition |
| Canada (lower tier) | Flexible | ✅ Professor has strong discretion |
| Europe (ETH/EPFL/TUM) | Hard cutoff | N/A (MSc only, PhD needs MSc first) |
| Europe (Nordic: Finland/Norway) | Holistic assessment | ✅ Portfolio/project valued |
| Europe (Belgium: KU Leuven) | Moderate holistic | ✅ Research group positions |

## Step-by-Step Research Workflow

### Step 1: Professor Background Lookup
For each potential supervisor, gather:
1. **OpenAlex API**: `curl "https://api.openalex.org/authors/{id}"` — get works_count, cited_by_count, h_index, topics
2. **OpenAlex works**: `curl "https://api.openalex.org/works?filter=author.id:{id}&sort=publication_date:desc"` — get all papers
3. **ORCID**: `curl "https://pub.orcid.org/v3.0/{orcid}/person" -H "Accept: application/json"` — verified identity
4. **MUST Scholar DB** (if MUST professor): `https://scholar.must.edu.mo/scholar/{email_or_id}` — internal profile
5. **Google Scholar**: search for recent citations and co-author network

Key metrics to report:
- h-index and total citations
- Recent publication trend (active vs dormant)
- Research topic alignment with user's interests
- Supervision capacity (new professor = more eager for students but less established)

### Step 2: GPA Policy Analysis Per School
For each target school, determine:
1. **University-level minimum** (set by Graduate School/Senate) — this is the HARD floor
2. **Departmental target** (set by department) — this is a SOFT guideline
3. **Professor override mechanism** — does a formal exception process exist?
4. **New campus bonus** — newer institutions have more flexible standards

### Step 3: School Categorization
Categorize into tiers:
- **Tier 1 (Apply)**: Realistic chances with current profile
- **Tier 2 (Reach)**: Possible with strong professor support
- **Tier 3 (Long shot)**: Very difficult, only if exceptional other factors
- **Tier 4 (Skip)**: Don't waste application fees

### Step 4: Application Timeline
- **Now**: Professor outreach (套磁) — don't wait for grades
- **Semester**: Retake courses to improve GPA
- **Before deadlines**: IELTS/TOEFL (6.5 target for most programs)
- **After grades**: Formal application submission

## Country-by-Country Quick Reference (from grad-school-research)

### 🇭🇰 Hong Kong (including GBA campuses)
- **Key schools:** CityU-DG (QS 52), HKUST-GZ (QS 60), CUHK-SZ (QS 47)
- **CityU-DG specifics:** 10 MSc programs including AI, CS, Data Science. Accepts CET-6 425+. No explicit GPA minimum on website. Degree = CityU Hong Kong certificate. 2-year IANG work visa after graduation. **Best option for mainland Chinese students with low GPA.**
- **HKUST-GZ:** Primarily research (MPhil/PhD). No explicit GPA minimum. IELTS 6.5 required. Has Financial Technology MPhil/PhD (great for quant). Information Hub has AI, Data Science programs.
- **Professor discretion:** HIGH for research programs at all HK schools. CUHK has the most explicit policy language allowing exceptions.

### 🇦🇺 Australia
- **Key schools:** Monash (QS 37), Adelaide (QS 82), UNSW (QS 19), Melbourne (QS 13)
- **GPA conversion:** 2.5/4.0 ≈ 62.5% Australian WAM
- **Monash:** WAM 60% minimum for many programs. Master of AI available. ~AUD $46-49k/year tuition.
- **Adelaide:** Regional area benefits — extra 1yr on 485 visa (3yr total), +5 immigration points, state nomination.
- **Work visa:** 2yr 485 for coursework, 3yr for research. 485 fee increased to AUD $4,600 (2026). Age limit reduced to 35.

### 🇬🇧 United Kingdom
- **Key concept:** GPA 2.5/4.0 ≈ UK 2:2 (Lower Second Class)
- **Schools accepting 2:2 for CS/AI:** Swansea, Brunel, Aberdeen, Heriot-Watt, Strathclyde, City University London
- **Duration:** 1 year (shortest among major destinations)
- **Work visa:** 2-year Graduate Route

### 🇮🇹 Italy
- **Key schools:** Politecnico di Milano (QS 111), University of Trento (QS ~335)
- **Tuition:** €0-4,000/year (income-based, ISEE system)

### 🇳🇴 Norway
- **Key school:** NTNU (QS 264)
- **Tuition for non-EU:** NOK 205,600/year (verified 2026). **NOT free for non-EU students** (changed ~2023).

### 🇩🇪 Germany
- **Key schools:** Saarland University (QS ~447, AI research hub), Stuttgart (QS ~285)
- **Tuition:** €0-1,500/semester at most public universities

### 🇧🇪 Belgium
- **Key schools:** KU Leuven (QS 63), Ghent (QS ~150), VUB (QS ~200)
- **Tuition:** €1,000-6,000/year (needs verification)

### 🇳🇱 Netherlands
- **Key schools:** TU Delft (QS 47), TU Eindhoven (QS ~125), Wageningen (QS ~151)
- **Tuition:** €14,000-22,000/year for non-EU

### 🇳🇿 New Zealand
- **Key schools:** Canterbury (QS ~256), Otago (QS ~214), Auckland (QS ~68)
- **Work visa:** 3-year post-study work visa

### 🇨🇦 Canada
- **Key insight:** University-level minimum is typically B (3.0) — hard floor at most schools
- **Professor discretion:** Exists for MSc/PhD, especially at UdeM, McMaster, UAlberta

### 🇨🇳 中外合办 (Chinese-Foreign Cooperative)
- **UIC (北师港浸大):** QS ~252, accepts CET-6 430+, tuition ¥8-10万/yr
- **XJTLU (西交利物浦):** QS ~176, accepts CET-6 450+, tuition ¥9万/yr
- **UNNC (宁波诺丁汉):** QS ~108, CET-6 450+, tuition ¥10万/yr

## HK & Mainland China Joint-Venture Campus Profiles (from graduate-admissions-hk-mainland)

### CityU Dongguan (港城东莞) — DETAILED
- Official website: https://pga.cityu-dg.edu.cn/
- **10 MSc programs** (all taught): AI, Computer Science, Data Science, Business Analytics, BIS, EEE, Engineering Management, Materials, BME, Innovation
- **No explicit GPA minimum stated** on official FAQ
- **CET-6 425 accepted** (no IELTS needed!)
- Degree: CityU Hong Kong master's degree certificate
- Graduates get 2-year Hong Kong IANG work visa
- Cross-major applications allowed
- Contact: admissions@cityu-dg.edu.cn, 0769-21183030

### HKUST Guangzhou (港科大广州) — DETAILED
- Official website: https://fytgs.hkust-gz.edu.cn/
- **Mostly research degrees** (MPhil/PhD) — good for low GPA
- Programs by Hub:
  - Information Hub: **AI**, Data Science, Data-Centric AI Tech (**MSc!**), IoT, Computational Media
  - Society Hub: **Financial Technology** (MPhil/PhD), Carbon Neutrality
  - Systems Hub: Robotics, Smart Manufacturing, Intelligent Transportation
  - Function Hub: Advanced Materials, Microelectronics
- No explicit GPA minimum in general requirements
- English: IELTS 6.5 (all sub 5.5) / TOEFL 80
- Degree: HKUST Hong Kong degree

### GBA University (大湾区大学)
- Website: https://www.gbu.edu.cn/
- Established December 2025 in Dongguan (very new)
- President: 田刚 (Tian Gang), CAS academician, PKU professor
- **Joint-training model** — degrees from partner universities (PKU, HITSZ, SYSU, SUSTech)

### Professor Override Mechanisms (HK Schools)
All major HK universities have formal exception pathways for research degrees:
- **HKUST**: Professor submits nomination → department approves → Graduate School final check
- **CUHK**: Explicitly states candidates below minimum may be admitted "on recommendation of Graduate Division with Graduate Council approval"
- **CityU**: Supervisor nomination system
- **PolyU**: Pre-admission system where professors identify candidates

**New campuses (CityU-DG, HKUST-GZ) have MORE professor discretion** because they're still building enrollment.

### English Test Requirements Matrix

| Test | CityU-DG | HKUST-GZ | Most HK | Australia |
|------|----------|----------|---------|-----------|
| CET-6 | **425 ✅** | ❌ | ❌ | ❌ |
| IELTS | 6.0 | 6.5 | 6.5 | 6.5 |
| TOEFL | 79 | 80 | 80 | 79-90 |

**CET-6 advantage:** CityU-DG is the only HK-quality school accepting CET-6 for mainland students.

## Website Navigation Techniques (from graduate-admissions-hk-mainland)
Many Chinese university sites are heavily JS-rendered and curl cannot extract content. Techniques:
- **CityU-DG**: Main site (cityu-dg.edu.cn) is JS-only. Use **pga.cityu-dg.edu.cn** (graduate portal) which renders better.
- **HKUST-GZ**: **fytgs.hkust-gz.edu.cn** renders well in browser.
- **OpenAlex API**: `curl "https://api.openalex.org/authors/{id}"` for professor profiles
- **ORCID API**: `curl "https://pub.orcid.org/v3.0/{orcid}/person" -H "Accept: application/json"`

## Formatting Lessons (from user feedback via grad-school-research)
- User complained tables disappeared in Feishu — keep tables to 4-5 columns max
- Break long comparisons into multiple shorter messages or sections
- Use bold headers and bullet points for scannability
- Don't put 8+ tables in one message — Feishu card rendering fails on complex messages
- When user asks for "deep dive" on specific schools, give focused detail on those schools only
- Don't re-emit the entire global comparison every time — user finds it repetitive

## Pitfalls

### ❌ Common Mistakes
1. **Only applying to taught MSc** — for low-GPA students, research degrees (MPhil/PhD) are ALWAYS better because professor has discretion
2. **Waiting for grades before contacting professors** — start 套磁 immediately, professors don't ask for transcripts in initial emails
3. **Mentioning GPA in professor emails** — showcase projects and skills, not grades
4. **Group-sending template emails** — each email must reference specific papers/projects of that professor
5. **Assuming mainland campus = easier** — CUHK-SZ is now very competitive; CityU-DG and HKUST-GZ are the flexible ones
6. **Confusing MPhil with MSc** — MPhil is research-based, professor-selected; MSc is coursework-based, committee-selected
7. **Ignoring self-funded options** — some schools (especially Canada, Australia) have lower GPA thresholds for self-funded students
8. **Only looking at English-speaking countries** — Italy (€3.5k/yr), Belgium (€3.9k/yr), Germany (free) have much lower tuition AND more flexible GPA conversion (Italian 90/110 ≈ GPA 2.5)
9. **Forgetting UK 2:2 accepting schools** — Swansea, Brunel, Aberdeen, Heriot-Watt, Strathclyde all explicitly accept 2:2 for CS/AI/Data Science, and UK 1-year master's is cheaper total than 2-year programs elsewhere
10. **Assuming Norway is free** — NTNU and other Norwegian universities started charging non-EU students tuition from autumn 2023 (~NOK 150,000–200,000/year ≈ €13,000–17,500). Norway is no longer a budget option.
11. **Assuming CET-6 works outside Hong Kong mainland campuses** — CET-6 is only accepted by CityU-DG and some CUHK-SZ programs. European, Australian, and most HK universities require IELTS/TOEFL. No exceptions.

### ✅ Key Strategies
1. **Lead with projects, not grades** — AlphaSeeker, psych-nlp, GitHub repos are more persuasive than a transcript
2. **Target new campuses** — CityU-DG (2024), HKUST-GZ (2022) need students, professors have more discretion
3. **Research MPhil everywhere** — even if the school doesn't prominently advertise it, ask if research degrees exist
4. **Dual track: research degree + industry** — research builds credentials, internship builds practical experience
5. **IELTS 6.5 is the universal gate** — almost all programs require this, get it first

### Reference Data

### Global School Options (GPA ~2.5)
See `references/global-school-options-gpa25.md` — comprehensive list of 30+ schools across UK, Italy, Norway, Belgium, Netherlands, Germany, New Zealand, Australia, Canada, Switzerland, Hong Kong, and mainland China joint-venture campuses. Includes tuition, GPA requirements, IELTS scores, and feasibility assessment.

### School-by-School Quick Reference
See `references/school-gpa-policies.md` for detailed per-school analysis.

### Professor Research Template
See `references/professor-research-template.md` for the email template and research checklist.

### User Profile (MUST Student)
See `references/user-profile-2026.md` for the specific student profile this skill was developed around.

### Verified Admission Data (multiple sources)
- `references/cityu-dg-official.md` — 港城东莞: 10 MSc programs, no GPA minimum, CET-6 accepted, CityU HK degree, IANG visa
- `references/hkust-gz-official.md` — 港科大广州: MPhil/PhD + MSc programs, no GPA minimum, IELTS 6.5 required, HKUST degree
- `references/verified-admission-data-2026-07.md` — Cross-school verified data: CityU-DG, HKUST-GZ, Trento, PoliMi, Saarland, NTNU (NOT free since 2023), Adelaide
- `references/verified-data-2026.md` — Additional verified data from earlier research sessions
- `references/hk-mainland-schools-2026.md` — HK and mainland China joint-venture campus profiles

### Website Navigation Techniques
Many Chinese university sites are heavily JS-rendered and curl cannot extract content. Techniques:
- **CityU-DG**: Main site (cityu-dg.edu.cn) is JS-only. Use **pga.cityu-dg.edu.cn** (graduate portal) which renders better. FAQ page requires JS console clicks on accordion tabs.
- **HKUST-GZ**: **fytgs.hkust-gz.edu.cn** renders well in browser. Use standard browser navigation.
- **OpenAlex API**: `curl "https://api.openalex.org/authors/{id}"` for professor profiles, `curl "https://api.openalex.org/works?filter=author.id:{id}"` for papers
- **ORCID API**: `curl "https://pub.orcid.org/v3.0/{orcid}/person" -H "Accept: application/json"`

## Special Notes for MUST Students
- MUST is a recognized institution but carries limited weight in mainland/HK admissions
- MUST students are "international" applicants for HK programs (different pool than mainland gaokao students)
- MUST's partnership network may include exchange/articulation agreements — check with academic affairs
- Professor 王黎 (Li Wang) at MUST: Financial Statistics, Stochastic Volatility, ORCID 0000-0001-8565-9477, h-index 1, only 2 papers — new professor, limited recommendation weight but aligned with quantitative finance direction
- BSAI internship: 320 hours, July 14 confirmation deadline. See `references/must-bsai-internship.md`

## Application Strategy Template (Low-GPA Student)

### Recommended Application Mix (8-10 schools)
1. **Primary target**: CityU-DG (cheap, CET-6, HK degree, IANG visa)
2. **Secondary target**: Italy (Trento/PoliMi — extremely cheap, GPA conversion works)
3. **Tertiary**: Belgium (VUB/Ghent — no hard GPA cutoff, very cheap)
4. **Safety**: Belgium (VUB/Ghent — no hard GPA cutoff, cheap) or Germany (Saarland — free but GPA conversion may be barrier)
5. **Reach**: HKUST-GZ MPhil (professor discretion), Milan理工 (QS 111)
6. **Backup**: Australia (Monash/Adelaide — expensive but stable)
7. **Last resort**: MUST home university

### Decision Framework
- **Cheapest path**: CityU-DG or Italy (€3.5k/yr) or Belgium (€3.9k/yr) or Germany (free tuition, ~€300/semester fees)
- **Best ranking**: Monash (QS 37) or CityU-DG (QS 52 via CityU)
- **Easiest immigration**: Australia (Adelaide regional +3yr visa) or NZ (3yr visa)
- **Best for quant/finance**: CityU-DG (Hong Kong financial hub) or HKUST-GZ FinTech
- **Fastest**: UK 1-year programs or CityU-DG 1-1.5yr

### Action Items (Priority Order)
1. Confirm CET-6 score ≥425 (for CityU-DG)
2. Register for IELTS (for all other schools)
3. Start professor outreach emails (for HKUST-GZ, European research programs)
4. Prepare CV and personal statement
5. Secure recommendation letters from research supervisor
6. Submit CityU-DG application (deadline: July 31, rolling admission, apply ASAP)

## Pitfall: PDF Document Extraction
MUST and HK universities distribute admission/internship info as PDFs (often Chinese). Extraction workflow:
1. Install pdfplumber: `pip install pdfplumber -q`
2. Use `pdfplumber.open(path)` with `page.extract_text()` for each page
3. For scanned PDFs, use pytesseract + pdf2image
4. Note: pdfplumber may not be available in execute_code sandbox — use terminal with `python3` directly
