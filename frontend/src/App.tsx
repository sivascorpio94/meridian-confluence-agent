import { useEffect, useState } from "react";
import { ApiError, askAgent, checkHealth, normalizeSource, NetworkError } from "./api/client";
import { ConversationCard } from "./components/ConversationCard";
import { Header } from "./components/Header";
import { QuestionForm } from "./components/QuestionForm";
import type { ConversationEntry } from "./types";
import "./App.css";

function makeId() {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

function App() {
  const [entries, setEntries] = useState<ConversationEntry[]>([]);
  const [backendOnline, setBackendOnline] = useState<boolean | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    checkHealth().then(setBackendOnline);
  }, []);

  const handleAsk = async (question: string) => {
    const id = makeId();
    setEntries((prev) => [...prev, { id, question, loading: true }]);
    setBusy(true);

    try {
      const response = await askAgent({ question, max_steps: 4, max_tokens: 500 });
      const normalizedSources = response.sources.map(normalizeSource);
      setEntries((prev) =>
        prev.map((e) => (e.id === id ? { ...e, response, normalizedSources, loading: false } : e))
      );
      setBackendOnline(true);
    } catch (err) {
      let message = "Something went wrong while contacting the Meridian backend.";
      if (err instanceof ApiError) {
        message = err.message;
      } else if (err instanceof NetworkError) {
        message = err.message;
        setBackendOnline(false);
      }
      setEntries((prev) => (prev.map((e) => (e.id === id ? { ...e, error: message, loading: false } : e))));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="app">
      <Header backendOnline={backendOnline} />
      <main className="app__main">
        <div className="app__composer">
          <QuestionForm onAsk={handleAsk} disabled={busy} />
        </div>

        {entries.length === 0 ? (
          <div className="app__empty">
            <p>Ask a question above to see Meridian retrieve, rerank, and cite Confluence evidence.</p>
          </div>
        ) : (
          <div className="app__conversation">
            {entries
              .slice()
              .reverse()
              .map((entry) => (
                <ConversationCard key={entry.id} entry={entry} />
              ))}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
