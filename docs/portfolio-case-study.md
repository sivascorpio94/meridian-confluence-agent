# Portfolio Case Study

## The problem

Enterprise Confluence spaces accumulate current procedures, old guides, draft
pages, FAQs, audits, and duplicated terminology. Keyword search returns a list
of pages, and vector search improves semantic matching, but neither guarantees
that the first result is safe to follow.

Meridian models a realistic access question: a new engineer needs read-only
Mosaic UI access. The knowledge base contains a canonical ServiceNow procedure,
an under-review FAQ, and a superseded email-based guide. The obsolete guide is
more semantically similar to the question than the canonical procedure.

## My approach

I built the system progressively so every abstraction remained observable:

1. Established a BM25 keyword baseline.
2. Called Titan embeddings directly and measured cosine similarity.
3. Implemented heading-aware chunking without a RAG framework.
4. Stored vectors and provenance metadata in PostgreSQL/pgvector.
5. Added bounded, explainable governance-aware reranking.
6. Built the grounded prompt manually and separated recommended evidence from
   conflicting evidence.
7. Added deterministic evaluation before introducing an agent loop.
8. Exposed the capabilities as MCP tools and connected a Bedrock tool-calling
   client.
9. Connected a personal Confluence Cloud space and implemented incremental
   refresh, source isolation, and safe pruning.
10. Containerized FastAPI, MCP, and PostgreSQL for a reproducible demo.

## Key design decisions

### RAG before agents

Plain retrieve-and-answer was made reliable before tool calling was added. This
kept retrieval failures separate from agent-loop failures.

### Governance is deterministic policy

The LLM does not decide whether a page is authoritative. Status, authority,
document type, freshness, and supersession produce bounded, visible scoring
adjustments. Every adjustment is returned to the UI.

### Conflicts remain visible

Misleading sources are not silently discarded. They are passed to the model in
a separate conflict lane so the answer can explicitly warn the user.

### PostgreSQL plus pgvector

Vectors, content, citations, fingerprints, and governance metadata remain in
one transactional system. This also demonstrates SQL-based vector retrieval
instead of hiding it behind a proprietary vector-database SDK.

### Source isolation

The frozen evaluation corpus and live Confluence pages coexist in one table,
but production-style API and MCP requests filter to `confluence_cloud`.
Evaluation explicitly filters to `frozen_corpus`.

## Result

For the Mosaic access query, the superseded live guide scored **0.7594** on raw
semantic similarity, while the canonical live procedure scored **0.5691**.
After governance-aware reranking, the canonical procedure reached **0.8191**
and the superseded guide fell to **0.5194** with a warning.

The final response cites the canonical Confluence page, identifies the exact
role and request path, and warns the user not to follow the outdated email
workflow. The same result is available through CLI, HTTP, MCP, and the React UI.

## Operational characteristics

- Content fingerprints prevent repeated Bedrock embedding calls.
- A no-change refresh skipped all 14 live chunks.
- Deleted or ungoverned pages are pruned only from `confluence_cloud` rows.
- Low-similarity questions stop before invoking the chat model.
- Agent requests have step, token, duplicate-call, and wall-clock limits.
- Health and readiness endpoints distinguish process health from dependencies.

## Production target

The portfolio environment runs locally in Docker to avoid idle infrastructure
cost. The container is designed for ECS Fargate with an IAM task role, RDS
PostgreSQL/pgvector, Secrets Manager, an Application Load Balancer, and
CloudWatch. The current portfolio proof focuses spending on Bedrock inference
rather than maintaining unused production infrastructure.
