---
name: fitness-science
description: Evidence-based fitness, body recomposition, posture correction, and nutrition science. Use when the user asks about body type, weight loss, muscle gain, gym programming, posture correction, or nutrition strategy.
---

# Evidence-Based Fitness Science

## Trigger

Load this skill when the user asks about: body type classification, weight management, muscle gain, gym training plans, posture correction (forward head, rounded shoulders), nutrition/macro strategy, or body recomposition.

## Core Principles

### 1. Don't assume body type without data

Always request height, weight, training history, and current activity level before classifying body type or prescribing a plan. "外胚型/内胚型" labels should only be applied after seeing actual data, not from self-description alone.

### 2. Somatotype (body type) has weak scientific validity for training prescription

The Sheldon somatotype classification (ectomorph/mesomorph/endomorph) has heritability of 0.65-0.91 (Silventoinen 2021, *Am J Hum Biol*), but its predictive value for training response is weak. Somatotype reflects sport selection effects, not differential training adaptation (Esteve-Ibáñez 2025, *Nutrients*).

**Practical takeaway**: Don't build training strategies around "endomorph diet" or "ectomorph training." Use actual body composition data (body fat %, muscle mass) and individual metabolic response instead.

### 3. Body recomposition (simultaneous fat loss + muscle gain) is well-supported

Higher baseline body fat + lower training experience = **easier recomposition**. Key conditions:

| Variable | Evidence-based target |
|----------|----------------------|
| Protein | **2.2-2.4 g/kg body weight/day** (not lower; Longland 2016, *AJCN*) |
| Caloric deficit | 300-500 kcal/day (moderate, not aggressive) |
| Training | Progressive resistance training mandatory |
| ISSN position | 2.3-3.1 g/kg LBM during deficit (Aragon 2017, *JISSN*) |

Landmark study: 2.4 g/kg protein group gained 1.2 kg LBM while losing 4.8 kg fat in 4 weeks at 40% deficit (Longland 2016).

### 4. Posture correction: evidence-backed exercises

2024 meta-analysis (Sepehri, *BMC Musculoskeletal Disorders*, 22 studies):

**Most effective approach**: Combined strength + stretch + shoulder-specific program.

**Highest-evidence exercises**:
- Chin tuck (下巴后缩) — deep neck flexor activation
- Wall angels (靠墙天使) — scapular retraining
- Band rows / face pulls (弹力带划船/面拉) — mid/lower trapezius
- Doorway chest stretch (门框胸肌拉伸) — pectoralis release

2026 RCT (Khaledi): 8 weeks of either isometric or isotonic exercise improves forward head posture by 6-8°. Both equally effective.

Diaphragmatic breathing retraining may add benefit (Jeong 2024, *J Clin Med*).

### 5. Protein is the most critical controllable variable in deficit

Default recommendation for cutting/recomposition: **2.0-2.4 g/kg/day**. Lower end for experienced lifters, higher end for novices with higher body fat. Never below 1.6 g/kg.

### 6. Open-source tools

| Tool | Use case | Stars |
|------|----------|-------|
| [wger](https://github.com/wger-project/wger) | Full fitness platform (training + nutrition + measurement) | 6.5k |
| [OpenNutriTracker](https://github.com/simonoppowa/OpenNutriTracker) | Nutrition/calorie tracking only | 2.2k |
| [lyftr](https://github.com/Cawlumm/lyftr) | Lightweight self-hosted workout tracker | 178 |

Posture assessment tools on GitHub are universally low-quality (≤4 stars, academic projects). Not recommended for direct use.

## Quick Reference Formulas

```
BMR (Mifflin-St Jeor, male):
  10 × weight(kg) + 6.25 × height(cm) - 5 × age + 5

TDEE = BMR × activity_factor
  Sedentary: 1.2
  Light (1-3x/week): 1.375
  Moderate (3-5x/week): 1.55
  Heavy (6-7x/week): 1.725

Cutting: TDEE - 300~500 kcal
Protein: 2.0-2.4 g/kg
Fat: 0.8-1.0 g/kg
Carbs: remainder
```

See `references/papers.md` for full academic citations and detailed findings.

## Pitfalls

- **Don't prescribe TDEE+400 to someone who hasn't confirmed they're underweight.** Wait for actual height/weight data.
- **"Ectomorph must bulk / endomorph must cut" is not evidence-based.** Individual response varies.
- **Don't add excessive cardio for fat loss in resistance-trained individuals.** Resistance training alone is effective; excessive cardio risks muscle loss and appetite rebound.
- **Posture correction takes 6-8 weeks minimum for measurable change.** Don't promise "1-2 week results" for structural changes — that's for habit formation, not anatomical improvement.
