# Meridian Confluence Agent

A trust-aware enterprise knowledge agent that finds the right Confluence page,
explains why it should be trusted, and warns when semantically relevant
documentation is stale, superseded, draft, or under review.

> **Portfolio safety:** Meridian Financial Group and its platforms are entirely
> fictional. The project uses a personal Confluence Cloud space and contains no
> employer or client data.

## Why this project exists

Confluence search can find pages containing the right words, but it cannot
reliably decide which conflicting procedure is authoritative. In the evaluation
corpus, a superseded access guide has a higher raw semantic score than the
canonical procedure. Meridian combines vector retrieval with explicit
governance metadata so the correct page wins for an explainable reason.

Example live result:

| Source | Raw semantic score | Trust adjustment | Final result |
|---|---:|---:|---:|
| Canonical procedure | 0.5691 | +0.25 | **0.8191 — recommended** |
| Under-review FAQ | 0.7340 | -0.15 | **0.5840 — warning** |
| Superseded guide | 0.7594 | -0.24 | **0.5194 — warning** |

The superseded page is the strongest semantic match, but the agent correctly
recommends the canonical procedure instead of blindly trusting similarity.

## What is implemented

- Personal Confluence Cloud REST v2 synchronization with cursor pagination
- Confluence storage XHTML-to-Markdown conversion
- Governance labels mapped to status, authority, type, and lifecycle metadata
- Heading-aware chunking with bounded overlap and stable citations
- Amazon Titan Text Embeddings V2 with 1,024-dimensional vectors
- PostgreSQL 16 with pgvector and HNSW cosine indexing
- Explainable trust-aware reranking and low-confidence rejection
- Grounded Llama 3.3 70B answers through Amazon Bedrock
- Custom MCP server with search, answer, conflict, and page-reading tools
- Tool-calling MCP agent with bounded steps and duplicate-call protection
- FastAPI endpoints, structured response contract, CORS, health, and readiness
- Incremental one-command knowledge refresh and safe source-scoped pruning
- Dockerized non-root backend plus PostgreSQL/pgvector
- Frozen 25-page adversarial evaluation corpus and **66 automated tests**

## Demonstrated performance

- Live Confluence refresh: **7 pages checked, 3 governed pages selected**
- Live knowledge corpus: **14 chunks**
- Unchanged refresh: **0 embeddings generated, 14 skipped**
- Typical semantic retrieval: approximately **0.2–0.3 seconds**
- End-to-end grounded answers: approximately **3–10 seconds**, depending on
  Bedrock on-demand model latency

## Portfolio resources

- [Architecture and security boundaries](docs/architecture.md)
- [Portfolio case study](docs/portfolio-case-study.md)
- [Two-minute demonstration script](docs/demo-script.md)
- [Interview explanation](docs/interview-story.md)
- [Screenshot checklist](docs/screenshots/README.md)

## Architecture

The production-style path synchronizes governed pages from a personal
Confluence Cloud space, embeds them with Amazon Titan, stores them in
PostgreSQL/pgvector, and generates grounded answers with Llama 3.3 through
Bedrock. A custom MCP server exposes search, answer, conflict, and page-reading
tools to the agent. See [docs/architecture.md](docs/architecture.md) for the
runtime and refresh diagrams, trust policy, and AWS deployment target.

## Containerized backend

The image runs FastAPI and its reusable MCP stdio subprocess as a non-root
user. PostgreSQL/pgvector remains a separate Compose service. `.env`, local
Confluence exports, credentials, and evaluation results are excluded from the
image build context.

For local Docker only, Compose mounts `~/.aws` read/write because `aws login`
refreshes its cached token. Production deployment must never mount developer
credentials and should use an ECS task role.

```bash
docker compose up -d --build
docker compose ps
curl http://127.0.0.1:8000/ready
```

Inspect logs and stop the containers without deleting PostgreSQL data:

```bash
docker compose logs -f api
docker compose down
```

## Stage 1 — lexical baseline

This stage intentionally uses no LLM, embeddings, vector database, LangChain,
or authority rules. A small BM25 implementation shows what keyword search can
retrieve and, crucially, what it cannot decide when pages conflict.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
python -m src.baseline_search "How do I obtain read-only Mosaic UI access?"
python -m eval.run_baseline
python -m unittest discover -s tests -v
```

The baseline is expected to retrieve both relevant and misleading pages. Later
stages must improve precision without hiding legitimate near-conflicts.

## Stage 2 — embedding fundamentals

This stage calls Titan Text Embeddings V2 directly through the Bedrock Runtime
API. It deliberately avoids LangChain and calculates cosine similarity in our
own code.

After configuring AWS credentials and enabling Bedrock model access:

```bash
pip install -e .
python -m experiments.embedding_similarity --region us-east-2
```

The experiment compares a semantic match, a keyword-adjacent VPN sentence, and
an unrelated hardware sentence. It prints vector dimensions, input token counts,
and pairwise cosine-similarity scores without printing the 1,024 float values.

## Stage 3 — heading-aware document chunking

This stage converts the 25 Markdown pages into embedding-ready JSON Lines. It
still avoids LangChain: headings define semantic boundaries, long sections are
split with controlled overlap, and every chunk retains the page metadata needed
later for authority filtering, conflict handling, and citations.

```bash
pip install -e .
python -m src.chunking --preview 5
python -m unittest discover -s tests -v
```

The generated `data/processed/chunks.jsonl` is reproducible build output. Each
record has two content fields: `text` is the original section content, while
`embedding_text` adds the page title and heading path so the embedding retains
context even when the chunk is retrieved by itself.

## Stage 4 — pgvector ingestion and semantic retrieval

PostgreSQL 16 plus pgvector runs in Docker; Titan remains in Bedrock. The table
stores chunk text, provenance metadata, a content fingerprint, and a
1,024-dimensional vector. An HNSW cosine index demonstrates approximate nearest
neighbor indexing, although PostgreSQL may prefer an exact scan for this tiny
152-row corpus.

Create a local configuration and replace both password placeholders with the
same development-only password:

```bash
cp .env.example .env
docker compose up -d
docker compose ps
```

Generate the chunks, install dependencies, and ingest them:

```bash
python -m src.chunking --preview 0
python -m pip install -e .
python -m src.ingest --region us-east-2 --limit 5
# After inspecting the five rows:
python -m src.ingest --region us-east-2
```

Ingestion is restart-safe. A SHA-256 fingerprint includes the embedding model,
dimensions, and exact embedding input. Unchanged rows are skipped, while changed
chunks are re-embedded and upserted one transaction at a time.

Run semantic retrieval:

```bash
python -m src.vector_search \
  "How do I obtain read-only access to the Mosaic customer console?" \
  --region us-east-2 --limit 5
```

### DBeaver connection

Use PostgreSQL with host `localhost`, port from `.env` (default `5432`), database
`meridian_rag`, and the username/password from `.env`. Useful inspection SQL:

```sql
SELECT COUNT(*) FROM document_chunks;

SELECT page_id, title, section_path, input_token_count, updated_at
FROM document_chunks
ORDER BY page_id, chunk_id;
```

Stop the database without deleting its named volume using `docker compose down`.
Do not use `docker compose down -v` unless you intentionally want to erase the
local database.

## Stage 5 — explainable trust-aware reranking

Raw vector similarity finds semantically relevant chunks but can rank a stale
page above the canonical procedure. This stage retrieves a wider candidate set
and then applies a bounded, visible metadata adjustment based on status,
authority, document type, freshness, and explicit `supersedes` relationships.
It also caps repeated chunks from one page and prints every scoring reason and
warning. Conflicting pages remain visible instead of being silently removed.

```bash
python -m src.trusted_search \
  "How do I obtain read-only access to the Mosaic customer console?" \
  --region us-east-2 --retrieve 15 --limit 5
```

The weights are deliberately policy code rather than an LLM judgment. This
makes the behavior deterministic, testable, auditable, and easy to replace with
organization-specific governance rules later.

## Stage 6 — manual RAG answer generation

This stage completes the first RAG loop without LangChain. It embeds the user
question, retrieves 8 candidates, reranks them, separates recommended evidence
from conflicting/stale evidence, constructs the prompt explicitly, and calls
Llama 3.3 70B through Bedrock Converse. The default is the US geo inference
profile `us.meta.llama3-3-70b-instruct-v1:0`, which can be invoked from
`us-east-2`.

```bash
python -m src.rag_answer \
  "How do I obtain read-only access to the Mosaic customer console?" \
  --region us-east-2 --show-context
```

Generation uses temperature `0.1` and a 250-token output limit. The system
prompt requires `[page-XX]` citations, treats retrieved text as untrusted data,
and forbids mixing conflicting procedures into the recommended answer. A small
post-generation validator reports missing or unknown citations. Progress and
per-stage latency are printed, and Bedrock calls use bounded timeouts and
retries so a transient service issue does not leave the CLI hanging silently.

## Stage 7 — deterministic RAG evaluation

The evaluation suite runs the same reusable RAG pipeline as the CLI against
seven adversarial cases. It covers a stale unlabelled page, a draft conflict,
a stale parent/current child pair, legitimate department-level variation, a
valid emergency procedure that is wrong for a routine request, an audit report,
and an unfinished FAQ. This is deliberately not an LLM-as-judge benchmark:
the first version uses transparent expected sources, answer terms, citations,
and conflict rules so every pass or failure is explainable.

Start with one inexpensive case:

```bash
python -m eval.run_rag_evaluation \
  --region us-east-2 \
  --case mosaic-new-engineer
```

Then run all seven cases (seven Titan calls and seven Llama calls):

```bash
python -m eval.run_rag_evaluation --region us-east-2
```

The evaluator writes machine-readable JSON and an interview-friendly Markdown
report under `eval/results/`. It records relevant-source retrieval, preferred
top result, misleading top-result avoidance, required answer facts, required
citations, conflict detection, citation grounding, latency, and token usage.

## Stage 8 — structured HTTP API

FastAPI exposes the evaluated pipeline without duplicating its RAG logic. The
blocking boto3 and psycopg work runs in a thread pool so it does not block the
async web event loop. Responses include citations, deduplicated recommended and
conflicting sources, explainable scores, validation warnings, token usage, and
per-stage latency.

```bash
python -m pip install -e '.[test]'
python -m src.run_api
```

Open `http://127.0.0.1:8000/docs` for the generated OpenAPI interface, or test
from another terminal:

```bash
curl -s http://127.0.0.1:8000/health

curl -s -X POST http://127.0.0.1:8000/ask \
  -H 'Content-Type: application/json' \
  -d '{"question":"How do I obtain read-only access to Mosaic UI?"}'
```

`GET /health` is a liveness check. `GET /ready` verifies PostgreSQL is
reachable. Invalid request fields receive FastAPI's structured `422` response;
dependency failures are sanitized instead of exposing credentials or internal
exception details.

## Stage 10 — MCP AI client and manual agent loop

The terminal client is now an MCP host: it starts the Meridian MCP server over
stdio, discovers its tools dynamically, converts their JSON schemas to Bedrock
Converse tool specifications, and lets Llama choose and invoke tools. The loop
is implemented directly instead of through LangChain so tool requests,
`toolResult` messages, limits, and error handling remain visible.

```bash
docker compose up -d
aws login
python -m src.mcp_agent \
  "How do I obtain read-only access to the Mosaic customer console?" \
  --region us-east-2
```

Omit the question for an interactive session. Diagnostic tool-call messages go
to stderr; the final conversational answer goes to stdout. The client only
launches the fixed local `src.mcp_server` module and caps the loop at four model
steps by default.

## Stage 11 — HTTP adapter for the MCP agent

The API exposes `POST /agent/ask` for browser and portfolio UI clients. The
backend—not the browser—owns the MCP stdio process, Bedrock credentials, tool
loop, and safety limit. Its structured response includes the final answer,
citations, collected sources, every tool call and duration, cumulative model
tokens, and total latency. The original deterministic `POST /ask` RAG endpoint
remains available for side-by-side comparison.

```bash
python -m src.run_api

curl -s -X POST http://127.0.0.1:8000/agent/ask \
  -H 'Content-Type: application/json' \
  -d '{"question":"Are there outdated Mosaic access instructions?"}'
```

## Stage 12 — reusable MCP session and latency guard

FastAPI now starts one MCP stdio subprocess during application startup and
reuses that session for every `/agent/ask` request. This removes repeated MCP
and Python startup work from the request path. Shutdown closes the child process
cleanly. Agent responses expose `mcp_startup`, cumulative Bedrock `model`, MCP
`tools`, and end-to-end `total` timings in milliseconds.

Requests are bounded by `AGENT_TIMEOUT_SECONDS` (60 seconds by default). A
stalled model or tool returns HTTP `504` instead of leaving the browser loading
indefinitely. `GET /ready` now verifies PostgreSQL and reports the MCP connection
state.

## Stage 13 — Confluence Cloud REST connector

The connector reads a **personal/demo Confluence Cloud space** through REST API
v2, follows cursor pagination, retries bounded 429/5xx responses, converts
Confluence storage XHTML into retrieval-friendly Markdown, and writes it to
`data/confluence_pages`. It never writes credentials into generated pages and
does not overwrite the frozen evaluation corpus in `data/raw_pages`.

Create an API token for your personal Atlassian account and add these values to
the local `.env` (never commit that file):

```dotenv
CONFLUENCE_BASE_URL=https://your-site.atlassian.net
CONFLUENCE_EMAIL=you@example.com
CONFLUENCE_API_TOKEN=your-personal-api-token
CONFLUENCE_SPACE_ID=123456
```

Validate access without writing, then synchronize:

```bash
python -m src.confluence_sync --dry-run
python -m src.confluence_sync
python -m src.chunking \
  --corpus data/confluence_pages \
  --output data/processed/confluence_chunks.jsonl
python -m src.ingest \
  --chunks data/processed/confluence_chunks.jsonl \
  --region us-east-2
```

Atlassian IDs become source IDs such as `conf-123456`, so live pages retain
stable citations across re-syncs. Unchanged Markdown and unchanged embeddings
are skipped by the sync and ingestion fingerprint checks respectively.

## Stage 15 — source-scoped retrieval

Static evaluation pages and synchronized Confluence pages can coexist in the
same pgvector table without producing duplicate results. Search and answer CLIs
accept `--source all|confluence_cloud|frozen_corpus`. The HTTP API and MCP
server read `RAG_SOURCE_SCOPE`, which defaults to `confluence_cloud`; the
evaluation runner explicitly uses `frozen_corpus`.

```bash
python -m src.trusted_search \
  "How do I obtain read-only Mosaic access?" \
  --region us-east-2 \
  --source confluence_cloud \
  --retrieve 20 \
  --limit 8

python -m src.rag_answer \
  "How do I obtain read-only Mosaic access?" \
  --region us-east-2 \
  --source confluence_cloud
```

## Stage 16 — one-command knowledge refresh

The refresh command synchronizes the configured Confluence space, excludes
unlabeled templates, chunks governed pages, embeds only changed chunks, and
prunes obsolete rows only from the `confluence_cloud` source. The frozen
evaluation corpus is never modified.

```bash
python -m src.refresh_knowledge --region us-east-2
```

Use `--no-prune` when diagnosing a refresh and you want to retain obsolete live
chunks temporarily.

### Low-confidence rejection

The pipeline uses the best **raw semantic similarity** as a relevance gate
before metadata reranking. If no retrieved chunk reaches `0.30`, it returns
`status: insufficient_evidence`, no citations or sources, zero generation
tokens, and does not invoke Llama. This prevents authority metadata from making
an irrelevant page appear relevant. The threshold can be calibrated with the
evaluation corpus and configured through `RAG_MINIMUM_SIMILARITY`.

## Stage 9 — custom MCP server

The official MCP Python SDK v2 exposes the existing knowledge services through
the protocol rather than rebuilding RAG inside the server. The first transport
is local `stdio`, which works with MCP hosts that launch local subprocesses.

- `search_knowledge`: retrieval and trust reranking without Llama
- `answer_question`: complete grounded RAG answer
- `get_page_details`: exact page content and governance metadata
- `check_document_conflicts`: stale/draft/superseded/review warnings
- `meridian://pages/{page_id}`: read-only MCP resource

```bash
python -m pip install -e '.[test]'
python -m src.mcp_server
```

A healthy stdio server appears to wait silently because stdout is reserved for
MCP JSON-RPC messages. Inspect it with the official development command:

```bash
python -m experiments.mcp_smoke_test
mcp dev src/mcp_server.py
```

An MCP host can launch it using the project virtual environment:

```json
{
  "mcpServers": {
    "meridian-confluence": {
      "command": "/ABSOLUTE/PATH/meridian-confluence-agent/.venv/bin/python",
      "args": ["-m", "src.mcp_server"],
      "cwd": "/ABSOLUTE/PATH/meridian-confluence-agent"
    }
  }
}
```
