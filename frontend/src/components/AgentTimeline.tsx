import type { ToolCall } from "../types";
import "./AgentTimeline.css";

interface AgentTimelineProps {
  toolCalls: ToolCall[];
}

const TOOL_LABELS: Record<string, string> = {
  search_knowledge: "Searched knowledge base",
  answer_question: "Ran grounded RAG pipeline",
  get_page_details: "Retrieved page details",
  check_document_conflicts: "Checked for document conflicts",
};

function describeTool(tool: string): string {
  return TOOL_LABELS[tool] ?? `Called ${tool}`;
}

export function AgentTimeline({ toolCalls }: AgentTimelineProps) {
  if (toolCalls.length === 0) return null;

  return (
    <div className="agent-timeline">
      <h3 className="section-heading">Agent activity</h3>
      <ol className="agent-timeline__list">
        {toolCalls.map((call) => (
          <li key={call.step} className={"agent-timeline__item" + (call.status !== "success" ? " agent-timeline__item--error" : "")}>
            <div className="agent-timeline__marker">{call.step}</div>
            <div className="agent-timeline__body">
              <div className="agent-timeline__title">
                <span className="agent-timeline__tool">{describeTool(call.tool)}</span>
                {call.duplicate && <span className="badge badge--muted">duplicate call skipped</span>}
                {call.status !== "success" && <span className="badge badge--error">{call.status}</span>}
              </div>
              {Object.keys(call.arguments ?? {}).length > 0 && (
                <code className="agent-timeline__args">{JSON.stringify(call.arguments)}</code>
              )}
              <span className="agent-timeline__duration">{call.duration_ms} ms</span>
            </div>
          </li>
        ))}
      </ol>
    </div>
  );
}
