# MUST 2026/2027 FYP Advisor Profiles — Quantitative/RL/Finance Focus

Updated: 2026-06-16. Data from OpenAlex, MUST FIE faculty page, and `must-prof-eval` project (quant_supervisor_ranking_v4).

## 盧曉平 (Xiaoping Lu)

- **Title:** 課程主任/教授 (Program Director / Professor)
- **Email:** xplu@must.edu.mo
- **Research:** Machine Learning (DL, RL), Data Science, High Performance Computing, Inverse Problems
- **FYP Topics:** FYP-2026-006 (Voice-Interactive Robotic Manipulators), FYP-2026-096 (RL for Visual Game Control)
- **OpenAlex:** Profile A5090615044 is MERGED with same-name authors from chemistry/biology/materials. Only papers matching RL/trading/robotics belong to this professor. Separate profile A5133460504 (Xiao-Ping Lu) has 1 work, 0 citations — likely incomplete.
- **Key Publications (verified):**
  - "A multi-agent reinforcement learning framework for optimizing financial trading strategies based on TimesNet" (2023, **67 citations**)
  - "DADE-DQN: Dual Action and Dual Environment DQN for Enhancing Stock Trading Strategy" (2023, with Yuling Huang)
  - "Enhancing trading strategies by combining incremental RL and self-supervised prediction" (2025, 7 citations)
  - "A combined Adaptive Gaussian STFT and Mamba framework for stock prediction" (2025, 4 citations)
  - "Stock Trading Strategy Based on Multi-Scale DRL and Price Movement Prediction" (2025, 1 citation)
- **must-prof-eval rank:** #20, score 5.78 (low because scoring weights direction-match over raw output)
- **Assessment:** Strongest MUST faculty for RL + quantitative trading. Professor rank + course director = established researcher. Low eval score is a scoring-system artifact, not a quality signal.

## 王黎 (Wang Li)

- **Title:** 助理教授 (Assistant Professor, 2019–present); previously Lecturer at BNU Zhuhai (2018–2019)
- **Email:** liwang-fi@must.edu.mo
- **Education:** PhD Statistics, University of Macau (2018); MSc Financial Mathematics, University of Macau (2014); BSc Mathematics, Jilin University (2011)
- **Research:** Statistics for Stochastic Processes, Financial Statistics, Econometric Mathematics
- **Teaching:** Time Series Analysis (MSc, 2019–2024), Calculus III, Linear Algebra, Discrete Mathematics
- **Funding:** MOP 100,000 (1 grant)
- **FYP Topics:** FYP-2026-024 (Factor-GARCH + DL for Portfolio Optimization), FYP-2026-108 (DL Dynamic Correlation for Multi-Asset Risk Management)
- **OpenAlex:** A5029511797 (Li Wang). Only 2 works indexed, 4 citations. Topics: Financial Risk and Volatility Modeling. **OpenAlex severely undercounts** — her MUST profile lists 5 publications (see below).
- **Verified Publications (from MUST FIE page):**
  1. "Generalized Method of Moments Estimation of Realized Stochastic Volatility Model" — J. Risk & Financial Management (with L. Zhang)
  2. "Rate efficient estimation of realized Laplace transform of volatility with microstructure noise" — Scandinavian J. Statistics 46(3):920–953 (with Z. Liu, X. Xia) ← strongest venue
  3. "Realized Laplace transforms for pure jump semimartingales with microstructure noise" — Soft Computing 23(14):5739–5752 (with Z. Liu, X. Xia)
  4. "Estimation of spot volatility with superposed noisy data" — North American J. Economics & Finance 44:62–79 (with Q. Liu, Y. Liu, Z. Liu)
  5. "Least-squares Monte Carlo for pricing options embedded in mortgages" — J. Applied Finance & Banking 6(2):1–20 (with D. Ding, W. Wang, 2016)
- **must-prof-eval rank:** #2, score 20.012 (high because financial statistics keywords directly match scoring criteria)
- **Assessment:** Core expertise is "realized volatility" estimation using high-frequency financial data — a niche but well-defined area. Publication record is modest (5 papers, mostly with collaborator Zhi Liu from UMacau) but methodologically coherent. Not a deep learning researcher — zero DL publications. Both FYP topics require DL skills she likely doesn't have, so students need to bring their own DL expertise. The professor provides statistical theory grounding; the student provides DL implementation.
- **FYP-024 vs FYP-108 comparison:**
  - 024 (Factor-GARCH + DL → portfolio optimization): Harder. Requires handling PSD constraint on high-dimensional covariance matrices. Math-heavy (matrix manifolds, convex optimization). Higher ceiling but higher risk.
  - 108 (DL-enhanced DCC-GARCH → risk management): More practical. VaR/CVaR backtesting provides clear evaluation metrics. DCC-GARCH → DL upgrade has well-defined baseline. Better alignment with existing quant skills (factor engines → risk management is a natural extension).
  - **Recommendation for students with existing quant/DL background:** FYP-108 — mature evaluation framework, clear baseline, natural skill extension. FYP-024 for students wanting to push mathematical frontier.

## 宋家陽 (Jiayang Song)

- **Research:** LLM Uncertainty, AI
- **FYP Topic:** FYP-2026-121 (Uncertainty Decomposition and Quantification for LLMs)
- **Key Publication:** "Look Before You Leap: An Exploratory Study of Uncertainty Measurement for LLMs" (arXiv 2023, with Yuheng Huang, Lei Ma et al.)
- **must-prof-eval rank:** #41, score 1.2018
- **Assessment:** Niche but well-defined topic. Good for students interested in LLM reliability research.

## 李曉東 (Xiaodong Li)

- **Title:** 教授 (Professor)
- **Email:** xdli@must.edu.mo
- **Academic Leadership:** IEEE Macau Section Chair 2022–2026
- **Research (actual core):** Power Electronics, Power Systems, AI Applications in Energy Systems — **NOT finance**
- **FYP Topics:** FYP-2026-009 (AI Quantitative Trading for US Stocks), FYP-2026-099 (Flywheel Energy Storage Modeling)
- **OpenAlex:** A5100369716 (Xiaodong Li). 11 works, 27 citations. Topics: Energy Load and Power Forecasting, Traffic Prediction, DC-DC Converters. Profile may include same-name merges.
- **Verified papers:** Energy load forecasting with Bi-LSTM (2022), wind power prediction (2025), power cable defect detection (2023, 19 citations). **Zero finance publications.**
- **must-prof-eval rank:** #25, score 4.081
- **Assessment:** Core expertise is power systems/energy engineering. FYP-2026-099 (flywheel energy storage) is his REAL research area. FYP-2026-009 (quant trading) is an opportunistic side interest with no backing publication record. IEEE chair role means strong institutional resources but NOT finance domain expertise. **Do NOT recommend for students seeking deep finance/quant guidance.**

## Scoring System Bias Warning

The `must-prof-eval` scoring system (`quant_supervisor_ranking_v4.json`) weights **direction-match keywords** heavily (financial statistics, stochastic processes, etc.) but does NOT adequately weight:
- Raw publication count
- Total citations
- h-index
- Academic rank (professor > assistant professor)

This causes: 王黎 (#2, assistant professor, 2 papers) outranks 盧曉平 (#20, professor/program director, 150+ papers). Always cross-reference eval scores with actual publication data before making recommendations.
