// Where the login tokens live in the browser, and who gets told when they change.
//
// Tokens are kept in localStorage so a page refresh doesn't log you out.
// (Trade-off for the viva: an httpOnly cookie is safer against XSS, but needs
//  more backend setup. Access tokens are short-lived (30 min) to limit the risk.)
import type { User } from "../types/auth";

const KEY = "safesight.session";

export type Session = { accessToken: string; refreshToken: string; user: User };

let current: Session | null = load();
const listeners = new Set<(s: Session | null) => void>();

// Storage can be blocked (private mode, strict settings): never crash on it
function load(): Session | null {
  try { const raw = localStorage.getItem(KEY); return raw ? JSON.parse(raw) : null; } catch { return null; }
}

export const getSession = () => current;

export function setSession(s: Session | null) {
  current = s;
  try { if (s) localStorage.setItem(KEY, JSON.stringify(s)); else localStorage.removeItem(KEY); } catch { /* ignore */ }
  listeners.forEach((fn) => fn(s));
}

// Lets React (AuthContext) re-render when we log in, refresh or get logged out
export function onSessionChange(fn: (s: Session | null) => void) {
  listeners.add(fn);
  return () => { listeners.delete(fn); };
}
