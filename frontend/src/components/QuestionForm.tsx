import { useState } from "react";
import "./QuestionForm.css";

const SUGGESTED_QUESTIONS = [
  "Does the Mosaic reporting team have read-only access to the trading ledger?",
  "What is the current procedure for onboarding a new vendor?",
  "Are the Mosaic integration instructions on Confluence still accurate?",
  "What should I do if a client requests an emergency wire during a system outage?",
  "Who owns the quarterly SOX audit checklist?",
];

interface QuestionFormProps {
  onAsk: (question: string) => void;
  disabled: boolean;
}

export function QuestionForm({ onAsk, disabled }: QuestionFormProps) {
  const [value, setValue] = useState("");

  const submit = (question: string) => {
    const trimmed = question.trim();
    if (!trimmed || disabled) return;
    onAsk(trimmed);
    setValue("");
  };

  return (
    <div className="question-form">
      <form
        onSubmit={(e) => {
          e.preventDefault();
          submit(value);
        }}
      >
        <input
          type="text"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder="Ask Meridian about policies, procedures, or systems…"
          disabled={disabled}
          aria-label="Question"
        />
        <button type="submit" disabled={disabled || !value.trim()}>
          Ask
        </button>
      </form>
      <div className="question-form__suggestions">
        <span className="question-form__suggestions-label">Try:</span>
        {SUGGESTED_QUESTIONS.map((q) => (
          <button
            key={q}
            type="button"
            className="suggestion-chip"
            disabled={disabled}
            onClick={() => submit(q)}
          >
            {q}
          </button>
        ))}
      </div>
    </div>
  );
}
