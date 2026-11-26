// Load the camera list (and refresh it every few seconds), plus an id -> name lookup.
import { useState } from "react";
import { fetchCameras } from "../api/cameras";
import type { Camera } from "../types/camera";
import { usePolling } from "./usePolling";

export function useCameras(ms = 5000) {
  const [cameras, setCameras] = useState<Camera[]>([]);
  usePolling(async () => {
    try { setCameras(await fetchCameras()); } catch { /* the page shows its own error */ }
  }, ms);
  const names = Object.fromEntries(cameras.map((c) => [c.id, c.name]));
  return { cameras, setCameras, names };
}
