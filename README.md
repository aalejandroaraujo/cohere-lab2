# 41-609 Cohere Lab 2

Microsoft Foundry Model Mastery Workshop, Cohere segment.
Hands-on lab demonstrating Cohere Embed-v4 + Rerank-v4 for customer support retrieval.

## Structure

- **`lab/`**: the notebooks and corpus learners run during the workshop
- **`tests/`**: validation scripts (connection, multimodal, real-image tests)
- **`setup/`**: environment provisioning for the Skillable VM image
- **`sandbox/`**: scratch files and test images (not part of the lab deliverable)

## Quick start (dev machine)

1. Copy `.env.example` to `.env`, fill in your Foundry endpoint and key.
2. Activate the virtual environment:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
3. Validate the environment:
   ```powershell
   python tests\connection_test.py
   ```
4. Open `lab/00-setup.ipynb` in VS Code and run the cells.

## Configuration

The lab reads four values from `.env`:

```
FOUNDRY_ENDPOINT=https://<resource>.services.ai.azure.com
FOUNDRY_KEY=<api-key>
EMBED_MODEL=embed-v-4-0
RERANK_MODEL=Cohere-rerank-v4.0-pro
```

Both models share the same endpoint and key; only the model name differs per call.

## Key technical decisions

- **Cohere on Foundry is called via REST**, not the Foundry SDK.
  Route pattern: `<endpoint>/providers/cohere/v2/{embed,rerank}`.
  The Foundry SDK is built on the OpenAI-compatible Responses API,
  which does not support reranking and does not expose Cohere-native
  embed features (multimodal).
- **Deployment:** Direct from Azure, Global Standard.
- **Vector search:** NumPy cosine similarity for the lab (corpus is small).
  At production scale, swap for FAISS or Azure AI Search.

## Lab flow (60 minutes)

| Notebook | What it teaches | Time |
|---|---|---|
| 00-setup | Confirm environment and model connectivity | 5 min |
| 01-embed | Embed the support corpus with Embed-v4 | 10 min |
| 02-vector-search | Baseline retrieval with cosine similarity | 15 min |
| 03-rerank | Apply Rerank-v4, observe the quality lift | 20 min |
| (wrap-up) | Discuss, try own queries | 10 min |
