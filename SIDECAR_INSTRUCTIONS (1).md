# Skillable Sidecar Instructions: Cohere Lab 2

This is the right-side instruction panel content, mapped to each notebook and step.
Left side = the VM with VS Code and the notebooks. Right side = these instructions.
Written for the learner. The presenter (Microsoft) can also narrate from this.

================================================================
## Before you start (intro panel)
================================================================

In this lab you will build a smarter search over a customer support knowledge
base using two Cohere models on Microsoft Foundry:

- **Embed-v4** turns text into vectors so you can search by meaning, not keywords.
- **Rerank-v4** reorders search results so the best answer rises to the top.

You will work through four notebooks in order. Open them from the `lab` folder
in VS Code on the left.

**How to run a cell:** click it and press Shift+Enter, or use the run arrow.

**Reading cell status:**
- `[1]` (a number) means the cell finished.
- A spinner means it is running; wait for it.
- `Pending` means it is queued or the kernel is still starting. If it stays
  Pending more than a few seconds, click **Restart** at the top and run again.

**If output looks cut off:** you may see "Output is truncated." Click
"scrollable element" to see all of it. This is normal for long output.

================================================================
## Notebook 0: Setup and Validate  (about 5 minutes)
================================================================

**What you are doing:** confirming your environment works before building anything.

1. Open `00-setup.ipynb`. Confirm the kernel (top-right) shows the lab's Python
   environment. If it says "Select Kernel," choose it first.
2. Run cell 1 (imports). You should see the endpoint and model names print.
3. Run cell 2 (load corpus). You should see "Loaded 153 documents" and an example.
4. Run cell 3 (embed test). You should see an embedding shape of (1, 1536).
5. Run cell 4 (rerank test). The password document should rank first.

**Checkpoint:** if all four ran without error, you are ready. If anything fails,
re-run from the top, or restart the kernel.

**Teaching point:** an embedding is a list of 1536 numbers that represents the
meaning of a piece of text. That is the foundation for everything that follows.

================================================================
## Notebook 1: Embed the Corpus  (about 10 minutes)
================================================================

**What you are doing:** converting all 153 support documents into vectors.

1. Open `01-embed.ipynb`.
2. Run cell 1 (load corpus).
3. Run cell 2 (build text). It prints the first document as an example.
4. Run cell 3 (embed). This calls Embed-v4 for all documents and takes about
   20 to 30 seconds. The service accepts a limited number of texts per request,
   so the code automatically sends them in batches; this is normal.
5. Run cell 4 (save). It writes `doc_vectors.npy` to your folder.

**Teaching point:** documents with similar meaning end up near each other in
vector space. We save the vectors so the next notebooks can search them instantly
without re-embedding.

**Why save to a file:** each notebook runs in its own session and does not share
memory with the others. The saved file is how the vectors pass from this notebook
to the next ones.

================================================================
## Notebook 2: Baseline Vector Search  (about 15 minutes)
================================================================

**What you are doing:** searching with vectors alone, and finding where it falls short.

1. Open `02-vector-search.ipynb`.
2. Run cell 1 (load). Re-loads the corpus and the saved vectors. (Each notebook
   re-loads what it needs; nothing carries over automatically.)
3. Run cell 2 (display helper).
4. Run cell 3 (single query). Look at the top 5 for the login query. Notice the
   genuinely correct answer is not always ranked first.
5. Run cell 4 (all five demo queries). Read the results carefully.

**What to notice:** for several queries, a document that shares words with the
query ranks high, while the correct answer (worded differently) ranks lower.
Vector search understands meaning, but it can still be fooled by surface wording.

**Your turn (do this):** scroll the documents, pick any topic, and add your own
question about it to the end of the `demo_queries` list in cell 4. Re-run the
cell. Where does the right document land? Keep this query for Notebook 3.

**Teaching point:** semantic search is a big step up from keyword search, but it
is a single coarse pass. The next notebook shows how to fix its mistakes.

================================================================
## Notebook 3: Rerank, The Lift  (about 20 minutes)
================================================================

**What you are doing:** applying Rerank-v4 and measuring the improvement.

1. Open `03-rerank.ipynb`.
2. Run cell 1 (load).
3. Run cell 2 (define the before-and-after function).
4. Run cell 3 (all five queries, before and after). This is the core of the lab.
5. Run cell 4 (your turn). Replace the text inside the quotes with your own
   question, then run it.

**What to notice (two things, not one):**
- **The ranking changes:** correct answers climb. For the rate-limit query,
  vector search missed the right answer entirely; rerank rescues it.
- **The scores sharpen:** vector search scores cluster in a vague 0.3 to 0.4 band.
  Rerank scores jump to 0.9+ with clear separation. Rerank turns "these all seem
  vaguely relevant" into "this one, definitively."

**The honest result:** one query (deployment) was already correct in vector
search. Rerank keeps it correct and does no harm. Not every query needs rerank;
its value is rescuing the hard cases without breaking the easy ones. That is what
makes it production-grade.

**Your turn (do this):** in cell 4, change the quoted question to your own, ideally
the one you added in Notebook 2. Phrase it the way a frustrated customer would,
with different words than the documentation. Watch rerank handle the mismatch.

================================================================
## Wrap-up panel: What you learned
================================================================

- **Embed-v4** turns text into vectors for fast semantic search by meaning.
- **Vector search** is a strong first pass but coarse: it can rank near-misses
  high, and sometimes misses the right answer entirely.
- **Rerank-v4** reads the query and each document together and fixes the ordering,
  with high confidence. Scores move from an ambiguous 0.3 to 0.4 band to 0.9+.
- **Rerank rescues the hard cases without breaking the easy ones.**
- The pattern **embed, then vector search, then rerank** is the production recipe
  for high-quality retrieval, and the foundation of good RAG.

**Scaling beyond the lab:** we used NumPy for vector search because the corpus is
small. At production scale (millions of documents) you would use a vector database
such as FAISS or Azure AI Search. The Embed and Rerank calls stay exactly the same.

**One technical note worth remembering:** these Cohere models are called on
Foundry through the Cohere v2 REST routes, not the OpenAI-compatible Foundry SDK.
The SDK does not support reranking. This is expected, and the lab shows the
correct pattern.
