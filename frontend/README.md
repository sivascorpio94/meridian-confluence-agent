# Meridian Knowledge Assistant — Portfolio UI

A React + TypeScript frontend for the Meridian Confluence knowledge agent. It talks to a
single backend endpoint, `POST /agent/ask`, and renders the agent's grounded answer,
citations, reranked evidence, tool-call timeline, and confidence/warning states.

**Meridian Financial Group is a fictional company invented for this portfolio project.**
No real data, credentials, or systems are involved.

## What this app does not do

- No AWS credentials, Bedrock calls, database access, or MCP subprocess logic live here.
  All agent execution — embeddings, retrieval, reranking, generation, tool calls — happens
  in the backend. The browser only calls the backend's HTTP API.

## Setup

```bash
npm install
cp .env.example .env
npm run dev
```

The app runs on `http://localhost:5173` by default and expects the backend at the URL in
`.env` (`VITE_API_BASE_URL`, default `http://127.0.0.1:8000`). The backend already allows
CORS from local origins on ports `5173` and `3000`.

## Environment variables

| Variable              | Default                   | Description                        |
| ---------------------- | -------------------------- | ----------------------------------- |
| `VITE_API_BASE_URL`    | `http://127.0.0.1:8000`   | Base URL of the FastAPI backend.    |

## API contract

`POST {VITE_API_BASE_URL}/agent/ask`

Request:

```json
{ "question": "string", "max_steps": 4, "max_tokens": 500 }
```

Response (fields the UI consumes):

- `status`: `"answered"` | `"safety_limit"` | `"insufficient_evidence"`
- `answer`: string containing inline `[page-XX]` citation markers
- `citations`: string[]
- `sources[]`: `page_id`, `title`, `url`, `status`, `authority`, `source_type`
  (`"recommended"` | `"conflict"`), `semantic_score`, `final_score`, `reasons[]`, `warnings[]`
- `tool_calls[]`: `step`, `tool`, `arguments`, `status`, `duplicate`, `duration_ms`
- `usage`: token counts
- `timings_ms`: stage/total timings

The client (`src/api/client.ts`) normalizes source field-name variants (snake_case vs.
camelCase, `authority: null`) defensively, since some fields evolved during backend
development.

## Structure

```
src/
  api/client.ts         fetch wrapper, error types, source normalization
  types.ts              shared request/response types
  components/           Header, QuestionForm, AnswerPanel, AgentTimeline,
                         SourceCard, SourcesPanel, WarningsPanel, HowProduced,
                         UsageBar, StatusStates, ConversationCard
  App.tsx                conversation state + orchestration
```

## Build

```bash
npm run build
```
