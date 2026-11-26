import type { Camera } from "../types/camera";
import { request } from "./client";

export const fetchCameras = () => request<Camera[]>("/api/cameras");

export const saveCamera = (id: string, name: string, ppeRequired: boolean) =>
  request<Camera>(`/api/cameras/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, ppeRequired }),
  });
