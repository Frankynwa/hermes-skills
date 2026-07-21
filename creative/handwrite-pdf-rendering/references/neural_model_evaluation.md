# Neural Network Handwriting Generation Models — Evaluation Results

## Summary

Evaluated 4 neural network approaches for replacing the font+perturbation architecture. None were successfully integrated due to quality, availability, or network barriers.

## Models Evaluated

### 1. Graves RNN (pytorch-handwriting-synthesis-toolkit)
- **Status**: Integrated but disabled for most use cases
- **Quality**: 3-4/10 (illegible for most text)
- **Language**: English ASCII only (79 chars)
- **Model**: Pre-trained on IAM-OnDB, 56 epochs
- **Path**: `libs/pytorch-handwriting-synthesis-toolkit/checkpoints/Epoch_56/`
- **Issues**:
  - Single character ("A") → 1 point only (useless)
  - Short text ("Hello World") → distorted, overlapping strokes
  - Long text ("Calculus II Problem Set 7") → somewhat recognizable but still poor quality
  - Cursive output is illegible, not suitable for homework submission
- **Conclusion**: Not viable for production. The model is undertrained and the IAM dataset is too small.

### 2. HWT (Handwriting Transformers, ICCV 2021)
- **Status**: Not integrated
- **Quality**: Unknown (couldn't test)
- **Language**: English (trained on IAM/CVL)
- **Source**: https://github.com/ankanbhunia/Handwriting-Transformers
- **HuggingFace**: https://ankankbhunia-hwt.hf.space/
- **Issues**:
  - HuggingFace Space API unreliable (timeouts, queue system requires session hash)
  - Pre-trained weights on Google Drive (~download fails/times out)
  - `gradio_client` library connection times out
  - Needs style reference images (few-shot setting)
- **Conclusion**: API unavailable. Would need to download weights and run locally.

### 3. OLHWG (ICLR 2025 — Decoupling Layout from Glyph)
- **Status**: Code cloned, data download failed
- **Quality**: High (per paper)
- **Language**: Chinese (online handwriting)
- **Source**: https://github.com/singularityrms/OLHWG
- **Data**: https://huggingface.co/datasets/Immortalman12/OLHWD
- **Architecture**: 1D U-Net diffusion model for character generation + LSTM for layout
- **Issues**:
  - HuggingFace dataset download times out (network issues in Macau/China)
  - `hf-mirror.com` doesn't have this dataset (404)
  - `curl` download times out after 300s
  - Needs training from scratch (no pre-trained weights provided)
  - Training requires GPU (MPS available on user's Mac, 16GB RAM)
- **Conclusion**: Best candidate for Chinese handwriting. Needs network access to download data (~1GB). Training time estimated 2-6 hours on MPS.

### 4. CASIA-OLHWDB (Dataset)
- **Status**: Not downloaded
- **Language**: Chinese online handwriting
- **Issues**: Same network timeout issues as OLHWG data
- **Conclusion**: Would need to train a model on this data. Not a standalone solution.

## Network Barriers (Macau/China)

Downloads from these sources consistently time out:
- HuggingFace (huggingface.co) — 300s timeout
- Google Drive — 120s timeout  
- GitHub raw files — intermittent

Working sources:
- GitHub API (api.github.com) — fast for metadata
- PyPI packages — usually OK
- Local font files — already present

## Key Lesson

**The font+perturbation architecture has a hard ceiling.** The mixed-font technique (楷书/草书 per character) is the best achievable within this architecture. For true handwriting quality, a trained neural network model is needed, but network barriers prevent downloading training data/models.

## Recommended Next Steps (When Network Improves)

1. **Download OLHWG data** from HuggingFace (datas.npy + mydict.npy)
2. **Train diffusion model** on user's Mac (MPS, 2-6 hours)
3. **Integrate** as new rendering path: text → OLHWG → stroke image → compositor
4. **Alternative**: Use CASIA-OLHWDB to train Graves RNN model for Chinese (the toolkit supports custom datasets)
