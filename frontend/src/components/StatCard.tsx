// One number with a label.
export function StatCard({ label, value, tone = "default", suffix = "" }: {
  label: string;
  value: number;
  tone?: "default" | "danger";
  suffix?: string;
}) {
  const color = tone === "danger" ? "text-red-600 dark:text-red-400" : "text-slate-900 dark:text-white";
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-neutral-800 dark:bg-neutral-900">
      <p className="text-xs font-medium uppercase tracking-wide text-slate-500 dark:text-neutral-400">{label}</p>
      <p className={`mt-2 text-3xl font-bold ${color}`}>{value}{suffix}</p>
    </div>
  );
}
