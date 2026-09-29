export type ToolCallStatus = "success" | "error" | string;

export interface ToolCall {
  step: number;
  tool: string;
  arguments: Record<string, unknown>;
  status: ToolCallStatus;
  duplicate: boolean;
  duration_ms: number;
}

export interface UsageStats {
  input_tokens?: number;
  output_tokens?: number;
  total_tokens?: number;
  [key: string]: number | undefined;
}

export interface TimingsMs {
  total?: number;
  [key: string]: number | undefined;
}

/**
 * Backend source shape is not fully pinned down field-by-field, so we accept
 * the common variants (snake_case, alternate key names) and normalize in
 * `normalizeSource`.
 */
export interface RawSource {
  page_id?: string;
  pageId?: string;
  id?: string;
  title?: string;
  url?: string;
  status?: string; // current | draft | under_review | stale | superseded
  authority?: string | null; // canonical | standard | absent/null
  doc_type?: string;
  docType?: string;
  source_type?: string; // recommended | conflict
  sourceType?: string;
  semantic_score?: number;
  semanticScore?: number;
  final_score?: number;
  finalScore?: number;
  reasons?: string[];
  reranking_reasons?: string[];
  warnings?: string[];
  supersedes?: string;
  superseded_by?: string;
  section_path?: string;
  sectionPath?: string;
}

export interface Source {
  pageId: string;
  title: string;
  url?: string;
  status: string;
  authority: string;
  docType?: string;
  sourceType?: string;
  semanticScore?: number;
  finalScore?: number;
  reasons: string[];
  warnings: string[];
  supersededBy?: string;
  sectionPath?: string;
  isFlagged: boolean;
}

export type AgentStatus = "answered" | "safety_limit" | "insufficient_evidence" | string;

export interface AgentAskRequest {
  question: string;
  max_steps?: number;
  max_tokens?: number;
}

export interface AgentAskResponse {
  question: string;
  status: AgentStatus;
  answer: string;
  citations: string[];
  sources: RawSource[];
  tool_calls: ToolCall[];
  usage: UsageStats;
  timings_ms: TimingsMs;
  warnings?: string[];
}

export interface ConversationEntry {
  id: string;
  question: string;
  response?: AgentAskResponse;
  normalizedSources?: Source[];
  error?: string;
  loading: boolean;
}
