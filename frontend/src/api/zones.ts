import type { CameraZones, Point } from "../types/zone";
import { request } from "./client";

export const fetchAllZones = () => request<CameraZones[]>("/api/zones");

// Returns null when the camera has no zone yet (404)
export async function fetchZone(cameraId: string): Promise<CameraZones | null> {
  try {
    return await request<CameraZones>(`/api/zones/${cameraId}`);
  } catch {
    return null;
  }
}

export const saveZone = (cameraId: string, points: Point[]) =>
  request<CameraZones>(`/api/zones/${cameraId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name: "Restricted zone", points }),
  });

export const deleteZone = (cameraId: string) =>
  request<void>(`/api/zones/${cameraId}`, { method: "DELETE" });
