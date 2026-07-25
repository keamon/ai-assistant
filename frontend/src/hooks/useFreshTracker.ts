import { useEffect, useRef, useState } from "react";

/**
 * Returns the set of ids that appeared since the previous data update, so the UI
 * can briefly highlight items an assistant action just created. The initial seed
 * is never flashed.
 */
export function useFreshTracker(ids: string[]): Set<string> {
  const seen = useRef<Set<string>>(new Set());
  const inited = useRef(false);
  const [fresh, setFresh] = useState<Set<string>>(new Set());

  useEffect(() => {
    const newly = new Set<string>();
    ids.forEach((id) => {
      if (!seen.current.has(id)) {
        if (inited.current) newly.add(id);
        seen.current.add(id);
      }
    });
    inited.current = true;
    if (newly.size) {
      setFresh(newly);
      const t = setTimeout(() => setFresh(new Set()), 4000);
      return () => clearTimeout(t);
    }
  }, [ids.join(",")]);

  return fresh;
}
