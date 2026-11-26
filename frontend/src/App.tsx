// SafeSight app shell: the login page when signed out; otherwise sidebar
// navigation, top bar (status, theme, user + logout) and the selected page.
import { useState } from "react";
import { useAuth } from "./auth/AuthContext";
import { Logo } from "./components/Logo";
import { useTheme } from "./components/useTheme";
import { LoginPage } from "./pages/LoginPage";
import type { Role } from "./types/auth";
import { AlertsPage } from "./pages/AlertsPage";
import { AnalyticsPage } from "./pages/AnalyticsPage";
import { MonitoringPage } from "./pages/MonitoringPage";
import { CamerasPage } from "./pages/CamerasPage";
import { BellIcon, CameraIcon, ChartIcon, LogoutIcon, MoonIcon, SunIcon, ZoneIcon } from "./components/Icons";

type Page = "monitoring" | "alerts" | "analytics" | "cameras";
// roles: who sees the page (the backend checks again, the UI only hides what you can't use)
const PAGES: { id: Page; label: string; title: string; Icon: typeof CameraIcon; roles?: Role[] }[] = [
  { id: "monitoring", label: "Monitoring", title: "Live monitoring · all cameras", Icon: CameraIcon },
  { id: "alerts", label: "Alerts", title: "Alerts", Icon: BellIcon },
  { id: "analytics", label: "Analytics", title: "Analytics", Icon: ChartIcon },
  { id: "cameras", label: "Cameras & zones", title: "Cameras & restricted zones", Icon: ZoneIcon, roles: ["admin"] },
];

const ROLE_STYLE: Record<Role, string> = {
  admin: "bg-yellow-100 text-yellow-800 dark:bg-yellow-400/15 dark:text-yellow-300",
  supervisor: "bg-blue-100 text-blue-700 dark:bg-blue-500/15 dark:text-blue-300",
  guard: "bg-slate-100 text-slate-600 dark:bg-neutral-800 dark:text-neutral-300",
};

export default function App() {
  const { user, logout, can } = useAuth();
  const { theme, toggle } = useTheme();
  const [page, setPage] = useState<Page>("monitoring");
  const [error, setError] = useState<string | null>(null);

  if (!user) return <LoginPage theme={theme} onToggleTheme={toggle} />;

  const pages = PAGES.filter((p) => !p.roles || can(...p.roles));
  const current = pages.find((p) => p.id === page) ?? pages[0];

  return (
    <div className="min-h-screen bg-slate-100 text-slate-900 md:flex dark:bg-black dark:text-neutral-100">
      {/* Sidebar */}
      <aside className="border-b border-slate-200 bg-white md:sticky md:top-0 md:flex md:h-screen md:w-60 md:shrink-0 md:flex-col md:border-r md:border-b-0 dark:border-neutral-800 dark:bg-neutral-950">
        <div className="flex items-center gap-2 px-5 py-4">
          <Logo className="h-9 w-9" />
          <div>
            <p className="text-sm font-bold leading-tight">SafeSight AI</p>
            <p className="text-xs text-slate-500 dark:text-neutral-500">Workplace safety</p>
          </div>
        </div>
        <nav className="flex gap-1 overflow-x-auto px-3 pb-3 md:flex-col md:pb-0">
          {pages.map(({ id, label, Icon }) => (
            <button
              key={id}
              onClick={() => setPage(id)}
              className={`flex shrink-0 items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium ${
                current.id === id
                  ? "bg-slate-900 text-white dark:bg-white dark:text-black"
                  : "text-slate-600 hover:bg-slate-100 dark:text-neutral-400 dark:hover:bg-neutral-900"
              }`}
            >
              <Icon className="h-4.5 w-4.5" />
              {label}
            </button>
          ))}
        </nav>
        <p className="mt-auto hidden px-5 py-4 text-xs text-slate-400 md:block dark:text-neutral-600">
          Need help? Contact your site administrator.
        </p>
      </aside>

      {/* Main area */}
      <div className="min-w-0 flex-1">
        <header className="flex items-center justify-between border-b border-slate-200 bg-white px-6 py-4 dark:border-neutral-800 dark:bg-neutral-950">
          <h1 className="text-lg font-semibold">{current.title}</h1>
          <div className="flex items-center gap-4">
            <span className={`flex items-center gap-1.5 text-xs font-medium ${error ? "text-red-500" : "text-green-600 dark:text-green-400"}`}>
              <span className={`h-2 w-2 rounded-full ${error ? "bg-red-500" : "bg-green-500"}`} />
              {error ? "Reconnecting..." : "All cameras connected"}
            </span>
            <button
              onClick={toggle}
              className="rounded-lg border border-slate-200 p-2 text-slate-600 hover:bg-slate-100 dark:border-neutral-800 dark:text-neutral-300 dark:hover:bg-neutral-900"
              aria-label="Switch theme"
              title={theme === "dark" ? "Light theme" : "Dark theme"}
            >
              {theme === "dark" ? <SunIcon className="h-4 w-4" /> : <MoonIcon className="h-4 w-4" />}
            </button>
            <div className="flex items-center gap-3 border-l border-slate-200 pl-4 dark:border-neutral-800">
              <div className="hidden text-right sm:block">
                <p className="text-sm font-medium leading-tight">{user.name}</p>
                <span className={`rounded px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide ${ROLE_STYLE[user.role]}`}>
                  {user.role}
                </span>
              </div>
              <button onClick={logout} title="Log out" aria-label="Log out"
                      className="rounded-lg border border-slate-200 p-2 text-slate-600 hover:bg-slate-100 dark:border-neutral-800 dark:text-neutral-300 dark:hover:bg-neutral-900">
                <LogoutIcon className="h-4 w-4" />
              </button>
            </div>
          </div>
        </header>

        <main className="mx-auto max-w-7xl p-6">
          {error && (
            <p className="mb-6 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700 dark:border-red-500/30 dark:bg-red-500/10 dark:text-red-400">
              {error}
            </p>
          )}
          {current.id === "monitoring" && <MonitoringPage onError={setError} />}
          {current.id === "alerts" && <AlertsPage onError={setError} />}
          {current.id === "analytics" && <AnalyticsPage onError={setError} />}
          {current.id === "cameras" && <CamerasPage />}
        </main>
      </div>
    </div>
  );
}
