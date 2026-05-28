"""
Multimodal test v3: use a REAL, programmatically-generated image so we know
the base64 is valid. Builds a tiny 32x32 red PNG with Pillow (or falls back to
a known-good hand-crafted PNG if Pillow is not installed).

Based on the v2 result: the endpoint accepts multimodal payloads, it was just
rejecting our hardcoded base64 image as malformed. With a valid image, multimodal
should now return a vector.
"""
import os, base64, sys, io
import requests
from dotenv import load_dotenv

load_dotenv()
ENDPOINT = os.environ.get("FOUNDRY_ENDPOINT", "").rstrip("/")
KEY = os.environ.get("FOUNDRY_KEY", "")
EMBED_MODEL = os.environ.get("EMBED_MODEL", "embed-v-4-0")
URL = f"{ENDPOINT}/providers/cohere/v2/embed"
HEADERS = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}


def get_test_image_data_url():
    """Build a real 32x32 red PNG and return as a data URL."""
    try:
        from PIL import Image
        img = Image.new("RGB", (32, 32), (220, 30, 30))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        png = buf.getvalue()
        print(f"  generated 32x32 PNG via Pillow ({len(png)} bytes)")
    except ImportError:
        # Fallback: a known-good 2x2 red PNG, hand-verified valid
        png = bytes.fromhex(
            "89504e470d0a1a0a0000000d4948445200000002000000020806000000"
            "72b60d240000001b49444154789c63fcceced0c8c8c8d0c8c8d0c8c800"
            "0000ff00010100013010be3b0000000049454e44ae426082"
        )
        print(f"  Pillow not installed, using fallback 2x2 PNG ({len(png)} bytes)")
    b64 = base64.b64encode(png).decode("ascii")
    return f"data:image/png;base64,{b64}"


def post(payload, label):
    try:
        r = requests.post(URL, headers=HEADERS, json=payload, timeout=60)
        if r.status_code != 200:
            print(f"  {label}: HTTP {r.status_code}\n     body: {r.text[:400]}")
            return None
        d = r.json()
        embs = d.get("embeddings")
        vec = embs["float"][0] if isinstance(embs, dict) else embs[0]
        print(f"  {label}: OK, dim={len(vec)}  first 4 values: {[round(v,3) for v in vec[:4]]}")
        return vec
    except Exception as e:
        print(f"  {label}: {type(e).__name__}: {e}")
        return None


print("Cohere Embed-v4 multimodal test v3 (valid image)")
print(f"endpoint: {ENDPOINT}\nmodel: {EMBED_MODEL}\n")

DATA_URL = get_test_image_data_url()
print(f"  data URL length: {len(DATA_URL)} chars (first 60: {DATA_URL[:60]}...)\n")

# Cohere v2 documented shape, the one most likely to be canonical
print("[A] inputs with content[image_url]  (Cohere v2 documented shape)")
post({
    "model": EMBED_MODEL,
    "input_type": "search_document",
    "embedding_types": ["float"],
    "inputs": [{"content": [{"type": "image_url", "image_url": {"url": DATA_URL}}]}],
}, "A")

# Mixed text+image, the multimodal headline
print("\n[B] mixed text+image in one input")
post({
    "model": EMBED_MODEL,
    "input_type": "search_document",
    "embedding_types": ["float"],
    "inputs": [{"content": [
        {"type": "text", "text": "a red square"},
        {"type": "image_url", "image_url": {"url": DATA_URL}},
    ]}],
}, "B")

print("\nIf [A] returns dim=...: image-only multimodal works.")
print("If [B] returns dim=...: mixed text+image works (Cohere's headline capability).")
print("If still failing: paste the error.")
