import "./StatusStates.css";

export function LoadingState() {
  return (
    <div className="status-state status-state--loading">
      <span className="spinner" />
      Meridian is retrieving evidence and reasoning about the answer…
    </div>
  );
}

export function ErrorState({ message }: { message: string }) {
  return <div className="status-state status-state--error">⚠ {message}</div>;
}

export function InsufficientEvidenceState({ question }: { question: string }) {
  return (
    <div className="status-state status-state--insufficient">
      <strong>Insufficient evidence</strong>
      <span>
        No retrieved content was similar enough to "{question}" to answer confidently. No
        sources are shown and no citations were generated, so no cost was spent on generation.
      </span>
    </div>
  );
}

export function SafetyLimitBanner() {
  return (
    <div className="status-state status-state--error" style={{ background: "#fff3d9", color: "#8a6100", border: "1px solid #f3d9a8" }}>
      ⚠ The agent reached its maximum step limit before fully resolving this question. The
      answer below may be incomplete.
    </div>
  );
}
