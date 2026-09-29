import type { Source } from "../types";

const STATUS_LABELS: Record<string, string> = {
  current: "Current",
  draft: "Draft",
  under_review: "Under review",
  stale: "Stale",
  superseded: "Superseded",
  unknown: "Unknown",
};

const AUTHORITY_LABELS: Record<string, string> = {
  canonical: "Canonical",
  standard: "Standard",
  none: "Authority not specified",
  absent: "Authority not specified",
  unknown: "Authority not specified",
};

export function humanizeStatus(status: string): string {
  return STATUS_LABELS[status.toLowerCase()] ?? status;
}

export function humanizeAuthority(authority: string): string {
  return AUTHORITY_LABELS[authority.toLowerCase()] ?? authority;
}

const INLINE_TOKEN_REPLACEMENTS: [RegExp, string][] = [
  [/\bunder_review\b/gi, "under review"],
  [/\bauthority=absent\b/gi, "authority not specified"],
  [/\babsent\b/gi, "not specified"],
];

export function humanizeWarningText(text: string): string {
  return INLINE_TOKEN_REPLACEMENTS.reduce((acc, [pattern, replacement]) => acc.replace(pattern, replacement), text);
}

export function isSuperseded(source: Source): boolean {
  return (
    source.status.toLowerCase() === "superseded" ||
    Boolean(source.supersededBy) ||
    source.warnings.some((w) => w.toLowerCase().includes("superseded"))
  );
}
