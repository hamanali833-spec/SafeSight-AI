import type { Alert } from "../types/alert";
import { request } from "./client";

export const fetchAlerts = () => request<Alert[]>("/api/alerts");

export const resolveAlert = (id: number) =>
  request<Alert>(`/api/alerts/${id}/resolve`, { method: "PATCH" });
