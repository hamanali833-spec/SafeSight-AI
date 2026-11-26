// Dark / light theme, remembered in this browser. Storage can be blocked, so never crash on it.
import { useEffect, useState } from "react";

export type Theme = "dark" | "light";

function loadTheme(): Theme {
  try { return localStorage.getItem("theme") === "light" ? "light" : "dark"; } catch { return "dark"; }
}

export function useTheme() {
  const [theme, setTheme] = useState<Theme>(loadTheme);
  // Put "dark" on <html> so every dark: style in the app switches on
  useEffect(() => {
    document.documentElement.classList.toggle("dark", theme === "dark");
    try { localStorage.setItem("theme", theme); } catch { /* ignore */ }
  }, [theme]);
  const toggle = () => setTheme((t) => (t === "dark" ? "light" : "dark"));
  return { theme, toggle };
}
