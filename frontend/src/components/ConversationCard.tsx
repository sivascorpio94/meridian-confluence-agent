import { collectWarnings } from "../api/client";
import type { ConversationEntry } from "../types";
import { AgentTimeline } from "./AgentTimeline";
import { AnswerPanel } from "./AnswerPanel";
import { HowProduced } from "./HowProduced";
import { SourcesPanel } from "./SourcesPanel";
import { ErrorState, InsufficientEvidenceState, LoadingState, SafetyLimitBanner } from "./StatusStates";
import { UsageBar } from "./UsageBar";
import { WarningsPanel } from "./WarningsPanel";
import "./ConversationCard.css";

interface ConversationCardProps {
  entry: ConversationEntry;
}

export function ConversationCard({ entry }: ConversationCardProps) {
  const { response, normalizedSources, error, loading } = entry;

  return (
    <div className="conversation-card">
      <p className="conversation-card__question">{entry.question}</p>

      {loading && <LoadingState />}
      {error && <ErrorState message={error} />}

      {response && !loading && (
        <div className="conversation-card__body">
          {response.status === "safety_limit" && <SafetyLimitBanner />}

          {response.status === "insufficient_evidence" ? (
            <InsufficientEvidenceState question={entry.question} />
          ) : (
            <>
              <AnswerPanel answer={response.answer} citations={response.citations} />
              <WarningsPanel warnings={collectWarnings(normalizedSources ?? [])} />
              <AgentTimeline toolCalls={response.tool_calls} />
              <SourcesPanel sources={normalizedSources ?? []} />
              <div className="conversation-card__footer">
                <UsageBar usage={response.usage} timings={response.timings_ms} />
              </div>
              <HowProduced response={response} sources={normalizedSources ?? []} />
            </>
          )}
        </div>
      )}
    </div>
  );
}
