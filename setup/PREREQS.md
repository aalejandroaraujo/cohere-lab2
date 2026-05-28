# Cohere Lab 2 - Prerequisites (Windows)

Canonical list of everything a clean Windows machine (or the Skillable Windows VM
image) needs to author and run the Cohere Embed + Rerank lab. Drives
`install-prereqs.ps1` (PowerShell). Target platform is Windows only: both the dev
machine and the Skillable lab VM are Windows.

## System-level (installed once on the VM image)

| Prereq | Version | Why | Notes |
|---|---|---|---|
| Python | 3.11 or 3.12 | runs the notebooks and SDK | Install via `winget install -e --id Python.Python.3.12`. Add to PATH and disable the Microsoft Store alias (Settings > Apps > Advanced app settings > App execution aliases > turn off python.exe / python3.exe) |
| pip | latest | installs Python packages | bundled with Python; upgrade after install |
| Azure CLI (`az`) | latest | `az login` for DefaultAzureCredential auth | `winget install -e --id Microsoft.AzureCLI`; only needed if using Entra ID auth instead of API keys |
| VS Code | latest | the IDE on the left/right lab layout | `winget install -e --id Microsoft.VisualStudioCode` |
| VS Code ext: Python | ms-python.python | run/debug Python | |
| VS Code ext: Jupyter | ms-toolsai.jupyter | run notebooks inline | |
| Git | latest | clone the take-home repo | optional for the live lab, useful for dev |

## Python packages (from requirements.txt, in a venv)

| Package | Purpose |
|---|---|
| cohere | Cohere SDK pointed at the Azure endpoint (Pattern A) |
| requests | raw REST calls to /v1/embed, /v1/rerank (Pattern B) |
| python-dotenv | load endpoint/key config from .env |
| numpy | vector math |
| faiss-cpu | in-memory vector index (no external service) |
| jupyter, ipykernel | notebook runtime |
| azure-ai-projects, azure-identity | Lab 1 only (chat/e2e Foundry), not needed for embed+rerank |

## Azure-side prerequisites (the deployed models, done by Charles for the event)

| Item | Value |
|---|---|
| Foundry resource + project | one per event/partner |
| Embed model | embed-v-4-0 (Direct from Azure, Global Standard) |
| Rerank model | Cohere-rerank-v4.0-pro (Direct from Azure, Global Standard) |
| Deployment type | Global Standard (NOT Managed compute, which bills idle) |
| Per learner | endpoint URL + key for each model, surfaced as env vars |

## Environment variables (per deployment)

```
EMBED_ENDPOINT=https://<embed-endpoint>      # base URL, no trailing path
EMBED_KEY=<embed-key>
RERANK_ENDPOINT=https://<rerank-endpoint>     # base URL, no trailing path
RERANK_KEY=<rerank-key>
```

## Files staged in the lab folder

| File | Purpose |
|---|---|
| requirements.txt | Python packages |
| .env.example | template for the four endpoint/key vars |
| connection_test.py | validates embed + rerank work (both call patterns) |
| support_corpus.json | the ~150-doc support corpus |
| (notebooks) | the Lab 2 hands-on notebooks (next build) |

## Install order (Windows)

1. Disable the Microsoft Store python alias (Settings > Apps > Advanced app settings > App execution aliases).
2. System-level: Python 3.12, Azure CLI, VS Code + extensions (run install-prereqs.ps1).
3. Open a NEW terminal after installing Python (PATH refreshes only in a new shell).
4. `python -m venv .venv` and `.\.venv\Scripts\Activate.ps1`
5. `python -m pip install -r requirements.txt`
6. `copy .env.example .env` and fill in the four values from the Foundry deployments
7. `python connection_test.py` -> expect PASS on embed + rerank
8. Open the notebooks and run

## Notes for the Skillable VM image (for Charles)

- Bake Python 3.12, pip, VS Code + the two extensions, and Azure CLI into the base image.
- Pre-create the venv and pre-install requirements.txt so launch is instant.
- The two models are pre-deployed via the resource template; endpoints/keys land as env vars.
- Learner opens the folder, everything runs with zero setup.
