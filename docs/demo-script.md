# Two-Minute Demo Script

## Before recording

```bash
aws login
docker compose up -d
curl http://127.0.0.1:8000/ready
```

Open the React UI, the three personal Confluence pages, and a terminal.

## Script

### 0:00–0:15 — Problem

“Confluence search usually gives employees several plausible pages. The hard
part is deciding which page is current and authoritative. This agent combines
semantic retrieval with documentation governance.”

### 0:15–0:40 — Ask the question

Enter:

> I am a new engineer. How do I obtain read-only Mosaic access, and which
> outdated instructions should I avoid?

Point out the direct ServiceNow answer, `MOSAIC_UI_VIEWER`, and the live
`conf-*` citation.

### 0:40–1:05 — Explain the differentiator

Show the source cards and say:

“The superseded guide is actually the strongest raw semantic match. A normal
vector search would likely rank it first. My trust layer applies explicit
status, authority, document-type, freshness, and lifecycle adjustments, so the
canonical procedure is recommended and the other pages remain visible as
warnings.”

### 1:05–1:25 — Show agent activity

Highlight the MCP tool trace:

- searched the knowledge base;
- checked documentation conflicts;
- returned grounded citations.

Explain that the model chooses tools, while the MCP server owns the knowledge
operations and the policy remains deterministic.

### 1:25–1:45 — Show live synchronization

Open the three Confluence pages and their labels. In the terminal run:

```bash
python -m src.refresh_knowledge --region us-east-2
```

Point out that unchanged chunks are skipped, preventing unnecessary embedding
cost.

### 1:45–2:00 — Architecture and close

Show the architecture diagram:

“The local portfolio environment runs React, FastAPI, MCP, and pgvector in
Docker, with Titan and Llama 3.3 through Bedrock. The same container is designed
for ECS and RDS deployment using IAM task roles and managed secrets.”
