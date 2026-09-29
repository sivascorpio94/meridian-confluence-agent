import type { Source } from "../types";
import { SourceCard } from "./SourceCard";
import "./SourcesPanel.css";

interface SourcesPanelProps {
  sources: Source[];
}

export function SourcesPanel({ sources }: SourcesPanelProps) {
  if (sources.length === 0) return null;

  const recommended = sources.filter((s) => !s.isFlagged);
  const flagged = sources.filter((s) => s.isFlagged);

  return (
    <div className="sources-panel">
      <div>
        <h3 className="section-heading">Recommended sources</h3>
        {recommended.length > 0 ? (
          <div className="sources-panel__grid">
            {recommended.map((s) => (
              <SourceCard key={s.pageId} source={s} />
            ))}
          </div>
        ) : (
          <p className="sources-panel__empty">No fully current, canonical sources were retrieved.</p>
        )}
      </div>

      {flagged.length > 0 && (
        <div className="sources-panel__warning-block">
          <h3 className="section-heading section-heading--warning">
            Stale, superseded, or draft documentation
          </h3>
          <p className="sources-panel__warning-copy">
            These pages were retrieved but are not considered authoritative. The agent avoids
            blending guidance from these with the recommended sources above.
          </p>
          <div className="sources-panel__grid">
            {flagged.map((s) => (
              <SourceCard key={s.pageId} source={s} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
