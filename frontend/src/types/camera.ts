// A CCTV camera and its settings (from GET /api/cameras)
export interface Camera {
  id: string;            // e.g. "warehouse" (also the zone file's name)
  name: string;          // shown on the dashboard, e.g. "Warehouse"
  ppeRequired: boolean;  // check helmets and vests on this camera?
  hasZone: boolean;      // a restricted zone is drawn for this camera
}
