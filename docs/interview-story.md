# Interview Explanation

## Thirty-second summary

“I built a trust-aware Confluence agent for a fictional financial company. The
problem was that keyword and vector search can both retrieve outdated pages.
I synchronized governed pages from Confluence, created heading-aware chunks,
embedded them with Titan, stored them in pgvector, and added deterministic
authority and lifecycle reranking before generating cited answers with Llama
3.3. I then exposed the capabilities through MCP, FastAPI, and a React UI.”

## Architecture explanation

“The ingestion path is Confluence REST API to normalized Markdown, governance
metadata, chunks, Titan embeddings, and pgvector. At query time, Titan embeds
the question, PostgreSQL retrieves semantic candidates, and a policy layer
reranks them based on status, authority, type, freshness, and supersession. The
prompt keeps recommended and conflicting evidence separate. Llama can warn
about conflicts, but it cannot override the deterministic trust policy.”

## Strong technical example

“The most useful test had a superseded guide scoring 0.7594 semantically versus
0.5691 for the canonical procedure. Pure vector search would choose the wrong
page. The metadata layer boosted the canonical procedure to 0.8191 and demoted
the superseded guide to 0.5194 while retaining it as a warning. That demonstrates
why retrieval relevance and source trust must be separate concerns.”

## Why MCP

“I first built and evaluated RAG without an agent. After retrieval was stable, I
wrapped search, grounded answering, conflict inspection, and page details as
MCP tools. MCP gives the model a standard tool interface and keeps domain logic
out of the agent loop. FastAPI reuses one MCP subprocess instead of starting one
for every request.”

## Production considerations

“The portfolio environment runs locally in Docker to control cost. The target
deployment is ECS Fargate, RDS PostgreSQL with pgvector, Secrets Manager,
CloudWatch, HTTPS, and a restricted Bedrock task role. Before making it public,
I would also add authentication, per-user rate limits, Bedrock budget alarms,
and audit logging.”

## Lessons learned

- Semantic similarity is not the same as authority.
- Metadata quality is part of RAG quality.
- Evaluation should precede agent autonomy.
- Incremental embeddings materially reduce cost and refresh time.
- Explicit evidence lanes make conflicts safer and easier to explain.
