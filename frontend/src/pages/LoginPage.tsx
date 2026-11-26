// Login screen. Left: what SafeSight is (so a visitor understands the product
// before signing in). Right: the sign-in form with one-click demo accounts.
import { useState, type FormEvent } from "react";
import { useAuth } from "../auth/AuthContext";
import { Logo } from "../components/Logo";
import { AlertIcon, EyeIcon, HelmetIcon, MoonIcon, SunIcon, ZoneIcon } from "../components/Icons";
import type { Theme } from "../components/useTheme";

const FEATURES = [
  { Icon: HelmetIcon, title: "Helmet & vest checks", text: "See right away when someone on site isn't wearing their safety gear." },
  { Icon: ZoneIcon, title: "No-go areas", text: "Mark the dangerous spots on each camera and know when someone steps in." },
  { Icon: AlertIcon, title: "Alerts that matter", text: "One clear alert per incident, so your team acts instead of scrolling." },
];

// Demo accounts are filled in with one click (they exist only in the demo database)
const DEMO = [
  { role: "Admin", email: "admin@safesight.ai", password: "admin123", hint: "Full control" },
  { role: "Supervisor", email: "supervisor@safesight.ai", password: "super123", hint: "Resolve & upload" },
  { role: "Guard", email: "guard@safesight.ai", password: "guard123", hint: "View only" },
];

// A drawn "CCTV frame" that shows what the system does: boxes, statuses and a zone
function CctvPreview() {
  return (
    <div className="relative overflow-hidden rounded-2xl border border-slate-200 bg-neutral-900 shadow-xl dark:border-white/10 dark:shadow-2xl">
      <svg viewBox="0 0 480 260" className="block w-full" role="img" aria-label="Example camera view">
        <defs>
          <linearGradient id="floor" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stopColor="#262626" />
            <stop offset="1" stopColor="#171717" />
          </linearGradient>
          <pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse">
            <rect width="4" height="1" fill="#ffffff" opacity="0.025" />
          </pattern>
        </defs>
        <rect width="480" height="260" fill="url(#floor)" />
        {/* shelves / walls */}
        <rect x="0" y="40" width="480" height="70" fill="#1f1f1f" />
        {[30, 120, 210].map((x) => <rect key={x} x={x} y="52" width="70" height="46" rx="3" fill="#2a2a2a" />)}
        {/* restricted zone */}
        <polygon points="320,150 470,140 478,250 300,250" fill="#ef4444" fillOpacity="0.14" stroke="#ef4444" strokeWidth="2" strokeDasharray="6 4" />
        <text x="308" y="244" fill="#f87171" fontSize="10" fontFamily="monospace" fontWeight="700">KEEP OUT</text>
        {/* worker 1: safe */}
        <g>
          <circle cx="95" cy="138" r="9" fill="#facc15" />
          <rect x="84" y="148" width="22" height="36" rx="5" fill="#f97316" />
          <rect x="86" y="184" width="7" height="30" fill="#404040" /><rect x="97" y="184" width="7" height="30" fill="#404040" />
          <rect x="72" y="124" width="46" height="96" fill="none" stroke="#22c55e" strokeWidth="2" />
          <rect x="72" y="110" width="58" height="14" fill="#22c55e" />
          <text x="75" y="120" fill="#000" fontSize="9" fontFamily="monospace" fontWeight="700">ALL GOOD</text>
        </g>
        {/* worker 2: no helmet */}
        <g>
          <circle cx="215" cy="142" r="9" fill="#d6a77a" />
          <rect x="204" y="152" width="22" height="34" rx="5" fill="#f97316" />
          <rect x="206" y="186" width="7" height="28" fill="#404040" /><rect x="217" y="186" width="7" height="28" fill="#404040" />
          <rect x="192" y="128" width="46" height="92" fill="none" stroke="#f59e0b" strokeWidth="2" />
          <rect x="192" y="114" width="66" height="14" fill="#f59e0b" />
          <text x="195" y="124" fill="#000" fontSize="9" fontFamily="monospace" fontWeight="700">NO HELMET</text>
        </g>
        {/* worker 3: inside the zone */}
        <g>
          <circle cx="395" cy="168" r="9" fill="#d6a77a" />
          <rect x="384" y="178" width="22" height="34" rx="5" fill="#3b82f6" />
          <rect x="386" y="212" width="7" height="26" fill="#404040" /><rect x="397" y="212" width="7" height="26" fill="#404040" />
          <rect x="372" y="154" width="46" height="88" fill="none" stroke="#ef4444" strokeWidth="2" />
          <rect x="372" y="140" width="72" height="14" fill="#ef4444" />
          <text x="375" y="150" fill="#fff" fontSize="9" fontFamily="monospace" fontWeight="700">NO-GO AREA</text>
        </g>
        <rect width="480" height="260" fill="url(#scan)" />
        {/* camera overlay text */}
        <circle cx="16" cy="16" r="4" fill="#ef4444"><animate attributeName="opacity" values="1;0.2;1" dur="1.4s" repeatCount="indefinite" /></circle>
        <text x="26" y="20" fill="#fff" fontSize="10" fontFamily="monospace" fontWeight="700">REC · CAM 01 · WAREHOUSE</text>
        <text x="372" y="20" fill="#a3a3a3" fontSize="10" fontFamily="monospace">14:32:07</text>
      </svg>
      {/* floating alert, like the dashboard shows */}
      <div className="absolute left-3 bottom-3 flex items-center gap-2 rounded-lg border border-red-500/30 bg-black/80 px-3 py-2 text-xs text-white backdrop-blur">
        <span className="h-2 w-2 animate-pulse rounded-full bg-red-500" />
        <span>Someone entered a no-go area</span>
      </div>
    </div>
  );
}

export function LoginPage({ theme, onToggleTheme }: { theme: Theme; onToggleTheme: () => void }) {
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function submit(e: FormEvent) {
    e.preventDefault();               // stop the browser reloading the page
    setBusy(true);
    setError(null);
    try {
      await login(email, password);   // on success AuthContext switches to the dashboard
    } catch (err) {
      setError(err instanceof Error && err.message.startsWith("Request failed")
        ? "We couldn't connect just now. Please try again in a moment."
        : err instanceof Error ? err.message : "Login failed");
      setBusy(false);
    }
  }

  const input = "w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-sm outline-none transition focus:border-yellow-500 focus:ring-2 focus:ring-yellow-400/30 dark:border-neutral-700 dark:bg-neutral-900 dark:text-white";

  return (
    <div className="min-h-screen bg-slate-50 lg:grid lg:grid-cols-[1.15fr_1fr] dark:bg-black">
      {/* Left: the product story (white in light theme, black in dark theme) */}
      <section className="relative hidden overflow-hidden border-r border-slate-200 bg-white px-12 py-8 text-slate-900 lg:flex lg:flex-col dark:border-neutral-800 dark:bg-neutral-950 dark:text-white">

        <div className="relative flex items-center gap-3">
          <Logo className="h-10 w-10" />
          <div>
            <p className="text-lg font-bold leading-tight">SafeSight AI</p>
            <p className="text-xs text-slate-500 dark:text-neutral-400">Workplace safety monitoring</p>
          </div>
        </div>

        <div className="relative my-auto py-6">
          <div className="max-w-xl">
            <p className="mb-3 text-sm font-medium text-yellow-700 dark:text-yellow-400">
              For warehouses, offices and construction sites
            </p>
            <h1 className="text-[2.4rem] font-bold leading-tight tracking-tight">
              Every camera watching out for your people
            </h1>
            <p className="mt-3 text-[15px] text-slate-600 dark:text-neutral-400">
              SafeSight works with the CCTV cameras you already have. It notices when someone
              is missing a helmet or vest, or walks into an area they shouldn't, and tells
              the right person straight away.
            </p>
          </div>

          <div className="mt-6 max-w-lg"><CctvPreview /></div>

          <div className="mt-8 grid max-w-xl grid-cols-3 gap-5">
            {FEATURES.map(({ Icon, title, text }) => (
              <div key={title}>
                <div className="mb-1.5 inline-flex rounded-lg bg-yellow-400/20 p-2 text-yellow-700 dark:bg-yellow-400/10 dark:text-yellow-400"><Icon className="h-5 w-5" /></div>
                <p className="text-sm font-semibold">{title}</p>
                <p className="mt-1 text-xs leading-relaxed text-slate-500 dark:text-neutral-400">{text}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Right: sign-in form */}
      <section className="relative flex min-h-screen flex-col px-6 py-8 sm:px-12">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 lg:invisible">
            <Logo className="h-8 w-8" />
            <span className="font-bold text-slate-900 dark:text-white">SafeSight AI</span>
          </div>
          <button onClick={onToggleTheme} aria-label="Switch theme"
                  className="rounded-lg border border-slate-200 p-2 text-slate-600 hover:bg-slate-100 dark:border-neutral-800 dark:text-neutral-300 dark:hover:bg-neutral-900">
            {theme === "dark" ? <SunIcon className="h-4 w-4" /> : <MoonIcon className="h-4 w-4" />}
          </button>
        </div>

        <div className="m-auto w-full max-w-sm py-10">
          {/* Short product line for phones, where the left side is hidden */}
          <p className="mb-6 text-sm text-slate-500 lg:hidden dark:text-neutral-400">
            Safety alerts from the CCTV cameras you already have.
          </p>
          <h2 className="text-2xl font-bold text-slate-900 dark:text-white">Welcome back</h2>
          <p className="mt-1 text-sm text-slate-500 dark:text-neutral-400">Sign in to your safety dashboard</p>

          <form onSubmit={submit} className="mt-8 space-y-4">
            <div>
              <label htmlFor="email" className="mb-1.5 block text-sm font-medium text-slate-700 dark:text-neutral-300">Email</label>
              <input id="email" type="email" autoComplete="username" required value={email}
                     onChange={(e) => setEmail(e.target.value)} placeholder="you@company.com" className={input} />
            </div>
            <div>
              <label htmlFor="password" className="mb-1.5 block text-sm font-medium text-slate-700 dark:text-neutral-300">Password</label>
              <div className="relative">
                <input id="password" type={showPassword ? "text" : "password"} autoComplete="current-password" required
                       value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Enter your password" className={`${input} pr-10`} />
                <button type="button" onClick={() => setShowPassword((v) => !v)}
                        aria-label={showPassword ? "Hide password" : "Show password"}
                        className={`absolute inset-y-0 right-0 px-3 ${showPassword ? "text-yellow-500" : "text-slate-400 hover:text-slate-600 dark:hover:text-neutral-200"}`}>
                  <EyeIcon className="h-4 w-4" />
                </button>
              </div>
            </div>

            {error && (
              <p role="alert" className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700 dark:border-red-500/30 dark:bg-red-500/10 dark:text-red-400">
                {error}
              </p>
            )}

            <button type="submit" disabled={busy}
                    className="w-full rounded-lg bg-yellow-400 py-2.5 text-sm font-semibold text-black shadow-sm transition hover:bg-yellow-300 disabled:opacity-60">
              {busy ? "Signing in..." : "Sign in"}
            </button>
          </form>

          <div className="mt-8">
            <p className="mb-3 text-center text-xs font-medium uppercase tracking-wide text-slate-400 dark:text-neutral-500">
              Try a demo account
            </p>
            <div className="grid grid-cols-3 gap-2">
              {DEMO.map((d) => (
                <button key={d.role} type="button"
                        onClick={() => { setEmail(d.email); setPassword(d.password); setError(null); }}
                        className={`rounded-lg border px-2 py-2 text-left transition ${email === d.email
                          ? "border-yellow-400 bg-yellow-50 dark:bg-yellow-400/10"
                          : "border-slate-200 hover:border-slate-300 dark:border-neutral-800 dark:hover:border-neutral-700"}`}>
                  <p className="text-sm font-semibold text-slate-800 dark:text-neutral-100">{d.role}</p>
                  <p className="text-[11px] text-slate-500 dark:text-neutral-500">{d.hint}</p>
                </button>
              ))}
            </div>
          </div>
        </div>

        <p className="text-center text-xs text-slate-400 dark:text-neutral-600">
          © 2026 SafeSight · Need access? Ask your site administrator.
        </p>
      </section>
    </div>
  );
}
