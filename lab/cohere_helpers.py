"""
Shared helpers for the Cohere retrieval lab.
REST calls to the Foundry endpoint + tiny NumPy vector-search utilities.
"""
import os
import requests
import numpy as np
from dotenv import load_dotenv

load_dotenv()

ENDPOINT = os.environ.get("FOUNDRY_ENDPOINT", "").rstrip("/")
KEY = os.environ.get("FOUNDRY_KEY", "")
EMBED_MODEL = os.environ.get("EMBED_MODEL", "embed-v-4-0")
RERANK_MODEL = os.environ.get("RERANK_MODEL", "Cohere-rerank-v4.0-pro")

EMBED_URL = f"{ENDPOINT}/providers/cohere/v2/embed"
RERANK_URL = f"{ENDPOINT}/providers/cohere/v2/rerank"
HEADERS = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}

# Cohere embed accepts a limited number of texts per request. Batch to stay under it.
EMBED_BATCH_SIZE = 90


def _embed_batch(texts, input_type):
    payload = {
        "model": EMBED_MODEL,
        "texts": texts,
        "input_type": input_type,
        "embedding_types": ["float"],
    }
    r = requests.post(EMBED_URL, headers=HEADERS, json=payload, timeout=60)
    r.raise_for_status()
    embs = r.json()["embeddings"]
    return embs["float"] if isinstance(embs, dict) else embs


def embed_texts(texts, input_type="search_document"):
    """Embed a list of texts with Embed-v4, batching to respect the API limit.
    Returns a NumPy array (n, dim)."""
    all_vectors = []
    for i in range(0, len(texts), EMBED_BATCH_SIZE):
        batch = texts[i:i + EMBED_BATCH_SIZE]
        all_vectors.extend(_embed_batch(batch, input_type))
    return np.array(all_vectors, dtype=np.float32)


def rerank(query, documents, top_n=5):
    """Rerank documents against the query with Rerank-v4.
    Returns list of {index, relevance_score} sorted best-first."""
    payload = {
        "model": RERANK_MODEL,
        "query": query,
        "documents": documents,
        "top_n": top_n,
    }
    r = requests.post(RERANK_URL, headers=HEADERS, json=payload, timeout=60)
    r.raise_for_status()
    return r.json()["results"]


def cosine_search(query_vec, doc_matrix, top_k=10):
    """Plain NumPy cosine similarity search.
    Returns list of (doc_index, score) sorted best-first."""
    q = query_vec / (np.linalg.norm(query_vec) + 1e-9)
    d = doc_matrix / (np.linalg.norm(doc_matrix, axis=1, keepdims=True) + 1e-9)
    sims = d @ q
    order = np.argsort(sims)[::-1][:top_k]
    return [(int(i), float(sims[i])) for i in order]
