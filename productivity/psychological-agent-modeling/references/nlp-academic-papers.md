# Academic Papers — Psych-NLP Pipeline

## Tier 1: Core References (directly implementable)

### LIWC & Chinese Version
- **Pennebaker et al. (2015)** — LIWC2015 psychometric properties. 80+ dimensions, Cronbach's α 0.70-0.90.
- **Huang et al. (2012)** — Chinese LIWC2007 dictionary. ~4500 entries. Correlation with English: r=0.65-0.80. Published in Chinese Journal of Psychology.

### Attachment + Language
- **Slatcher & Pennebaker (2006)** — Couple letters. Avoidant: more negative words, less self-disclosure. Anxious: more 1sg pronouns (r=0.31). N=86 couples.
- **Ireland et al. (2011)** — Language Style Matching predicts relationship stability (β=0.47). N=86 couples.
- **Wahle et al. (2022)** — Therapy transcripts. Avoidant: fewer emotion words, more cognitive words, more conditionals. 3-class accuracy 71%, F1=0.68. N=350+.
- **Stănculescu & Griffiths (2023)** — BERT-based attachment prediction from social media. Binary AUC=0.76, 4-class F1=0.45-0.52. N≈2000.

### Schema + Language
- **Brockmeyer et al. (2015)** — Schema therapy language analysis. Emotional deprivation → more 3rd person pronouns; defectiveness → more negative emotion; harsh standards → more cognitive words. N=43. r=0.25-0.42.
- **Newell et al. (2021)** — EMS + LIWC. Emotional inhibition → decreased emotion words (β=-0.31, p<0.01). Self-sacrifice → 1pl pronouns. N=218. R²=0.15-0.25.
- **Renner et al. (2023)** — ML prediction of EMS from text. Random Forest + SVM. Emotional deprivation/defectiveness/harsh standards best predicted (AUC=0.71-0.78). N=312.

### LLM Assessment
- **Binz & Schulz (2023a)** — Using cognitive psychology to understand GPT-3. PNAS. Human consistency 65-89%.
- **Binz & Schulz (2023b)** — "LLMs are effective psychologists." arXiv:2310.07032. KL divergence from human: 0.02-0.15.
- **Ghandeharioun et al. (2024)** — Google Research. LLM predicts PHQ-9. Pearson r=0.55-0.68. Depression screening AUC=0.82-0.89. N=5000+.
- **Foltz et al. (2023)** — Review of LLM psychological assessment. Assessment journal. Opportunities + ethics.
- **Yang et al. (2023)** — LLMs as few-shot health learners. F1: 0.78-0.85 (EN), 0.71-0.78 (CN).

### Longitudinal Tracking
- **Sondergaard et al. (2022)** — Language change in therapy predicts outcome. AUC=0.74. N=120 clients.
- **Aafjes-van Doorn et al. (2020)** — Cognitive word increase + emotion word trajectory → better outcomes. N=85.
- **Al-Mosaiwi & Johnstone (2018)** — Absolutist words specific to anxiety/depression. AUC=0.78. N=63,000+ posts.

## Tier 2: Chinese-Specific

- **Qiu et al. (2019)** — Weibo depression detection. LSTM+attention. Accuracy 0.84, F1=0.81. N=5203 posts.
- **Cheng et al. (2017)** — Chinese social media suicide risk. jieba+TF-IDF+SVM. Accuracy 0.76, F1=0.74. N=2414.
- **Cui et al. (2020)** — Chinese-BERT-wwm. +1-3% on Chinese NLU benchmarks.
- **Yang et al. (2023)** — C-MEL Chinese mental health emotional language dataset. 12000+ annotated samples. F1=0.73-0.82.

## Chinese Sentiment Lexicons

| Lexicon | Entries | Source | Notes |
|---------|---------|--------|-------|
| LIWC-CN 2007 | ~4,500 | Pennebaker team | Cross-linguistic comparable |
| Dalian Univ. Affective Lexicon | ~27,000 | Xu Linhong et al. | 7 categories, 21 subcategories |
| HowNet | ~8,900 | Dong Zhendong | Semantic primitives |
| NTUSD | ~11,000 | NTU | Bilingual CN/EN |
| BosonNLP | ~100,000 | BosonNLP | Covers internet slang |

## Accuracy Ceilings

| Dimension | Method | Best Accuracy | Notes |
|-----------|--------|---------------|-------|
| Depression binary | BERT-based | F1 0.85-0.93 | Clinical datasets |
| Personality (Big Five) | Transformer | r=0.50-0.70 | Self-report ceiling r≈0.75 |
| Attachment binary | BERT | AUC 0.72-0.78 | Limited by construct stability |
| Attachment 4-class | BERT | F1 0.45-0.52 | Fearful-avoidant hardest |
| Schema (EMS) binary | RF+SVM | AUC 0.71-0.78 | Novel field |
| PHQ-9 prediction | LLM | r=0.55-0.68 | Prompt-engineered |
