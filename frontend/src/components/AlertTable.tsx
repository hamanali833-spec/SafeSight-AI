// Table of alerts, with a "Resolve" button for open ones.
import type { Alert } from "../types/alert";
import { SeverityBadge } from "./SeverityBadge";

export function AlertTable({ alerts, onResolve, canResolve = true, cameraNames = {} }: {
  alerts: Alert[];
  onResolve?: (id: number) => void;   // leave out for a read-only table
  canResolve?: boolean;               // false: show status only (guards can't resolve)
  cameraNames?: Record<string, string>;   // camera id -> display name
}) {
  if (alerts.length === 0) {
    return <p className="p-6 text-center text-sm text-slate-500 dark:text-neutral-500">No alerts yet.</p>;
  }
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-sm">
        <thead className="text-xs uppercase tracking-wide text-slate-500 dark:text-neutral-500">
          <tr>
            <th className="px-4 py-3 font-medium">Time</th>
            <th className="px-4 py-3 font-medium">Camera</th>
            <th className="px-4 py-3 font-medium">Person</th>
            <th className="px-4 py-3 font-medium">Type</th>
            <th className="px-4 py-3 font-medium">Severity</th>
            <th className="px-4 py-3 font-medium">Issue</th>
            {onResolve && <th className="px-4 py-3 font-medium">Status</th>}
          </tr>
        </thead>
        <tbody className="text-slate-700 dark:text-neutral-300">
          {alerts.map((a) => (
            <tr key={a.id} className="border-t border-slate-100 dark:border-neutral-800">
              <td className="whitespace-nowrap px-4 py-3">{new Date(a.createdAt).toLocaleTimeString()}</td>
              <td className="px-4 py-3">{cameraNames[a.cameraId] ?? a.cameraId}</td>
              <td className="px-4 py-3">Person #{a.trackId}</td>
              <td className="px-4 py-3">{a.kind === "ZONE" ? "Restricted zone" : "PPE"}</td>
              <td className="px-4 py-3"><SeverityBadge severity={a.severity} /></td>
              <td className="px-4 py-3">{a.message}</td>
              {onResolve && (
                <td className="px-4 py-3">
                  {a.resolved ? (
                    <span className="text-green-600 dark:text-green-400">Resolved</span>
                  ) : !canResolve ? (
                    <span className="text-orange-600 dark:text-orange-400">Open</span>
                  ) : (
                    <button
                      onClick={() => onResolve(a.id)}
                      className="rounded-md bg-slate-900 px-3 py-1 text-xs font-medium text-white hover:bg-slate-700 dark:bg-white dark:text-black dark:hover:bg-neutral-200"
                    >
                      Resolve
                    </button>
                  )}
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
