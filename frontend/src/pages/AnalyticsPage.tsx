// Analytics: how many alerts, of which type, from which camera, at what time.
import { useState } from "react";
import { fetchStats } from "../api/stats";
import type { Stats } from "../types/stats";
import { BarList } from "../components/BarList";
import { Card } from "../components/Card";
import { StatCard } from "../components/StatCard";
import { usePolling } from "../components/usePolling";
import { useCameras } from "../components/useCameras";

export function AnalyticsPage({ onError }: { onError: (msg: string | null) => void }) {
  const [stats, setStats] = useState<Stats | null>(null);
  const { names } = useCameras();

  usePolling(async () => {
    try {
      setStats(await fetchStats());
      onError(null);
    } catch {
      onError("We can't reach the server right now. Trying again...");
    }
  }, 5000);

  if (!stats) return <p className="p-6 text-center text-slate-500">Loading analytics...</p>;

  const byType = Object.fromEntries(
    Object.entries(stats.byKind).map(([k, n]) => [k === "ZONE" ? "Restricted zone" : "PPE violation", n]),
  );
  const byCamera = Object.fromEntries(Object.entries(stats.byCamera).map(([id, n]) => [names[id] ?? id, n]));
  const resolvedRate = stats.total ? Math.round(((stats.total - stats.open) / stats.total) * 100) : 0;

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatCard label="Total alerts" value={stats.total} />
        <StatCard label="Open alerts" value={stats.open} />
        <StatCard label="Open HIGH" value={stats.openHigh} tone="danger" />
        <StatCard label="Resolved" value={resolvedRate} suffix="%" />
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        <Card title="Alerts by type"><BarList data={byType} /></Card>
        <Card title="Alerts by severity"><BarList data={stats.bySeverity} color="bg-red-500" /></Card>
        <Card title="Alerts by camera"><BarList data={byCamera} /></Card>
        <Card title="Alerts by hour of day"><BarList data={stats.byHour} color="bg-amber-500" /></Card>
      </div>
    </div>
  );
}
