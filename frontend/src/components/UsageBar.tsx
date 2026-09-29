import type { TimingsMs, UsageStats } from "../types";
import "./UsageBar.css";

interface UsageBarProps {
  usage: UsageStats;
  timings: TimingsMs;
}

function totalTokens(usage: UsageStats): number | undefined {
  if (usage.total_tokens !== undefined) return usage.total_tokens;
  if (usage.input_tokens !== undefined || usage.output_tokens !== undefined) {
    return (usage.input_tokens ?? 0) + (usage.output_tokens ?? 0);
  }
  return undefined;
}

function totalLatency(timings: TimingsMs): number | undefined {
  if (timings.total !== undefined) return timings.total;
  const values = Object.values(timings).filter((v): v is number => typeof v === "number");
  if (values.length === 0) return undefined;
  return values.reduce((a, b) => a + b, 0);
}

export function UsageBar({ usage, timings }: UsageBarProps) {
  const tokens = totalTokens(usage);
  const latency = totalLatency(timings);

  return (
    <div className="usage-bar">
      {tokens !== undefined && (
        <div className="usage-bar__stat">
          <span className="usage-bar__value">{tokens.toLocaleString()}</span>
          <span className="usage-bar__label">tokens</span>
        </div>
      )}
      {latency !== undefined && (
        <div className="usage-bar__stat">
          <span className="usage-bar__value">{(latency / 1000).toFixed(2)}s</span>
          <span className="usage-bar__label">latency</span>
        </div>
      )}
    </div>
  );
}
