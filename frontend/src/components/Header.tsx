import "./Header.css";

interface HeaderProps {
  backendOnline: boolean | null;
}

export function Header({ backendOnline }: HeaderProps) {
  return (
    <header className="app-header">
      <div className="app-header__brand">
        <div className="app-header__logo">MK</div>
        <div>
          <h1>Meridian Knowledge Assistant</h1>
          <p className="app-header__subtitle">
            Internal Confluence knowledge agent for <strong>Meridian Financial Group</strong> —
            a fictional company created for portfolio purposes only.
          </p>
        </div>
      </div>
      <div className="app-header__status">
        <span
          className={
            "status-dot " +
            (backendOnline === null ? "status-dot--unknown" : backendOnline ? "status-dot--ok" : "status-dot--down")
          }
        />
        {backendOnline === null ? "Checking backend…" : backendOnline ? "Backend online" : "Backend unavailable"}
      </div>
    </header>
  );
}
