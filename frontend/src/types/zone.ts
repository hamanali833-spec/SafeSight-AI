// A restricted zone: a polygon in ORIGINAL video pixels
export type Point = [number, number];

export interface Zone {
  name: string;
  points: Point[];
}

export interface CameraZones {
  cameraId: string;
  zones: Zone[];
}
