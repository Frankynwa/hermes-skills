# Ensemble Theory: Why Comprehensive Models Don't Need MoA

## Core Principle

The accuracy-diversity tradeoff is fundamental, not incidental. As a model becomes more comprehensive, its utility in an ensemble diminishes — because there are fewer UNIQUE errors for other models to correct.

## Key Theorems

### 1. Breiman (2001) — Error Correlation Bound

From Random Forests (Machine Learning 45:5-32):

```
Ensemble error ≤ ρ × individual_error
```

Where ρ = average correlation between model errors.

**Applied to LLMs:** If Model A gets 13/15 questions right and Model B gets 12/15 right, but the 2 questions Model A missed are the same ones Model B missed → ρ ≈ 1 → ensemble adds nothing. The complementarity rate = fraction of questions where exactly one model is correct.

### 2. Krogh & Vedelsby (1995) — Ambiguity Decomposition

```
E_ens = E_avg − A_avg
```

E_ens = ensemble error, E_avg = average individual error, A_avg = average ambiguity (diversity/disagreement).

As individual models get stronger, E_avg shrinks. The potential gain A_avg also shrinks because stronger models disagree less often.

### 3. Kuncheva & Whitaker (2003) — Diversity-Accuracy Paradox

Systematically evaluated 10 diversity measures. Core finding: "diversity and accuracy are inversely correlated — the accuracy-diversity tradeoff is fundamental, not incidental."

### 4. Dietterich (2000) — Three Reasons Ensembles Work

1. Statistical: reduce variance of single hypothesis
2. Computational: avoid local optima
3. Representational: expand hypothesis space

All three diminish when the individual model already has high coverage of the relevant hypothesis space.

### 5. Fort et al. (2019) — Mode Collapse in Deep Ensembles

As individual model coverage of the hypothesis space increases, different models begin exploring the same "modes." Mode diversity collapses, reducing ensemble gain.

## Practical Implication for MiMo v2.5 Pro

MiMo v2.5 Pro (the commercial version, not the 7B open-source model) achieves broad coverage across reasoning domains. Its official 7B version already reaches:

- MATH-500: 95.8% (vs GPT-4o 74.6%)
- AIME 2024: 68.2% (vs GPT-4o 9.3%)
- LiveCodeBench v5: 57.8% (vs GPT-4o 32.9%)

The v2.5 Pro commercial version is significantly larger. This means:

- MiMo's error coverage has high ρ (correlation) with all other models
- Complementarity rates of 13-23% mean < 1/4 of questions benefit from ensemble
- Cost of adding MiMo to MoA: pays for 3 extra API calls but only captures ~3 additional questions out of 15

**Conclusion: MiMo is best used as a standalone primary model. MoA (DS + MiniMax + Qwen) is reserved for cases where MiMo itself is stuck.**
