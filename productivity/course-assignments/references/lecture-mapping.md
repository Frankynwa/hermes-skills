# Exam Topic → Lecture Mapping

## CS463 Deep Learning Final Exam

### Section A — Multiple Choice (15 marks, full syllabus)
| Exam Topic | Lectures | Key Concepts |
|-----------|----------|--------------|
| Backpropagation basics | Lect2 | Chain rule, gradient flow, activation gradients |
| CNNs | Lect3, Lect4 | Conv layers, pooling, parameter counting, output size formula |
| Batch Normalization | Lect5 | Train vs test behavior, running statistics, γ/β parameters |
| Residual Networks | Lect5 | Degradation problem, skip connections, ensemble view |
| Transformers | Lect6 | Attention, positional encoding, BERT vs GPT, KV-cache |
| Graph Neural Networks | Lect7 | Message passing, node aggregation, graph convolutions |
| GANs | Lect9 | Generator vs Discriminator, adversarial training, mode collapse |
| VAEs | Lect11 | ELBO, KL divergence, reparameterization trick |
| Normalizing Flows | Lect10 | Bijective transformations, change-of-variables, exact likelihood |
| Diffusion Models | Lect12 | DDPM forward/reverse process, noise prediction, reparameterization |
| Reinforcement Learning | Lect13 | Policy gradient, log-derivative trick, exploration-exploitation |
| Training Dynamics | Lect14 | Overparameterization, loss landscape, flat vs sharp minima, double descent |
| Alignment & Ethics | Lect15 | Outer vs inner alignment, transparency, explainability, LIME |

### Section B — Short Answer Questions (40 marks)
| # | Topic | Primary Lecture |
|---|-------|----------------|
| 1 | Activation functions & gradient flow | Lect2 |
| 2 | Batch Normalization (purpose, train/test, running stats) | Lect5 |
| 3 | Shattered gradient & residual connections | Lect5 |
| 4 | Autoregressive decoding & KV-cache | Lect6 |
| 5 | BERT vs GPT (attention mask, use cases) | Lect6 |
| 6 | KL divergence in VAE ELBO | Lect11 |
| 7 | Generative model families comparison | Lect9,10,11,12 |
| 8 | Outer vs inner alignment, transparency vs explainability | Lect15 |

### Section C — Problem Solving (45 marks)
| # | Topic | Primary Lecture | Key Formulas |
|---|-------|----------------|--------------|
| Q1 | DDPM forward process | Lect12 | x_t = √(ᾱ_t)·x_0 + √(1-ᾱ_t)·ε, ᾱ_t = ∏(1-β_s) |
| Q2 | Policy gradient | Lect13 | ∇J = E[∑ ∇log π(a_t|s_t) · R(τ)], log-derivative trick |
| Q3 | Scaled dot-product attention | Lect6 | Attention(Q,K,V) = softmax(QK^T/√d_k)V |
| Q4 | CNN architecture calculations | Lect3,4 | Out = (W-K+2P)/S+1, Params = K·K·C_in·C_out + bias |
