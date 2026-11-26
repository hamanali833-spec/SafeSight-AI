import type { Session } from "../auth/session";
import { request } from "./client";

export const loginRequest = (email: string, password: string) =>
  request<Session>("/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
