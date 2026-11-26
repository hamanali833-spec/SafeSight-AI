// Gives every component the logged-in user, plus login() and logout().
import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { loginRequest } from "../api/auth";
import type { Role, User } from "../types/auth";
import { getSession, onSessionChange, setSession } from "./session";

type AuthValue = {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  can: (...roles: Role[]) => boolean;    // e.g. can("admin", "supervisor")
};

const AuthContext = createContext<AuthValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(getSession()?.user ?? null);

  // Follow the session: login, token refresh, or forced logout (refresh failed)
  useEffect(() => onSessionChange((s) => setUser(s?.user ?? null)), []);

  const value: AuthValue = {
    user,
    login: async (email, password) => setSession(await loginRequest(email, password)),
    logout: () => setSession(null),
    can: (...roles) => !!user && roles.includes(user.role),
  };
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside <AuthProvider>");
  return ctx;
}
