"""
Cohere Embed-v4 MULTIMODAL test on Azure Foundry.
Confirms whether image (and image+text) embeddings work via the
/providers/cohere/v2/embed route - the thing Andy (Cohere) is asking about.

Embed-v4 multimodal accepts images as base64 data URLs in an `inputs` structure.
We test three things in order:
  1. text-only embed (known to work, as a baseline)
  2. image-only embed
  3. mixed text+image embed (interleaved, Embed-v4's headline capability)

.env (same as connection_test.py):
  FOUNDRY_ENDPOINT=https://<resource>.services.ai.azure.com
  FOUNDRY_KEY=<key>
  EMBED_MODEL=embed-v-4-0

Run:  .\.venv\Scripts\python.exe multimodal_test.py
"""
import os, base64, sys
import requests
from dotenv import load_dotenv

load_dotenv()
ENDPOINT = os.environ.get("FOUNDRY_ENDPOINT", "").rstrip("/")
KEY = os.environ.get("FOUNDRY_KEY", "")
EMBED_MODEL = os.environ.get("EMBED_MODEL", "embed-v-4-0")
URL = f"{ENDPOINT}/providers/cohere/v2/embed"
HEADERS = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}

# A tiny 1x1 red PNG as a stand-in image (no external file needed).
# Replace with a real screenshot/diagram later for a realistic demo.
RED_DOT_PNG_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
)
DATA_URL = f"data:image/png;base64,{RED_DOT_PNG_B64}"


def post(payload, label):
    try:
        r = requests.post(URL, headers=HEADERS, json=payload, timeout=60)
        if r.status_code != 200:
            print(f"  {label}: HTTP {r.status_code}: {r.text[:300]}")
            return None
        data = r.json()
        embs = data.get("embeddings")
        vec = embs["float"][0] if isinstance(embs, dict) else embs[0]
        print(f"  {label}: OK, dim={len(vec)}")
        return vec
    except Exception as e:
        print(f"  {label}: {type(e).__name__}: {e}")
        return None


print("Cohere Embed-v4 multimodal test")
print(f"endpoint: {ENDPOINT}\nmodel: {EMBED_MODEL}\n")
if not ENDPOINT or not KEY:
    print("FAIL: missing FOUNDRY_ENDPOINT or FOUNDRY_KEY in .env")
    sys.exit(1)

# ---- 1. text-only (baseline, the shape we know works) ----
print("[1] text-only embed")
post({"model": EMBED_MODEL, "texts": ["a red square"],
      "input_type": "search_document", "embedding_types": ["float"]}, "text")

# ---- 2. image-only embed (Embed-v4 inputs structure) ----
# Cohere v2 multimodal uses an `inputs` array with content items.
print("\n[2] image-only embed (inputs structure)")
post({
    "model": EMBED_MODEL,
    "input_type": "search_document",
    "embedding_types": ["float"],
    "inputs": [
        {"content": [{"type": "image_url", "image_url": {"url": DATA_URL}}]}
    ],
}, "image (inputs)")

# ---- 2b. alternate image field name some versions use ----
print("\n[2b] image-only embed (images field fallback)")
post({
    "model": EMBED_MODEL,
    "input_type": "search_document",
    "embedding_types": ["float"],
    "images": [DATA_URL],
}, "image (images field)")

# ---- 3. mixed text + image (interleaved) ----
print("\n[3] mixed text+image embed (interleaved inputs)")
post({
    "model": EMBED_MODEL,
    "input_type": "search_document",
    "embedding_types": ["float"],
    "inputs": [
        {"content": [
            {"type": "text", "text": "a red square"},
            {"type": "image_url", "image_url": {"url": DATA_URL}},
        ]}
    ],
}, "text+image (inputs)")

print("\n" + "=" * 60)
print("READING THE RESULT")
print("=" * 60)
print("- If [1] works but [2]/[2b]/[3] all fail: multimodal may not be enabled")
print("  on this deployment via REST. Capture the exact error to show Andy/MS.")
print("- If any of [2], [2b], [3] return a dim: multimodal WORKS. Note which")
print("  payload shape succeeded - that is the one to use in the lab and to")
print("  send Andy as working code.")
print("- 400/422 usually means the payload shape is wrong (try the other variant).")
print("- 404 means wrong route. 401 means auth. 500 may mean model/feature gating.")
