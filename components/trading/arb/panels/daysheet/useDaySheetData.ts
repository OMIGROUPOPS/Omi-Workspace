"use client";

import { useEffect, useState, useCallback, useRef } from "react";
import type { DaySheet } from "./types";

const POLL_MS = 60_000; // day sheet regenerates at most every ~5h; 60s poll just catches the refresh promptly
const STALE_MS = 90 * 60 * 1000; // 90 min — matches this shell's staleness convention elsewhere

export function useDaySheetData() {
  const [sheet, setSheet] = useState<DaySheet | null>(null);
  const [fetchError, setFetchError] = useState(false);
  const [lastFetch, setLastFetch] = useState<Date | null>(null);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const fetchData = useCallback(async () => {
    try {
      const res = await fetch("/api/daysheet", { cache: "no-store" });
      if (res.ok) {
        const data = await res.json();
        if (!data.error) {
          setSheet(data);
          setFetchError(false);
          setLastFetch(new Date());
          return;
        }
      }
      setFetchError(true);
    } catch {
      setFetchError(true);
    }
  }, []);

  useEffect(() => {
    fetchData();
    timerRef.current = setInterval(fetchData, POLL_MS);
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [fetchData]);

  const sourceMtime = sheet?.meta.sourceMtimeIso ? new Date(sheet.meta.sourceMtimeIso) : null;
  const isStale = sourceMtime ? Date.now() - sourceMtime.getTime() > STALE_MS : false;

  return {
    sheet,
    fetchError,
    lastFetch,
    isStale,
    hasData: !!sheet,
    fetchData,
  };
}
