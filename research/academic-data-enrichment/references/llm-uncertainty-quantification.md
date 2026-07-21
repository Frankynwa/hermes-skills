# LLM Uncertainty Quantification — Research Knowledge Bank

## Overview

UQ for LLMs: measuring how confident a model is in its outputs, decomposing uncertainty into components, and using uncertainty signals for hallucination detection and abstention.

## Taxonomy of Methods

### By Input Source
- **Input Uncertainty**: Prompt clarification, perturbation stability, in-context variation
- **Reasoning Uncertainty**: CoT disagreement, Tree-of-thought, topology-based reasoning graphs
- **Parameter Uncertainty**: Bayesian LoRA, LoRA ensembles, uncertainty-aware instruction tuning
- **Prediction Uncertainty**: Largest category, most studied

### By Access Level
- **Whitebox** (need logits/hidden states): Perplexity, entropy, logprobs, attention-based (SAR)
- **Blackbox** (only outputs): Semantic entropy, graph methods, verbalized confidence

### By Compute Cost
- **Low** (single forward pass): Perplexity, entropy, logprob, P(True)
- **Medium**: PMI, verbalized confidence
- **High** (multiple generations): Semantic entropy, graph methods, SAR

## Key Methods

| Method | Venue | What It Does |
|--------|-------|-------------|
| **Semantic Entropy** | ICLR 2023 → Nature 2024 | Groups semantically equivalent answers before computing entropy. Foundational work. |
| **SAR** (Shifting Attention to Relevance) | ACL 2024 | Ranks **1st** among 28 methods in LM-Polygraph. Shifts token attention from likelihood to relevance. |
| **Spectral Uncertainty Decomposition** | AAAI 2026 | Decomposes AU + EU via eigenvalue analysis of answer similarity matrices + input clarification. |
| **Verbalized Confidence** | ICLR 2024 | P(True) prompting; CoT+M5+AvgConf achieves 90.92% AUROC on GSM8K. |
| **Kernel Language Entropy** | NeurIPS 2024 | Kernel-based entropy over semantic clusters. |
| **EigenScore** | ICLR 2024 | Eigenvalue-based scoring for answer diversity. |
| **LM-Polygraph** | EMNLP 2023 → TACL 2025 | Benchmark framework for 35+ UE methods. |
| **Claim-Conditioned Probability** | 2024 | Per-claim uncertainty in addition to sequence-level. |
| **CoCoA** | 2025 | Combined context-aware method. |
| **RAUQ** | 2025 | Recurrent Attention-based UQ. |

## Uncertainty Decomposition (AU vs EU)

**Aleatoric Uncertainty (AU)** — irreducible, from question ambiguity.
- Example: "Capital of Turkey?" → Ankara (political) or Istanbul (cultural)
- Response: Ask for clarification

**Epistemic Uncertainty (EU)** — reducible, from model knowledge gaps.
- Example: Factual answer not in training data
- Response: Abstain or retrieve external information

**Decomposition methods:**
1. **Spectral approach** (AAAI 2026): Eigenvalue decomposition of answer similarity matrices, combined with input clarification via GPT-4o to resolve ambiguity
2. **Input clarification delta**: Generate clarified versions → measure uncertainty reduction → remainder ≈ EU
3. **Clinical Reasoning Graph** (2026): Graph-theoretical AU/EU decomposition for medical diagnosis

## Benchmarks & Evaluation

**Framework:** LM-Polygraph (`pip install lm-polygraph`) — 35+ methods, unified interface
**Toolkit:** omniuq (`pip install omniuq`) — newer, modular

**Datasets:**
- Short QA: TriviaQA, CoQA, SciQ, SQuAD, Natural Questions, BioASQ
- Ambiguity: AmbigQA, AmbigInst
- Math reasoning: SVAMP, GSM8K

**Metrics:**
- **AUROC**: Can the score separate correct from incorrect?
- **AUARC/AURC**: Ranking quality (risk-coverage)
- **ECE**: Calibration error — is "90% confident" correct 90% of the time?

## Typical FYP Pipeline

1. Select 2-3 LLMs (Llama-3.1-8B, Phi-4, Mistral-7B)
2. Generate multiple answers per question (temperature sampling)
3. Compute uncertainty scores (perplexity, semantic entropy, SAR, graph-based)
4. Optionally decompose into AU/EU (input clarification + eigenvalue analysis)
5. Evaluate AUROC (ranking) + ECE (calibration)
6. Analyze correlation with hallucination detection

## Key Repositories

- `IINemo/lm-polygraph` — benchmark framework
- `MinaGabriel/omniuq` — modular UQ toolkit
- `MLO-lab/spectral_uncertainty_decomposition` — AU/EU decomposition (AAAI 2026)
- `jlko/semantic_uncertainty` — Nature 2024 paper code
- `jinhaoduan/SAR` — top-ranked method (ACL 2024)

## MUST Faculty

- **宋家陽 (Jiayang Song)** — co-authored "Look Before You Leap: Uncertainty Measurement for LLMs" (arXiv 2023). FYP-2026-121 topic: "Uncertainty Decomposition and Quantification for LLMs".
