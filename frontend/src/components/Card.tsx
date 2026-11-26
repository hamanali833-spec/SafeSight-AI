// A white (light theme) / near-black (dark theme) panel used everywhere.
export function Card({ title, action, children, className = "" }: {
  title?: string;
  action?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <section className={`rounded-xl border border-slate-200 bg-white shadow-sm dark:border-neutral-800 dark:bg-neutral-900 ${className}`}>
      {title && (
        <div className="flex items-center justify-between border-b border-slate-100 px-4 py-3 dark:border-neutral-800">
          <h2 className="text-sm font-semibold text-slate-800 dark:text-neutral-100">{title}</h2>
          {action}
        </div>
      )}
      {children}
    </section>
  );
}
