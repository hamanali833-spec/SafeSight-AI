// Monitoring: key numbers, then a grid of cameras analyzed side by side,
// then the most recent alerts from all cameras.
import { useCallback, useState } from "react";
import { fetchAlerts } from "../api/alerts";
import { fetchStats } from "../api/stats";
import { uploadVideo } from "../api/videos";
import type { Alert } from "../types/alert";
import type { Stats } from "../types/stats";
import type { VideoJob } from "../types/video";
import { AlertTable } from "../components/AlertTable";
import { Card } from "../components/Card";
import { CameraTile } from "../components/CameraTile";
import { StatCard } from "../components/StatCard";
import { useCameras } from "../components/useCameras";
import { usePolling } from "../components/usePolling";
import { useAuth } from "../auth/AuthContext";

export function MonitoringPage({ onError }: { onError: (msg: string | null) => void }) {
  const { cameras, names } = useCameras();
  const canUpload = useAuth().can("admin", "supervisor");   // guards only watch
  const [stats, setStats] = useState<Stats | null>(null);
  const [recent, setRecent] = useState<Alert[]>([]);
  const [files, setFiles] = useState<Record<string, File | null>>({});   // camera id -> chosen video
  const [jobs, setJobs] = useState<Record<string, VideoJob>>({});         // camera id -> its job
  const [starting, setStarting] = useState(false);
  const [startError, setStartError] = useState<string | null>(null);

  // Numbers and recent alerts, refreshed every 3 seconds
  usePolling(async () => {
    try {
      const [s, a] = await Promise.all([fetchStats(), fetchAlerts()]);
      setStats(s);
      setRecent(a.slice(0, 6));
      onError(null);
    } catch {
      onError("We can't reach the server right now. Trying again...");
    }
  }, 3000);

  const updateJob = useCallback((j: VideoJob) => setJobs((prev) => ({ ...prev, [j.cameraId]: j })), []);
  const isRunning = (id: string) => ["queued", "processing"].includes(jobs[id]?.status ?? "");
  const ready = cameras.filter((c) => files[c.id] && !isRunning(c.id));

  // Upload every chosen video at once: each camera becomes its own job on the backend
  async function startAll() {
    setStarting(true);
    setStartError(null);
    const results = await Promise.allSettled(ready.map((c) => uploadVideo(files[c.id]!, c.id)));
    results.forEach((r, i) => {
      if (r.status === "fulfilled") {
        updateJob(r.value);
        setFiles((prev) => ({ ...prev, [ready[i].id]: null }));
      } else {
        setStartError(`${ready[i].name}: ${r.reason instanceof Error ? r.reason.message : "upload failed"}`);
      }
    });
    setStarting(false);
  }

  const live = cameras.filter((c) => isRunning(c.id)).length;

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatCard label="Cameras live" value={live} />
        <StatCard label="Open alerts" value={stats?.open ?? 0} />
        <StatCard label="Open HIGH" value={stats?.openHigh ?? 0} tone="danger" />
        <StatCard label="Zone alerts" value={stats?.byKind.ZONE ?? 0} />
      </div>

      <Card
        title={`Cameras (${cameras.length})`}
        action={
          <div className="flex items-center gap-3">
            {startError && <span className="text-xs text-red-600 dark:text-red-400">{startError}</span>}
            {canUpload ? <button
              onClick={startAll}
              disabled={!ready.length || starting}
              className="rounded-md bg-slate-900 px-3 py-1.5 text-sm font-medium text-white hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-40 dark:bg-white dark:text-black dark:hover:bg-neutral-200"
            >
              {starting ? "Uploading..." : `Start all${ready.length ? ` (${ready.length})` : ""}`}
            </button> : <span className="text-xs text-slate-500 dark:text-neutral-400">View only · ask a supervisor to start cameras</span>}
          </div>
        }
      >
        <div className="grid gap-4 p-4 md:grid-cols-2 xl:grid-cols-3">
          {cameras.map((c) => (
            <CameraTile
              key={c.id}
              camera={c}
              file={files[c.id] ?? null}
              onFile={(f) => setFiles((prev) => ({ ...prev, [c.id]: f }))}
              job={jobs[c.id] ?? null}
              onJob={updateJob}
              canUpload={canUpload}
            />
          ))}
        </div>
      </Card>

      <Card title="Recent alerts (all cameras)">
        <AlertTable alerts={recent} cameraNames={names} />
      </Card>
    </div>
  );
}
