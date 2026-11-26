// One small helper for every backend call.
// - adds the login token (Authorization: Bearer ...)
// - if the token has expired (401), gets a new one with the refresh token and tries once more
// - throws a readable error on failure
import { getSession, setSession, type Session } from "../auth/session";

let refreshing: Promise<boolean> | null = null;   // share ONE refresh between parallel requests

async function refreshTokens(): Promise<boolean> {
  const session = getSession();
  if (!session) return false;
  const res = await fetch("/api/auth/refresh", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refreshToken: session.refreshToken }),
  }).catch(() => null);
  if (!res?.ok) return false;
  setSession((await res.json()) as Session);
  return true;
}

function withToken(options: RequestInit = {}): RequestInit {
  const token = getSession()?.accessToken;
  const headers = new Headers(options.headers);
  if (token) headers.set("Authorization", `Bearer ${token}`);
  return { ...options, headers };
}

export async function request<T>(url: string, options?: RequestInit): Promise<T> {
  let response = await fetch(url, withToken(options));

  if (response.status === 401 && getSession()) {
    refreshing ??= refreshTokens().finally(() => { refreshing = null; });
    if (await refreshing) {
      response = await fetch(url, withToken(options));   // retry with the new token
    } else {
      setSession(null);                                   // refresh failed: back to the login page
    }
  }

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(typeof body?.detail === "string" ? body.detail : `Request failed (${response.status})`);
  }
  return response.status === 204 ? (undefined as T) : response.json();
}
