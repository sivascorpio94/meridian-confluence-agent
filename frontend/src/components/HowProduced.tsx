import { useState } from "react";
import type { AgentAskResponse, Source } from "../types";
import "./HowProduced.css";

interface HowProducedProps {
  response: AgentAskResponse;
  sources: Source[];
}

export function HowProduced({ response, sources }: HowProducedProps) {
  const [open, setOpen] = useState(false);

  return (
    <div className="how-produced">
      <button className="how-produced__toggle" onClick={() => setOpen((o) => !o)}>
        <span className={"how-produced__chevron" + (open ? " how-produced__chevron--open" : "")}>›</span>
        How this answer was produced
      </button>
      {open && (
        <div className="how-produced__body">
          <div className="how-produced__row">
            <span className="how-produced__label">Status</span>
            <span className="how-produced__value">{response.status}</span>
          </div>
          <div className="how-produced__row">
            <span className="how-produced__label">Tool calls</span>
            <span className="how-produced__value">{response.tool_calls.length}</span>
          </div>
          <div className="how-produced__row">
            <span className="how-produced__label">Sources considered</span>
            <span className="how-produced__value">{sources.length}</span>
          </div>

          {sources.length > 0 && (
            <table className="how-produced__table">
              <thead>
                <tr>
                  <th>Page</th>
                  <th>Semantic</th>
                  <th>Final</th>
                  <th>Reasons</th>
                </tr>
              </thead>
              <tbody>
                {sources.map((s) => (
                  <tr key={s.pageId}>
                    <td>{s.pageId}</td>
                    <td>{s.semanticScore !== undefined ? s.semanticScore.toFixed(2) : "—"}</td>
                    <td>{s.finalScore !== undefined ? s.finalScore.toFixed(2) : "—"}</td>
                    <td>{s.reasons.join("; ") || "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}

          <details className="how-produced__raw">
            <summary>Raw response JSON</summary>
            <pre>{JSON.stringify(response, null, 2)}</pre>
          </details>
        </div>
      )}
    </div>
  );
}
