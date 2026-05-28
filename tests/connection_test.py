"""
Cohere on Azure Foundry - connection test (shared Foundry resource)
====================================================================
Embed-v4 and Rerank-v4 deployed under one Foundry resource from Alejandro (Global Standard).
Shared endpoint + key. Model name per call.

KEY ROUTING FACT (confirmed): Cohere models under a Foundry resource use
    https://<resource>.services.ai.azure.com/providers/cohere/v2/embed
    https://<resource>.services.ai.azure.com/providers/cohere/v2/rerank
NOT /v1/embed. The Cohere SDK hardcodes /v1/... so REST is the reliable path here.

.env:
    FOUNDRY_ENDPOINT=https://<resource>.services.ai.azure.com
    FOUNDRY_KEY=<key>
    EMBED_MODEL=embed-v-4-0
    RERANK_MODEL=Cohere-rerank-v4.0-pro
"""
import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()
ENDPOINT = os.environ.get("FOUNDRY_ENDPOINT", "").rstrip("/")
KEY = os.environ.get("FOUNDRY_KEY", "")
EMBED_MODEL = os.environ.get("EMBED_MODEL", "embed-v-4-0")
RERANK_MODEL = os.environ.get("RERANK_MODEL", "Cohere-rerank-v4.0-pro")

DOCS = [
    "Reset your password from the account settings page.",
    "Our billing cycle runs monthly and invoices are sent on the first.",
    "To deploy a model, open the Foundry portal and select the model catalog.",
]
QUERY = "how do I change my password"

# Candidate route prefixes to try, in order. The first that works wins.
EMBED_ROUTES = ["/providers/cohere/v2/embed", "/v2/embed", "/v1/embed"]
RERANK_ROUTES = ["/providers/cohere/v2/rerank", "/v2/rerank", "/v1/rerank"]


def check_env():
    miss = [k for k, v in {"FOUNDRY_ENDPOINT": ENDPOINT, "FOUNDRY_KEY": KEY}.items() if not v]
    if miss:
        print(f"FAIL: missing env vars: {', '.join(miss)}")
        sys.exit(1)
    print(f"endpoint: {ENDPOINT}")
    print(f"embed model:  {EMBED_MODEL}")
    print(f"rerank model: {RERANK_MODEL}")


def try_routes(routes, payload, label):
    headers = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}
    last = None
    for route in routes:
        url = f"{ENDPOINT}{route}"
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=30)
            if r.status_code == 404:
                print(f"  {label}: 404 at {route}, trying next route...")
                last = r
                continue
            r.raise_for_status()
            print(f"  {label}: ok via {route}")
            return r.json(), route
        except requests.HTTPError as e:
            print(f"  {label}: {r.status_code} at {route}: {r.text[:160]}")
            last = r
            # 500 often means model-name mismatch; stop and report
            if r.status_code == 500:
                break
        except Exception as e:
            print(f"  {label}: {type(e).__name__} at {route}: {e}")
    return None, None


def main():
    print("Cohere on Azure Foundry: connection test (providers/cohere/v2 routes)")
    check_env()

    print("\n--- EMBED ---")
    embed_payload = {"model": EMBED_MODEL, "texts": DOCS,
                     "input_type": "search_document", "embedding_types": ["float"]}
    edata, eroute = try_routes(EMBED_ROUTES, embed_payload, "EMBED")
    if edata:
        embs = edata.get("embeddings")
        dim = len(embs["float"][0]) if isinstance(embs, dict) else len(embs[0])
        print(f"  EMBED PASS: {len(DOCS)} docs, dim={dim}, route={eroute}")

    print("\n--- RERANK ---")
    rerank_payload = {"model": RERANK_MODEL, "query": QUERY, "documents": DOCS, "top_n": 3}
    rdata, rroute = try_routes(RERANK_ROUTES, rerank_payload, "RERANK")
    if rdata:
        top = rdata["results"][0]
        print(f"  RERANK PASS: top index={top['index']}, score={top['relevance_score']:.3f} "
              f"(expect index 0), route={rroute}")

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  EMBED:  {'PASS via ' + eroute if edata else 'FAIL'}")
    print(f"  RERANK: {'PASS via ' + rroute if rdata else 'FAIL'}")
    if edata and rdata:
        print("\nBoth working. Use these routes in the notebooks.")
        print("Note: Cohere SDK hardcodes /v1, so REST is the reliable path on Foundry.")
    else:
        print("\nIf 500: model name likely mismatched, must match the deployment name")
        print("exactly (casing + hyphens), e.g. Cohere-rerank-v4.0-pro.")
        print("If all 404: check the deployment's endpoint URL in the portal (known UI quirk).")


if __name__ == "__main__":
    main()
