export type Role = "admin" | "supervisor" | "guard";

export interface User {
  id: number;
  email: string;
  name: string;
  role: Role;
}
