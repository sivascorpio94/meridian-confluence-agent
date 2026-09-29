const SOURCES_HEADING = /^sources:?$/i;
const WARNING_PARAGRAPH = /^warning:/i;
const MECHANICAL_SOURCE_REF = /\bSOURCE\s+([a-zA-Z]+-[\w-]+)\b/gi;

/**
 * The backend's raw answer text often repeats information the UI already
 * renders in dedicated panels: a trailing "Sources:" bullet list (covered by
 * source cards + citation chips) and a "Warning: ..." paragraph (covered by
 * the structured warnings panel). Strip those paragraphs here so the answer
 * reads as prose, not as a re-print of the structured response.
 */
export function cleanAnswerText(answer: string): string {
  const paragraphs = answer.split(/\n\s*\n/);

  const kept = paragraphs.filter((paragraph) => {
    const firstLine = paragraph.trim().split("\n")[0]?.trim() ?? "";
    if (SOURCES_HEADING.test(firstLine)) return false;
    if (WARNING_PARAGRAPH.test(paragraph.trim())) return false;
    return true;
  });

  return kept
    .join("\n\n")
    .replace(MECHANICAL_SOURCE_REF, "[$1]")
    .trim();
}
