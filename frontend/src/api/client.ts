import { humanizeWarningText } from "../lib/format";
import type { AgentAskRequest, AgentAskResponse, RawSource, Source } from "../types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

export class ApiError extends Error {
  status?: number;

  constructor(message: string, status?: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

export class NetworkError extends Error {
  constructor(message = "Could not reach the Meridian backend.") {
    super(message);
    this.name = "NetworkError";
  }
}

const STALE_STATUSES = new Set(["stale", "superseded", "draft", "under_review"]);

export function normalizeSource(raw: RawSource): Source {
  const pageId = raw.page_id ?? raw.pageId ?? raw.id ?? "unknown";
  const status = raw.status ?? "unknown";
  const authority = raw.authority ?? "absent";
  const sourceType = raw.source_type ?? raw.sourceType;
  const warnings = raw.warnings ?? [];
  return {
    pageId,
    title: raw.title ?? pageId,
    url: raw.url,
    status,
    authority,
    docType: raw.doc_type ?? raw.docType,
    sourceType,
    semanticScore: raw.semantic_score ?? raw.semanticScore,
    finalScore: raw.final_score ?? raw.finalScore,
    reasons: raw.reasons ?? raw.reranking_reasons ?? [],
    warnings,
    supersededBy: raw.superseded_by,
    sectionPath: raw.section_path ?? raw.sectionPath,
    isFlagged:
      sourceType !== undefined
        ? sourceType.toLowerCase() !== "recommended"
        : STALE_STATUSES.has(status.toLowerCase()) || warnings.length > 0,
  };
}

export function collectWarnings(sources: Source[]): string[] {
  const seen = new Set<string>();
  const out: string[] = [];
  for (const s of sources) {
    for (const w of s.warnings) {
      const label = `${s.pageId}: ${humanizeWarningText(w)}`;
      if (!seen.has(label)) {
        seen.add(label);
        out.push(label);
      }
    }
  }
  return out;
}

export async function askAgent(request: AgentAskRequest, signal?: AbortSignal): Promise<AgentAskResponse> {
  let res: Response;
  try {
    res = await fetch(`${API_BASE_URL}/agent/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request),
      signal,
    });
  } catch {
    throw new NetworkError();
  }

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail ?? body.message ?? detail;
    } catch {
      // response body wasn't JSON; fall back to statusText
    }
    throw new ApiError(detail, res.status);
  }

  return (await res.json()) as AgentAskResponse;
}

export async function checkHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE_URL}/health`, { method: "GET" });
    return res.ok;
  } catch {
    return false;
  }
}
