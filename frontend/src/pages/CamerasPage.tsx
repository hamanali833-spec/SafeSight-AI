// Cameras: each camera's settings (name, PPE required) and its restricted zone,
// drawn on the camera's first frame right in the browser.
import { useEffect, useState } from "react";
import { saveCamera } from "../api/cameras";
import { deleteZone, fetchZone, saveZone } from "../api/zones";
import type { Point } from "../types/zone";
import { Card } from "../components/Card";
import { ZoneIcon } from "../components/Icons";
import { useCameras } from "../components/useCameras";

interface Frame { url: string; width: number; height: number }

// Read the first frame of a video file in the browser (no upload needed)
function grabFirstFrame(file: File): Promise<Frame> {
  return new Promise((resolve, reject) => {
    const video = document.createElement("video");
    video.muted = true;
    video.preload = "auto";
    video.src = URL.createObjectURL(file);
    video.onloadeddata = () => { video.currentTime = 0.1; };
    video.onseeked = () => {
      const canvas = document.createElement("canvas");
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      canvas.getContext("2d")!.drawImage(video, 0, 0);
      resolve({ url: canvas.toDataURL("image/jpeg", 0.85), width: video.videoWidth, height: video.videoHeight });
      URL.revokeObjectURL(video.src);
    };
    video.onerror = () => reject(new Error("The browser can't read this video. Try the original .mp4 file."));
  });
}

const btn = "rounded-md px-3 py-1.5 text-sm font-medium disabled:cursor-not-allowed disabled:opacity-40";
const primary = `${btn} bg-slate-900 text-white hover:bg-slate-700 dark:bg-white dark:text-black dark:hover:bg-neutral-200`;
const secondary = `${btn} border border-slate-300 text-slate-700 hover:bg-slate-100 dark:border-neutral-700 dark:text-neutral-300 dark:hover:bg-neutral-800`;

export function CamerasPage() {
  const { cameras, setCameras } = useCameras();
  const [selected, setSelected] = useState<string | null>(null);
  const [frame, setFrame] = useState<Frame | null>(null);
  const [points, setPoints] = useState<Point[]>([]);
  const [message, setMessage] = useState<{ text: string; ok: boolean } | null>(null);

  const camera = cameras.find((c) => c.id === selected) ?? null;
  useEffect(() => { if (!selected && cameras.length) setSelected(cameras[0].id); }, [cameras, selected]);

  // Switching camera: clear the picture and load that camera's saved zone (if any)
  useEffect(() => {
    if (!selected) return;
    setFrame(null);
    setMessage(null);
    fetchZone(selected).then((z) => setPoints(z ? z.zones[0].points : []));
  }, [selected]);

  async function updateSettings(id: string, name: string, ppeRequired: boolean) {
    const saved = await saveCamera(id, name, ppeRequired);
    setCameras((prev) => prev.map((c) => (c.id === id ? saved : c)));
  }

  async function chooseFile(file: File | undefined) {
    if (!file) return;
    try {
      setFrame(await grabFirstFrame(file));
    } catch (e) {
      setMessage({ text: e instanceof Error ? e.message : "Could not read video", ok: false });
    }
  }

  // Convert a click on the (scaled) image into ORIGINAL video pixels
  function addPoint(e: React.MouseEvent<SVGSVGElement>) {
    if (!frame) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const x = Math.round(((e.clientX - rect.left) / rect.width) * frame.width);
    const y = Math.round(((e.clientY - rect.top) / rect.height) * frame.height);
    setPoints((prev) => [...prev, [x, y]]);
  }

  async function handleSave() {
    if (!camera) return;
    try {
      await saveZone(camera.id, points);
      setCameras((prev) => prev.map((c) => (c.id === camera.id ? { ...c, hasZone: true } : c)));
      setMessage({ text: `Zone saved for ${camera.name}. Analyze its video on the Monitoring page.`, ok: true });
    } catch (e) {
      setMessage({ text: e instanceof Error ? e.message : "Save failed", ok: false });
    }
  }

  async function handleRemove() {
    if (!camera) return;
    await deleteZone(camera.id).catch(() => undefined);
    setPoints([]);
    setCameras((prev) => prev.map((c) => (c.id === camera.id ? { ...c, hasZone: false } : c)));
    setMessage({ text: `Zone removed for ${camera.name}.`, ok: true });
  }

  const r = frame ? frame.width / 160 : 5;
  const stroke = frame ? frame.width / 400 : 3;

  return (
    <div className="grid gap-4 lg:grid-cols-3">
      {/* Camera list with settings */}
      <Card title="Cameras">
        <ul className="divide-y divide-slate-100 dark:divide-neutral-800">
          {cameras.map((c) => (
            <li key={c.id}
                className={`cursor-pointer space-y-2 px-4 py-3 ${c.id === selected ? "bg-slate-50 dark:bg-neutral-800/60" : ""}`}
                onClick={() => setSelected(c.id)}>
              <div className="flex items-center gap-2">
                <input
                  defaultValue={c.name}
                  onClick={(e) => e.stopPropagation()}
                  onBlur={(e) => e.target.value.trim() && e.target.value !== c.name && updateSettings(c.id, e.target.value.trim(), c.ppeRequired)}
                  className="w-full rounded-md border border-transparent bg-transparent px-1 py-0.5 text-sm font-semibold text-slate-800 hover:border-slate-200 focus:border-slate-400 focus:outline-none dark:text-neutral-100 dark:hover:border-neutral-700"
                  aria-label="Camera name"
                />
                <span className="shrink-0 text-xs text-slate-400 dark:text-neutral-500">{c.id}</span>
              </div>
              <div className="flex items-center justify-between text-xs text-slate-600 dark:text-neutral-400">
                <label className="flex cursor-pointer items-center gap-2" onClick={(e) => e.stopPropagation()}>
                  <input type="checkbox" checked={c.ppeRequired}
                         onChange={(e) => updateSettings(c.id, c.name, e.target.checked)}
                         className="h-4 w-4 accent-slate-900 dark:accent-white" />
                  Helmet + vest required
                </label>
                <span className={c.hasZone ? "text-red-600 dark:text-red-400" : ""}>{c.hasZone ? "Zone set" : "No zone"}</span>
              </div>
            </li>
          ))}
        </ul>
      </Card>

      {/* Zone drawing for the selected camera */}
      <Card
        title={camera ? `Restricted zone: ${camera.name}` : "Restricted zone"}
        className="overflow-hidden lg:col-span-2"
        action={
          <label className={`${secondary} cursor-pointer`}>
            Choose video
            <input type="file" accept="video/*" className="hidden" onChange={(e) => chooseFile(e.target.files?.[0])} />
          </label>
        }
      >
        {frame ? (
          <>
            <div className="relative bg-black">
              <img src={frame.url} alt="First frame of the camera" className="block w-full" />
              {/* The SVG uses the video's own pixel size, so the polygon lines up exactly */}
              <svg viewBox={`0 0 ${frame.width} ${frame.height}`} preserveAspectRatio="none"
                   className="absolute inset-0 h-full w-full cursor-crosshair" onClick={addPoint}>
                {points.length >= 3 && (
                  <polygon points={points.map((p) => p.join(",")).join(" ")}
                           fill="rgba(239,68,68,0.3)" stroke="#ef4444" strokeWidth={stroke} />
                )}
                {points.length === 2 && (
                  <line x1={points[0][0]} y1={points[0][1]} x2={points[1][0]} y2={points[1][1]}
                        stroke="#ef4444" strokeWidth={stroke} />
                )}
                {points.map(([x, y], i) => (
                  <circle key={i} cx={x} cy={y} r={r} fill="#facc15" stroke="#000" strokeWidth={stroke / 2} />
                ))}
              </svg>
            </div>
            <div className="flex flex-wrap items-center gap-2 p-4">
              <span className="mr-auto text-sm text-slate-500 dark:text-neutral-400">
                {points.length < 3 ? `Click at least ${3 - points.length} more corner(s) on the floor` : `${points.length} corners`}
              </span>
              <button className={secondary} disabled={!points.length} onClick={() => setPoints((p) => p.slice(0, -1))}>Undo</button>
              <button className={secondary} disabled={!points.length} onClick={() => setPoints([])}>Clear</button>
              {camera?.hasZone && <button className={secondary} onClick={handleRemove}>Remove zone</button>}
              <button className={primary} disabled={points.length < 3} onClick={handleSave}>Save zone</button>
            </div>
          </>
        ) : (
          <div className="flex min-h-72 flex-col items-center justify-center gap-2 p-6 text-center text-sm text-slate-500 dark:text-neutral-500">
            <ZoneIcon className="h-8 w-8" />
            {camera
              ? `Choose a video from the ${camera.name} camera. Its first frame appears here; click the corners of the area where people are not allowed.`
              : "Select a camera on the left."}
            {camera?.hasZone && <span className="text-red-600 dark:text-red-400">This camera already has a zone; choose its video to see or change it.</span>}
          </div>
        )}
        {message && (
          <p className={`border-t px-4 py-3 text-sm dark:border-neutral-800 ${message.ok ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"}`}>
            {message.text}
          </p>
        )}
      </Card>
    </div>
  );
}
