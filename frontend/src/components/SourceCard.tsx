import { useState } from "react";
import { humanizeAuthority, humanizeStatus, isSuperseded } from "../lib/format";
import type { Source } from "../types";
import "./SourceCard.css";

interface SourceCardProps {
  source: Source;
}

function scorePercent(score: number | undefined): string {
  if (score === undefined) return "—";
  return `${Math.round(score * 100)}%`;
}

export function SourceCard({ source }: SourceCardProps) {
  const [detailsOpen, setDetailsOpen] = useState(false);
  const superseded = isSuperseded(source);

  return (
    <div className={"source-card" + (source.isFlagged ? " source-card--flagged" : "")}>
      <div className="source-card__header">
        <span className="source-card__page-id">{source.pageId}</span>
        <div className="source-card__pills">
          <span className={`pill pill--status pill--status-${source.status.toLowerCase()}`}>
            {humanizeStatus(source.status)}
          </span>
          <span className={`pill pill--authority pill--authority-${source.authority.toLowerCase()}`}>
            {humanizeAuthority(source.authority)}
          </span>
        </div>
      </div>

      {superseded && <span className="pill pill--superseded">Superseded</span>}

      <h4 className="source-card__title">
        {source.url ? (
          <a href={source.url} target="_blank" rel="noopener noreferrer">
            {source.title}
          </a>
        ) : (
          source.title
        )}
      </h4>
      {source.sectionPath && <p className="source-card__section">{source.sectionPath}</p>}

      {source.supersededBy && (
        <p className="source-card__superseded-note">Superseded by {source.supersededBy}</p>
      )}

      <button
        type="button"
        className="source-card__details-toggle"
        onClick={() => setDetailsOpen((o) => !o)}
      >
        {detailsOpen ? "Hide" : "Show"} scoring details
      </button>

      {detailsOpen && (
        <>
          <div className="source-card__scores">
            <div className="source-card__score">
              <span className="source-card__score-label">Semantic</span>
              <span className="source-card__score-value">{scorePercent(source.semanticScore)}</span>
            </div>
            <div className="source-card__score">
              <span className="source-card__score-label">Final</span>
              <span className="source-card__score-value">{scorePercent(source.finalScore)}</span>
            </div>
          </div>

          {source.reasons.length > 0 && (
            <ul className="source-card__reasons">
              {source.reasons.map((r, i) => (
                <li key={i}>{r}</li>
              ))}
            </ul>
          )}
        </>
      )}
    </div>
  );
}
