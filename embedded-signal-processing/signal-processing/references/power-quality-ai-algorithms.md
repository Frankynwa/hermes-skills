# AI Algorithms for Power Quality Analysis — Research Survey

> Compiled for UT285E power quality analyzer project. Covers academic papers,
> open-source implementations, edge deployment strategy, and industry adoption status.

## Technology Roadmap — Three Paradigms

### Paradigm A: Signal Transform + Traditional Classifier

Manually extract features via FFT/STFT/Wavelet/S-Transform/Hilbert Transform,
then feed into SVM/Random Forest/XGBoost.

- 2025 ISGT Europe: RWTH Aachen — Kalman filter event segmentation + Hilbert
  envelope CNN. CNN surpassed traditional SVM in both accuracy and real-time
  deployment efficiency.
- Key insight: The choice of transform matters more than the classifier.
  Hilbert envelope captures transient dynamics better than pure frequency-domain
  transforms.

### Paradigm B: End-to-End Deep Learning

Three sub-routes:
- **1D-CNN**: Spectrogram preprocessed 1D-CNN (2025 IEEE ICCSP) — identifies
  harmonic and non-harmonic disturbances simultaneously. Best speed/accuracy
  tradeoff for edge deployment.
- **LSTM/RNN**: Captures long temporal dependencies. Slightly better accuracy
  on compound disturbances but slower inference.
- **CNN+LSTM hybrid**: CNN extracts local features, LSTM captures temporal
  patterns. Most common high-accuracy approach.

### Paradigm C: Transformer

Latest frontier. Best for complex compound disturbance decoupling, but model
size and latency are obstacles for edge deployment.

## Vetted Papers — Full Quality-Scored Survey (July 2026)

Search scope: OpenAlex (250M+ papers), arXiv, Semantic Scholar, SpringerLink.
IEEE Xplore / IET Digital Library / ScienceDirect / Google Scholar blocked by anti-bot.
All papers verified via DOI lookup on OpenAlex. See `academic-search-methodology.md`
for multi-platform search strategy and anti-bot workarounds.

### A+ Grade (7/7 — IEEE/IET flagship journals, rigourous peer review)

| # | Paper | Venue | Year | Cited | Refs | Score |
|---|-------|-------|------|-------|------|-------|
| 1 | A Comprehensive Review of Harmonic Issues and Estimation Techniques in Power System Networks Based on Traditional and AI/ML — Taghvaie A et al. (Queensland UT) | IEEE Access | 2023 | 95 | 98 | 7/7 |
| 2 | Power quality disturbance signal segmentation and classification based on modified BI-LSTM with double attention mechanism — Khetarpal P et al. | IET GTD | 2023 | 19 | 35 | 7/7 |
| 3 | Transient event classification using PMU data with deep learning techniques and synthetically supported training-set — Gök G et al. (ASELSAN, Turkey) | IET GTD | 2023 | 10 | 39 | 7/7 |
| 4 | Classification of voltage sags causes in industrial power networks using multivariate time-series — Veizaga M et al. (CNRS, France) | IET GTD | 2023 | 24 | 43 | 7/7 |

**Paper 3 (Gök/ASELSAN)** is the most directly relevant to UT285E: transient event classification with synthetic training data augmentation, from an industrial (defense) context with real engineering constraints. ASELSAN is Turkey's largest defense electronics company — the paper carries practical deployment experience, not just academic simulation.

### A Grade (6/7 — Elsevier/Springer major journals)

| # | Paper | Venue | Year | Cited | Refs | Score |
|---|-------|-------|------|-------|------|-------|
| 5 | A systematic review of real-time detection and classification of power quality disturbances — Caicedo JE + Meyer J (TU Dresden) | Protection and Control of Modern Power Systems | 2023 | 119 | 221 | 6/7 |
| 6 | Power quality monitoring in electric grid integrating offshore wind energy: A review — Shao H et al. (NTNU, Norway) | Renewable and Sustainable Energy Reviews (IF 15.9) | 2023 | 74 | 160 | 6/7 |

**Paper 5** is the definitive entry-point review for PQ-AI — 221 references, from TU Dresden (one of Europe's top power systems groups). **Paper 6** is wind-specific but covers the same renewable integration challenges as UT285E's PV scenario.

### B Grade (conference/preprint, published but weaker quality indicators)

| # | Paper | Venue | Year | Cited | Refs | Score |
|---|-------|-------|------|-------|------|-------|
| 7 | Classification of power quality events in the transmission grid: comparative evaluation of different ML models — Güvengir U et al. | CIGRE SEERC 2023 + arXiv:2503.13566 | 2025 | 0 | 0* | — |
| 8 | A Novel Approach to Classify Power Quality Signals Using Vision Transformers — Saber AM et al. (U of Toronto, Concordia) | IECON 2024 (IEEE) + arXiv:2409.00025 | 2024 | 2 | 0* | — |
| 9 | Unsupervised clustering of disturbances in power systems via deep convolutional autoencoders — Islam MM et al. + EPRI | IEEE PESGM 2023 | 2023 | 6 | 13 | 3/7 |

*OpenAlex metadata may undercount conference paper references. Both papers confirmed as legitimately presented at IEEE/CIGRE conferences.

**Paper 8 (ViT)** is notable for method novelty — first application of Vision Transformers to PQD. Authors from reputable Canadian universities. **Paper 9** involves EPRI (Electric Power Research Institute), a major US utility research organization.

### CRITICAL LESSON: The JAIGS Failure

A paper titled "AI-Driven PQ Analytics and Improvement of Grid Connected Solar Energy Systems" was initially recommended based on title/domain match. It was published in JAIGS (ISSN 3006-4023, registered Oct 2024, not indexed in Scopus/WoS/IEEE), had 0 references, 2 citations, and authors from a non-specialist institution. The user correctly rejected it: "不是看到领域符合就行，随便搜一个野鸡注水造假论文". **ALWAYS run `ai-technique-evaluation/references/paper-quality-screening.md` protocol before presenting a paper.** 0 references = automatic rejection, regardless of how well the title matches.

### Key Finding: Zero Edge Deployment Papers

None of the 9 vetted papers — or any paper found across all searched platforms — validates AI inference on a real embedded NPU (like RK3568's 0.8 TOPS NPU). All experiments are either MATLAB/Simulink simulation or server-side Python inference. This confirms UT285E would be the **first** to deploy PQ-AI on an edge NPU in a commercial handheld instrument.

## GitHub Open-Source Implementations

| Repo | Year | Methods | Notes |
|------|------|---------|-------|
| Vishal-Prakash-1 PQD | 2024 | S-Transform + CNN | 99.57% accuracy, full pipeline |
| sayandeep02 PQD | 2026 | RF, XGBoost, SVM, MLP, LSTM | Comparison framework + LIME explainability |
| AbdelAlJurf PQD | 2026 | CNN, LSTM, Transformer | Three-way comparison on standard dataset |
| arsheencodes PQD | 2026 | STFT + CNN | Lightweight, closest to edge deployment needs |

All four repos use public MATLAB/Simulink synthetic datasets. None have been validated on real field waveforms from PV/wind installations.

## S-Transform vs Hilbert Transform — Complementary Roles

- **S-Transform**: Time-frequency decomposition, window width auto-scales with
  frequency. Answers "which frequency components appear when." Good for
  panoramic time-frequency view.
- **Hilbert Transform**: Instantaneous amplitude (envelope), phase, frequency.
  Answers "how the signal's instantaneous state changes." Good for capturing
  transient event dynamics — sag depth/time, oscillatory decay envelope, pulse
  edge steepness.
- **Mixed**: S-Transform does global TF decomposition; Hilbert does local
  instantaneous feature extraction. Combined, they describe a disturbance from
  two complementary dimensions. But compute cost is high — better for offline
  deep analysis mode than real-time edge inference.

## Industry Adoption Status

**Zero precedent in mainstream PQ analyzers.** Fluke 1777, Hioki PQ3198,
CA 8345 — none advertise AI features. The industry is extremely conservative:
IEC certification is priority #1, AI is not in any standard.

Adjacent instrument categories with edge AI:
- Fluke ii900 acoustic imager: leak detection + AI classification
- Hikmicro acoustic imager: partial discharge pattern recognition (CNN on HiSilicon NPU)
- HiLook THP thermal camera: AI anomaly temperature alert

These prove edge AI on handheld instruments is technically viable. PQ analyzers
are simply the last to adopt it.

## Implications for UT285E

1. **Short-term**: Don't ship AI. Preload NPU driver + RKNN Runtime in system image.
2. **Mid-term (6-12 months)**: Start with simplest use case — transient event
   binary classification (attention-worthy vs ignore). STFT+1D-CNN on NPU, <5ms.
   Train on public datasets, fine-tune on real field data.
3. **Long-term (12+ months)**: Harmonic source identification, compound
   disturbance decoupling, inverter efficiency trend prediction. Knowledge
   distillation from large Transformer teacher to small CNN student.

**Key advantage**: UT285E's 20MS/s sampling captures high-frequency transient
details that competitors' 200kS/s instruments simply don't have. The AI model's
input quality is fundamentally superior — this closes the hardware-AI loop that
competitors can't replicate without first upgrading their sampling hardware.

## Data Challenge

Public PQ datasets (e.g., Kaggle) are MATLAB/Simulink synthetic waveforms.
They don't cover PV-specific scenarios (inverter switching oscillations, MPPT
oscillations, partial shading). Models trained on synthetic data will degrade
on real PV field data. UT285E must plan for: ship → collect real field data →
label via DSP heuristics + human review → fine-tune → OTA push. This closed
loop is the moat — no competitor can access the same training data.
