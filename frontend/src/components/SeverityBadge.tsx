// Colored label for a severity level (same colors as the boxes drawn on the video).
import type { Severity } from "../types/alert";

const STYLES: Record<Severity, string> = {
  HIGH: "bg-red-100 text-red-700 ring-red-600/20 dark:bg-red-500/15 dark:text-red-400 dark:ring-red-500/30",
  PARTIAL: "bg-orange-100 text-orange-700 ring-orange-600/20 dark:bg-orange-500/15 dark:text-orange-400 dark:ring-orange-500/30",
  REVIEW: "bg-yellow-100 text-yellow-800 ring-yellow-600/20 dark:bg-yellow-500/15 dark:text-yellow-300 dark:ring-yellow-500/30",
};

export function SeverityBadge({ severity }: { severity: Severity }) {
  return (
    <span className={`rounded-md px-2 py-0.5 text-xs font-semibold ring-1 ring-inset ${STYLES[severity]}`}>
      {severity}
    </span>
  );
}
