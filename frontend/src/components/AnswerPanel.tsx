import { cleanAnswerText } from "../lib/cleanAnswer";
import "./AnswerPanel.css";

interface AnswerPanelProps {
  answer: string;
  citations: string[];
}

type Token = { type: "text"; value: string } | { type: "citation"; value: string } | { type: "code"; value: string };

const TOKEN_PATTERN = /\[([a-zA-Z]+-[\w-]+)\]|`([^`\n]+)`/g;

function tokenize(answer: string): Token[] {
  const tokens: Token[] = [];
  let lastIndex = 0;
  let match: RegExpExecArray | null;

  TOKEN_PATTERN.lastIndex = 0;
  while ((match = TOKEN_PATTERN.exec(answer)) !== null) {
    if (match.index > lastIndex) {
      tokens.push({ type: "text", value: answer.slice(lastIndex, match.index) });
    }
    if (match[1]) {
      tokens.push({ type: "citation", value: match[1] });
    } else if (match[2]) {
      tokens.push({ type: "code", value: match[2] });
    }
    lastIndex = TOKEN_PATTERN.lastIndex;
  }
  if (lastIndex < answer.length) {
    tokens.push({ type: "text", value: answer.slice(lastIndex) });
  }
  return tokens;
}

export function AnswerPanel({ answer, citations }: AnswerPanelProps) {
  const cleaned = cleanAnswerText(answer);
  const tokens = tokenize(cleaned);

  return (
    <div className="answer-panel">
      <p className="answer-panel__text">
        {tokens.map((token, i) => {
          if (token.type === "citation") {
            return (
              <span key={i} className="citation-chip">
                {token.value}
              </span>
            );
          }
          if (token.type === "code") {
            return (
              <code key={i} className="inline-code">
                {token.value}
              </code>
            );
          }
          return <span key={i}>{token.value}</span>;
        })}
      </p>
      {citations.length > 0 && (
        <div className="answer-panel__citation-list">
          <span className="answer-panel__citation-label">Cited pages:</span>
          {citations.map((c) => (
            <span key={c} className="citation-chip citation-chip--outline">
              {c}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
