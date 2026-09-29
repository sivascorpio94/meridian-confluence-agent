import "./WarningsPanel.css";

interface WarningsPanelProps {
  warnings: string[];
}

export function WarningsPanel({ warnings }: WarningsPanelProps) {
  if (warnings.length === 0) return null;

  return (
    <div className="warnings-panel">
      <span className="warnings-panel__icon">!</span>
      <div>
        <p className="warnings-panel__title">Review before relying on this answer</p>
        <ul className="warnings-panel__list">
          {warnings.map((w, i) => (
            <li key={i}>{w}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}
