"""
Embed a REAL image file with Cohere Embed-v4 on Foundry.
Drop any .png/.jpg next to this script and pass its name as an argument:
   python test_real_image.py mychart.png
   python test_real_image.py "C:\path\to\screenshot.jpg"

Demonstrates:
  - reading a real image from disk
  - encoding it as a base64 data URL
  - embedding it with Embed-v4
  - embedding a TEXT query and computing cosine similarity to the image
    (a tiny image-text similarity demo, the foundation of image search)
"""
import os, sys, base64, mimetypes
import requests
import numpy as np
from dotenv import load_dotenv

load_dotenv()
ENDPOINT = os.environ.get("FOUNDRY_ENDPOINT", "").rstrip("/")
KEY = os.environ.get("FOUNDRY_KEY", "")
EMBED_MODEL = os.environ.get("EMBED_MODEL", "embed-v-4-0")
URL = f"{ENDPOINT}/providers/cohere/v2/embed"
HEADERS = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}


def image_to_data_url(path):
    """Read an image file and return a base64 data URL."""
    mime, _ = mimetypes.guess_type(path)
    if mime not in ("image/png", "image/jpeg", "image/jpg", "image/webp", "image/gif"):
        mime = "image/png"  # fallback guess
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    return f"data:{mime};base64,{b64}"


def embed_image(data_url, input_type="search_document"):
    """Embed a single image. Returns a NumPy vector."""
    payload = {
        "model": EMBED_MODEL,
        "input_type": input_type,
        "embedding_types": ["float"],
        "inputs": [{"content": [{"type": "image_url", "image_url": {"url": data_url}}]}],
    }
    r = requests.post(URL, headers=HEADERS, json=payload, timeout=60)
    r.raise_for_status()
    embs = r.json()["embeddings"]
    vec = embs["float"][0] if isinstance(embs, dict) else embs[0]
    return np.array(vec, dtype=np.float32)


def embed_text(text, input_type="search_query"):
    """Embed a single text. Returns a NumPy vector."""
    payload = {
        "model": EMBED_MODEL,
        "input_type": input_type,
        "embedding_types": ["float"],
        "texts": [text],
    }
    r = requests.post(URL, headers=HEADERS, json=payload, timeout=60)
    r.raise_for_status()
    embs = r.json()["embeddings"]
    vec = embs["float"][0] if isinstance(embs, dict) else embs[0]
    return np.array(vec, dtype=np.float32)


def cosine(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_real_image.py <path-to-image>")
        print("Tip: put any png/jpg in this folder and pass its name.")
        sys.exit(1)
    path = sys.argv[1]
    if not os.path.exists(path):
        print(f"File not found: {path}")
        sys.exit(1)
    size_kb = os.path.getsize(path) / 1024
    print(f"Embedding: {path}  ({size_kb:.1f} KB)")
    data_url = image_to_data_url(path)

    print("\n[1] Embedding the image...")
    img_vec = embed_image(data_url)
    print(f"    image vector dim = {len(img_vec)}, first 4 = {[round(v,3) for v in img_vec[:4]]}")

    # Image-text similarity demo: embed a few text descriptions and compare
    print("\n[2] Embedding three candidate text descriptions...")
    candidates = [
        "a chart or diagram",
        "a photograph of a person",
        "a screenshot of a user interface",
    ]
    text_vecs = [embed_text(c) for c in candidates]

    print("\n[3] Cosine similarity image-to-text (higher = more similar):")
    pairs = sorted(zip(candidates, text_vecs), key=lambda p: -cosine(img_vec, p[1]))
    for text, vec in pairs:
        s = cosine(img_vec, vec)
        print(f"    {s:+.3f}  {text}")

    print("\nThe top match is what the model thinks the image is most like.")
    print("With more candidates (or a corpus of pre-embedded images), this becomes image search.")
