# Cohere Lab 2: Build Notes and Teaching Takeaways

Living document. Two purposes:
1. Track build decisions and technical facts.
2. Capture the learnings, because what we learned building this is exactly what
   we want the attendees to learn from the lab.

## Status
- Environment: working (Windows, venv, REST routes confirmed)
- Notebook 0 (setup): runs clean
- Notebook 1 (embed): runs clean after batching fix, produces (153, 1536)
- Notebook 2 (vector search): runs clean, results captured
- Notebook 3 (rerank): runs clean, before/after captured, lift confirmed
- Sidecar instructions: drafted (SIDECAR_INSTRUCTIONS.md)

==================================================================
## TEACHING TAKEAWAYS (what attendees should leave understanding)
==================================================================

These are the real lessons, framed for learners. They map directly to what we
discovered building the lab.

1. **Embeddings search by meaning, not keywords.** Embed-v4 maps text to a
   1536-dimensional vector; similar meanings land near each other. This already
   beats keyword search.

2. **Vector search is a strong first pass, but coarse.** It can rank a near-miss
   (shares vocabulary, wrong topic) above the genuinely correct answer, and can
   miss the right answer entirely when it is worded differently from the query.
   We saw this on 4 of 5 demo queries.

3. **Rerank does two things, not one.** It reorders (correct answers climb) AND
   it sharpens confidence (scores move from a vague 0.3-0.4 band to 0.9+ with
   clear separation). The confidence jump is as important as the reordering.

4. **Rerank rescues hard cases without breaking easy ones.** On the deployment
   query, vector search already ranked the answer first; rerank kept it first.
   Not every query needs rerank. Its production value is fixing the hard cases
   while doing no harm to the easy ones. An honest, mixed result is more credible
   than a uniformly dramatic one.

5. **The production recipe is embed -> vector search -> rerank.** This is the
   foundation of high-quality retrieval and good RAG.

6. **Scale changes the vector store, not the model calls.** NumPy is fine for a
   small corpus; production uses FAISS or Azure AI Search. The Embed and Rerank
   calls are identical at any scale.

7. **On Foundry, Cohere is called via REST, not the Foundry SDK.** The SDK is
   built on the OpenAI-compatible API, which has no rerank concept. The Cohere
   v2 REST routes on the Foundry endpoint do everything. (Audience-relevant when
   they go build this themselves.)

==================================================================
## Confirmed technical facts (build reference)
==================================================================
- Route: <endpoint>/providers/cohere/v2/{embed,rerank}. The /v1 path 404s.
- Foundry SDK cannot do rerank or Cohere multimodal embed. REST is the path.
- Both models share one endpoint + key; model name differs per call.
- Deploy as Direct from Azure, Global Standard (not Managed compute).
- Embed endpoint has a per-request batch limit (~96); helper batches at 90.
- Multimodal embed works with a properly sized image (32x32+); 2x2 returns 500.
- Multimodal needs a valid base64 data URI in the v2 inputs[].content[] shape.
- Rerank is text-to-text only; no image inputs.

## Timing (for the sidecar)
- Kernel restart: ~0.1s
- Notebook 1 (embed full corpus): ~20-30s
- Notebooks 2 and 3: a few seconds per query
- Cell status: [n]=done, spinner=running, Pending=queued/kernel starting.
- Long output shows a truncation notice; click "scrollable element".

## Notebook 3 results (rerank before/after, live endpoint)
Q1 login: correct #2 (0.383) -> #1 (0.949). Modest rank move, big confidence gain.
Q2 billing: correct #3 (0.430) -> #1 (0.898).
Q3 deployment: correct #1 (0.442) -> #1 (0.911). Already solved; no harm done.
Q4 data export: correct #3 (0.472) -> #1 (0.959). Leapfrogged two near-misses.
Q5 rate limit: correct NOT in top 5 -> #2 (0.828). Strongest case, full rescue.

## Build changes made
- Section "the wow moment" renamed to "The lift".
- embed_texts now batches at 90 (was failing with 400 on the full 153 at once).
- Connection test rewritten for shared endpoint (one endpoint+key, model per call).
- Route corrected from /v1/embed to /providers/cohere/v2/embed.
- Notebook 3 "Your turn" cell: added an inline comment and a markdown example so
  it is clear the quoted string is what the learner edits.
- Notebooks 2 and 3: added explanation that each notebook runs in its own session
  and re-loads what it needs (why imports and loads repeat).
- "What you learned" lives in both the notebook (brief recap) and the sidecar
  (fuller version). Not duplicated verbatim.

## Design decisions
- Attendee exercise: open a random corpus file, add a related query to the end of
  demo_queries, re-run. Carry that query from Notebook 2 into Notebook 3.
- Sidecar carries the conceptual teaching; notebooks stay lean and runnable.

## Open items
- Q1 tuning: leave as-is (confidence story carries it) vs bury deeper for rank
  drama. Current lean: leave.
- Multimodal in/out of v1: decide with Nitya/Mo'Shai.
- Build remains: integrate with Lab 1, full run-through, Cohere/Nitya/QA review.
