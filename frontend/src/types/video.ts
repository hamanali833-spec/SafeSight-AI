// A video processing job for one camera (from /api/videos)
export type JobStatus = "queued" | "processing" | "done" | "failed";

export interface VideoJob {
  id: string;
  cameraId: string;
  filename: string;
  status: JobStatus;
  progress: number;      // 0-100
  ppeAlerts: number;
  zoneAlerts: number;
  ppeRequired: boolean;
  hasZones: boolean;
  error: string | null;
}
