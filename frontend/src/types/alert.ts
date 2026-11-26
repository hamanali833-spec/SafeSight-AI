// Shapes of the data the dashboard works with (camelCase JSON from FastAPI).
export type Severity = "REVIEW" | "PARTIAL" | "HIGH";
export type AlertKind = "PPE" | "ZONE";

export interface Alert {
  id: number;
  cameraId: string;    // which camera raised it, e.g. "warehouse"
  trackId: number;     // the person's ID from ByteTrack
  kind: AlertKind;     // PPE violation or restricted zone entry
  severity: Severity;
  message: string;
  createdAt: string;   // ISO date-time
  resolved: boolean;
}
