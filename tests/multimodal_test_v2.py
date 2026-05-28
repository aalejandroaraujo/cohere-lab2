"""
Multimodal test v2: try Cohere's documented v2 shape and OpenAI-style fallback.
Cohere's v2 multimodal embed expects an `inputs` array where each input has a
`content` list of typed parts. The content types per Cohere docs are:
  - {"type": "text", "text": "..."}
  - {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}}
We also try {"type": "image", "image": "data:..."} as an alternate.
"""
import os, base64, sys, json
import requests
from dotenv import load_dotenv

load_dotenv()
ENDPOINT = os.environ.get("FOUNDRY_ENDPOINT", "").rstrip("/")
KEY = os.environ.get("FOUNDRY_KEY", "")
EMBED_MODEL = os.environ.get("EMBED_MODEL", "embed-v-4-0")
URL = f"{ENDPOINT}/providers/cohere/v2/embed"
HEADERS = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}

# A slightly more substantial test image (10x10 solid red JPEG, ~150 bytes)
# Some image embedders reject 1x1 trivial inputs; this avoids that edge case.
RED_10x10_JPEG_B64 = (
    "/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAMCAgICAgMCAgIDAwMDBAYEBAQEBAgGBgUGCQgKCgkICQkKDA8MCgsOCwkJDRENDg8QEBEQCgwSExIQEw8QEBD/2wBDAQMDAwQDBAgEBAgQCwkLEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBD/wAARCAAKAAoDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAr/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFAEBAAAAAAAAAAAAAAAAAAAAAP/EABQRAQAAAAAAAAAAAAAAAAAAAAD/2gAMAwEAAhEDEQA/AL+AAAAAAAH//Z"
)
DATA_URL = f"data:image/jpeg;base64,{RED_10x10_JPEG_B64}"


def post(payload, label):
    try:
        r = requests.post(URL, headers=HEADERS, json=payload, timeout=60)
        if r.status_code != 200:
            print(f"  {label}: HTTP {r.status_code}")
            print(f"     body: {r.text[:400]}")
            return None
        d = r.json()
        embs = d.get("embeddings")
        vec = embs["float"][0] if isinstance(embs, dict) else embs[0]
        print(f"  {label}: OK, dim={len(vec)}")
        return vec
    except Exception as e:
        print(f"  {label}: {type(e).__name__}: {e}")
        return None


print("Cohere Embed-v4 multimodal test v2 (documented v2 shape)")
print(f"endpoint: {ENDPOINT}\nmodel: {EMBED_MODEL}\n")

# --- A. Cohere v2 documented multimodal shape: inputs[].content[] ---
print("[A] inputs with content[image_url]  (Cohere v2 documented shape)")
post({
    "model": EMBED_MODEL,
    "input_type": "search_document",
    "embedding_types": ["float"],
    "inputs": [{"content": [{"type": "image_url", "image_url": {"url": DATA_URL}}]}],
}, "A")

# --- B. Alternate 'image' content type ---
print("\n[B] inputs with content[image]  (alternate content type)")
post({
    "model": EMBED_MODEL,
    "input_type": "search_document",
    "embedding_types": ["float"],
    "inputs": [{"content": [{"type": "image", "image": DATA_URL}]}],
}, "B")

# --- C. Top-level images array (older Cohere v1-style) ---
print("\n[C] top-level images array  (older v1-style)")
post({
    "model": EMBED_MODEL,
    "input_type": "image",
    "embedding_types": ["float"],
    "images": [DATA_URL],
}, "C")

# --- D. Mixed text+image interleaved ---
print("\n[D] mixed text+image in one input")
post({
    "model": EMBED_MODEL,
    "input_type": "search_document",
    "embedding_types": ["float"],
    "inputs": [{"content": [
        {"type": "text", "text": "a red square"},
        {"type": "image_url", "image_url": {"url": DATA_URL}},
    ]}],
}, "D")

print("\nIf any variant returned dim=..., that's the shape multimodal needs.")
print("If all are 500 with no request id, multimodal is gated/unsupported on this route.")
print("If 400/422, payload shape needs adjustment - paste the error and we'll iterate.")
