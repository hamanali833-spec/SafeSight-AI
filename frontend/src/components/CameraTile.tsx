// One camera on the Monitoring grid: its settings, a video to analyze,
// the live processed frame, progress and this camera's alert counts.
import { useEffect, useState } from "react";
import { fetchJob, previewUrl } from "../api/videos";
import type { Camera } from "../types/camera";
import type { VideoJob } from "../types/video";

export function CameraTile({ camera, file, onFile, job, onJob, canUpload = true }: {
  camera: Camera;
  file: File | null;                       // the video chosen for this camera
  onFile: (f: File | null) => void;
  job: VideoJob | null;                    // this camera's current job, if any
  onJob: (j: VideoJob) => void;
  canUpload?: boolean;                     // false for guards: no video picker
}) {
  const [frameUrl, setFrameUrl] = useState<string | null>(null);
  const running = job?.status === "queued" || job?.status === "processing";

  // While this camera's job runs: fresh status and preview frame every 1.5 s
  useEffect(() => {
    if (!job || !running) return;
    const timer = setInterval(async () => {
      try {
        const latest = await fetchJob(job.id);
        onJob(latest);
        if (latest.progress > 0) setFrameUrl(previewUrl(job.id));
      } catch { /* keep the last frame; the header shows offline */ }
    }, 1500);
    return () => clearInterval(timer);
  }, [job, running, onJob]);

  // A new job (new upload) starts with an empty preview
  useEffect(() => { if (job?.status === "queued") setFrameUrl(null); }, [job?.id, job?.status]);

  const badge = "rounded px-1.5 py-0.5 text-[11px] font-semibold uppercase tracking-wide";

  return (
    <section className="flex flex-col overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm dark:border-neutral-800 dark:bg-neutral-900">
      {/* Header: camera name, its rules, LIVE */}
      <div className="flex items-center justify-between gap-2 border-b border-slate-100 px-3 py-2.5 dark:border-neutral-800">
        <div className="min-w-0">
          <p className="truncate text-sm font-semibold text-slate-800 dark:text-neutral-100">{camera.name}</p>
          <div className="mt-1 flex gap-1.5">
            <span className={`${badge} ${camera.ppeRequired ? "bg-orange-100 text-orange-700 dark:bg-orange-500/15 dark:text-orange-400" : "bg-slate-100 text-slate-500 dark:bg-neutral-800 dark:text-neutral-400"}`}>
              PPE {camera.ppeRequired ? "on" : "off"}
            </span>
            <span className={`${badge} ${camera.hasZone ? "bg-red-100 text-red-700 dark:bg-red-500/15 dark:text-red-400" : "bg-slate-100 text-slate-500 dark:bg-neutral-800 dark:text-neutral-400"}`}>
              Zone {camera.hasZone ? "set" : "none"}
            </span>
          </div>
        </div>
        {running && (
          <span className="flex shrink-0 items-center gap-1.5 text-xs font-semibold text-red-500">
            <span className="h-2 w-2 animate-pulse rounded-full bg-red-500" />LIVE
          </span>
        )}
      </div>

      {/* Picture: live frame, or a place to choose a video */}
      <div className="relative flex aspect-video items-center justify-center overflow-hidden bg-black">
        {frameUrl ? (
          <img src={frameUrl} alt={`${camera.name} processed frame`} className="absolute inset-0 h-full w-full object-contain" />
        ) : !canUpload ? (
          <span className="text-xs text-neutral-500">Camera idle</span>
        ) : (
          <label className="flex h-full w-full cursor-pointer flex-col items-center justify-center gap-1 px-4 text-center text-xs text-neutral-400 hover:text-neutral-200">
            <span className="text-sm font-medium break-all">{file ? file.name : "+ Choose video"}</span>
            <span>{file ? "ready · press Start all" : "one CCTV clip for this camera"}</span>
            <input type="file" accept="video/*" className="hidden" disabled={running}
                   onChange={(e) => onFile(e.target.files?.[0] ?? null)} />
          </label>
        )}
      </div>

      {/* Footer: progress and this camera's alerts */}
      <div className="space-y-2 px-3 py-2.5">
        <div className="flex items-center justify-between text-xs">
          <span className="capitalize text-slate-500 dark:text-neutral-400">
            {job ? job.status : file ? "waiting to start" : "idle"}
          </span>
          <span className="font-semibold text-slate-800 dark:text-neutral-100">{job ? `${job.progress}%` : ""}</span>
        </div>
        <div className="h-1.5 rounded-full bg-slate-100 dark:bg-neutral-800">
          <div className={`h-1.5 rounded-full transition-all ${job?.status === "failed" ? "bg-red-500" : "bg-green-500"}`}
               style={{ width: `${job?.progress ?? 0}%` }} />
        </div>
        <div className="flex gap-4 text-xs text-slate-600 dark:text-neutral-400">
          <span><b className="text-orange-600 dark:text-orange-400">{job?.ppeAlerts ?? 0}</b> PPE alerts</span>
          <span><b className="text-red-600 dark:text-red-400">{job?.zoneAlerts ?? 0}</b> zone alerts</span>
          {frameUrl && !running && canUpload && (
            <label className="ml-auto cursor-pointer text-slate-500 underline hover:text-slate-800 dark:hover:text-white">
              new video
              <input type="file" accept="video/*" className="hidden"
                     onChange={(e) => { setFrameUrl(null); onFile(e.target.files?.[0] ?? null); }} />
            </label>
          )}
        </div>
        {job?.status === "failed" && <p className="text-xs text-red-600">Error: {job.error}</p>}
      </div>
    </section>
  );
}
