// Run an async function now and then every `ms` milliseconds, until the page closes.
import { useEffect, useRef } from "react";

export function usePolling(fn: () => Promise<void>, ms: number) {
  const saved = useRef(fn);
  useEffect(() => {
    saved.current = fn;            // always call the latest version of fn
  });

  useEffect(() => {
    saved.current();
    const timer = setInterval(() => saved.current(), ms);
    return () => clearInterval(timer);   // cleanup: stop the timer
  }, [ms]);
}
