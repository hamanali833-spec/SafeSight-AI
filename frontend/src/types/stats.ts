// Analytics data from GET /api/stats
export interface Stats {
  total: number;
  open: number;
  openHigh: number;
  byKind: Record<string, number>;
  bySeverity: Record<string, number>;
  byCamera: Record<string, number>;
  byHour: Record<string, number>;
}
