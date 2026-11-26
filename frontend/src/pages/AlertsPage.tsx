// All alerts with a severity filter and a "Resolve" button.
import { useState } from "react";
import { fetchAlerts, resolveAlert } from "../api/alerts";
import type { Alert, Severity } from "../types/alert";
import { AlertTable } from "../components/AlertTable";
import { Card } from "../components/Card";
import { usePolling } from "../components/usePolling";
import { useCameras } from "../components/useCameras";
import { useAuth } from "../auth/AuthContext";

type Filter = Severity | "ALL";
const FILTERS: Filter[] = ["ALL", "HIGH", "PARTIAL", "REVIEW"];

export function AlertsPage({ onError }: { onError: (msg: string | null) => void }) {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [filter, setFilter] = useState<Filter>("ALL");
  const { names } = useCameras();
  const { can } = useAuth();

  usePolling(async () => {
    try {
      setAlerts(await fetchAlerts());
      onError(null);
    } catch {
      onError("We can't reach the server right now. Trying again...");
    }
  }, 3000);

  async function handleResolve(id: number) {
    try {
      const updated = await resolveAlert(id);
      setAlerts((prev) => prev.map((a) => (a.id === id ? updated : a)));
    } catch {
      onError("Could not resolve the alert. Please try again.");
    }
  }

  const visible = filter === "ALL" ? alerts : alerts.filter((a) => a.severity === filter);

  return (
    <Card
      title={`Alerts (${visible.length})`}
      action={
        <div className="flex gap-1">
          {FILTERS.map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`rounded-md px-3 py-1 text-xs font-medium ${
                filter === f
                  ? "bg-slate-900 text-white dark:bg-white dark:text-black"
                  : "text-slate-600 hover:bg-slate-100 dark:text-neutral-400 dark:hover:bg-neutral-800"
              }`}
            >
              {f}
            </button>
          ))}
        </div>
      }
    >
      <AlertTable alerts={visible} onResolve={handleResolve}
                  canResolve={can("admin", "supervisor")} cameraNames={names} />
    </Card>
  );
}
