// Horizontal bar chart made with plain divs (no chart library needed).
export function BarList({ data, color = "bg-slate-800 dark:bg-white" }: {
  data: Record<string, number>;
  color?: string;   // Tailwind background class for the bars
}) {
  const entries = Object.entries(data).sort((a, b) => b[1] - a[1]);   // biggest first
  const max = Math.max(1, ...entries.map(([, n]) => n));

  if (entries.length === 0) {
    return <p className="p-4 text-sm text-slate-400 dark:text-neutral-500">No data yet</p>;
  }
  return (
    <ul className="space-y-3 p-4">
      {entries.map(([label, n]) => (
        <li key={label}>
          <div className="mb-1 flex justify-between text-xs text-slate-600 dark:text-neutral-400">
            <span>{label}</span>
            <span className="font-semibold text-slate-900 dark:text-white">{n}</span>
          </div>
          <div className="h-2 rounded-full bg-slate-100 dark:bg-neutral-800">
            {/* Width = share of the biggest value, e.g. 3 of 6 -> 50% */}
            <div className={`h-2 rounded-full ${color}`} style={{ width: `${(n / max) * 100}%` }} />
          </div>
        </li>
      ))}
    </ul>
  );
}
