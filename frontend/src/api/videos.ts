import type { VideoJob } from "../types/video";
import { getSession } from "../auth/session";
import { request } from "./client";

// Upload a video for one camera; the backend answers 202 with a job to follow
export function uploadVideo(file: File, cameraId: string) {
  const form = new FormData();          // multipart/form-data, like an HTML file form
  form.append("file", file);
  form.append("camera_id", cameraId);
  return request<VideoJob>("/api/videos", { method: "POST", body: form });
}

export const fetchJob = (id: string) => request<VideoJob>(`/api/videos/${id}`);

// A new URL every time, so the browser never shows an old cached image.
// <img> can't send an Authorization header, so the token goes in the URL here.
export const previewUrl = (id: string) =>
  `/api/videos/${id}/frame?t=${Date.now()}&token=${encodeURIComponent(getSession()?.accessToken ?? "")}`;
