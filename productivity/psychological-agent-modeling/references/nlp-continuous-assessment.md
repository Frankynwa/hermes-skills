# NLP-Based Continuous Psychological Assessment — Research & Implementation

## Overview

Phase 1 of a system that starts with structured questionnaires (ECR-R, YSQ-S3) and evolves into continuous natural language-based psychological assessment. The NLP engine extracts features from Chinese text and maps them to attachment dimensions, schema activation levels, and IFS part activity.

**Package location**: `~/projects/psych-nlp/` (Python, `psych_nlp` module)

**Usage**:
```python
from psych_nlp import PsychAnalyzer
analyzer = PsychAnalyzer()
result = analyzer.analyze("还行吧，没什么特别的感觉。")
print(result.format_report())  # Full Chinese report with scores
```

## Architecture

```
用户文本 → jieba分词 → 12类中文心理词典匹配 → 特征提取
    ↓
依恋维度 (焦虑/回避 0-5)    图式激活 (8个图式 0-5)    IFS部分活跃度 (0-5)
    ↓                                                    ↓
基线对比 (ECR-R/YSQ-S3)                             MiroFish Agent参数更新
    ↓                                                    ↓
纵向追踪 (变化检测)                                  模拟运行
```

## 12 Dictionaries Built

1. Positive emotion (100+ words)
2. Negative emotion (100+ words)
3. Cognitive processing words (50+) — avoidance marker
4. Absolutist words (30+) — anxiety/depression marker (Al-Mosaiwi 2018)
5. First person singular/plural, second/third person pronouns
6. Somatic expressions (50+) — Chinese-specific: 心里堵得慌, 喘不过气
7. Internet slang emotion (30+) — emo了, 破防, 绷不住
8. Emotional inhibition markers (30+) — 还行吧, 怎么说呢, 其实客观来说
9. Harsh standards markers (20+) — 应该, 必须, 完美, 不够好
10. Emotional deprivation markers (20+) — 没人理解, 不被看见
11. Topic shift markers (20+) — 不想了, 换个方向, 先做别的
12. Time markers (past/present/future)

## Key Academic Papers

### Foundation
- Pennebaker (2015) — LIWC2015, 80+ psycholinguistic dimensions
- Huang et al. (2012) — LIWC-CN, 4500 Chinese entries

### Attachment Language Markers
- Slatcher & Pennebaker (2006) — attachment style in love letters, r=-0.27 (avoidance×first-person)
- Wahle et al. (2022) — therapy transcripts, 3-way classification 71% accuracy
- Stănculescu & Griffiths (2023) — BERT attachment prediction, AUC=0.76

### Schema Language Markers
- Newell et al. (2021) — EMS×language, emotional inhibition→emotion words β=-0.31
- Brockmeyer et al. (2015) — schema therapy language, r=0.25-0.42
- Renner et al. (2023) — ML schema prediction, AUC=0.71-0.78

### LLM-Based Assessment
- Binz & Schulz (2023) — "LLM are effective psychologists", KL divergence 0.02-0.15
- Ghandeharioun et al. (2024) — Google Research, PHQ-9 prediction AUC=0.82-0.89
- Foltz et al. (2023) — Assessment journal, LLM potential + ethical challenges

### Longitudinal Tracking
- Sondergaard et al. (2022) — language change trajectory predicts therapy outcome AUC=0.74
- Al-Mosaiwi (2018) — absolutist words AUC=0.78 for anxiety/depression

### Chinese-Specific
- Qiu et al. (2019) — Weibo depression detection F1=0.81
- Yang et al. (2023) — C-MEL Chinese mental health emotional language dataset, 12000+ samples
- Cui et al. (2020) — Chinese-BERT-wwm

## Three Extraction Dimensions

### 1. Attachment (焦虑/回避 0-5)
Anxiety = weighted combination of: first-person singular ratio, absolutist words, negative emotion, somatic expressions, emotion valence
Avoidance = weighted combination of: cognitive words, emotion ratio (inverse), hedging words, third person, first person (inverse), emotional inhibition markers
Weights calibrated to literature effect sizes (Slatcher r=0.27-0.31, Al-Mosaiwi AUC=0.78)

### 2. Schema Activation (8 schemas, 0-5 each)
- Emotional inhibition: emotion ratio (inverse) + hedging + dictionary markers + third person
- Harsh standards: cognitive words + absolutist + dictionary markers
- Emotional deprivation: dictionary markers + negative emotion + first person
- Others: abandonment, defectiveness, dependence, vulnerability, vigilance

### 3. IFS Part Activity (0-5 each)
- Protector: cognitive + obligation words + low emotion + first person
- Firefighter: topic shift + escape language + slang + future orientation
- Exile: emotion + vulnerability words + past orientation + first person + negative
- Self: self-awareness words + emotional balance + low absolutism + first person plural

## Validation Results (4 test cases)

| Input Pattern | Expected | Detected | Correct? |
|---|---|---|---|
| "还行吧，没什么特别的感觉" (suppressive) | Emotional inhibition high | EI 3.32/5, Firefighter dominant | ✅ |
| "我好害怕，总是做不好，心里堵得慌" (anxious) | Anxiety high, Exile dominant | Anxiety 3.4/5, Exile 3.82/5, conflict 50% | ✅ |
| "不想了，换个方向，先打把游戏" (avoidant) | Firefighter dominant | FF 3.75/5, EI 3.56/5 | ✅ |
| "我注意到自己在逃避，我好奇为什么" (Self) | Self presence high | Self 4.06/5, low anxiety/avoidance | ✅ |

## Key Chinese NLP Challenges

1. **Somatic expression**: Chinese users express psychological pain through body (心里堵, 胸闷, 喘不过气)
2. **Indirectness**: "还行吧" may mean very bad; "没事" may mean very much not ok
3. **Modal particles**: 吧/呢/啊/了 carry emotional information
4. **Internet slang**: emo了, 破防了, 绷不住了 — high frequency in young users
5. **Double negation**: "不是不好" = good — more complex than English

## Open-Source Tools Referenced

| Tool | Stars | Use |
|------|-------|-----|
| HanLP | 33k | Chinese NLP (segmentation, POS, dependency parsing) |
| jieba | 33k | Chinese word segmentation |
| EmoLLM | active | Chinese mental health LLM (Qwen/DeepSeek support) |
| Chinese-BERT-wwm | — | Chinese pre-trained encoder |
| smallville-2 | active | Generative Agents implementation |

## IFS + AI: Completely Novel

No existing open-source project combines IFS therapy with AI agents. This is the innovation point of the project.

## Next Phases

- **Phase 2**: LLM-based assessment (prompt-engineered evaluation from conversation history)
- **Phase 3**: Fine-tuned model using accumulated personal data
- **Phase 4**: Predictive alerting (detect pattern activation before it fully unfolds)
- **Integration**: Auto-update MiroFish agent parameters from NLP assessment results

## Failure Modes & Limitations

1. **Fearful-avoidant masking**: High suppression tendency — language may look more "normal" than actual state
2. **Minimum text length**: ≥50 chars for emotion, ≥500 chars for schema, ≥2000 chars/week for reliable assessment
3. **Chinese schema markers**: Almost no existing research — dictionaries built from inference + English literature translation
4. **Calibration needed**: NLP scores need periodic questionnaire recalibration (every 3 months)
5. **Ceiling accuracy**: Attachment 2-class ~76% AUC, 4-class ~50% F1; Schema detection ~75% AUC
