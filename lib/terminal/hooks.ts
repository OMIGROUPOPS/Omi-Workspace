// Terminal shared hooks — animation utilities

import { useRef, useEffect, useState } from "react";

/** Store the previous render's value */
export function usePrevious<T>(value: T): T | undefined {
  const ref = useRef<T | undefined>(undefined);
  useEffect(() => {
    ref.current = value;
  });
  return ref.current;
}

/** Smoothly interpolate a number via requestAnimationFrame + cubic ease-out */
export function useAnimatedNumber(target: number, durationMs = 400): number {
  const [display, setDisplay] = useState(target);
  const animRef = useRef<number | null>(null);
  const startRef = useRef({ value: target, time: 0 });
  const targetRef = useRef(target);

  useEffect(() => {
    if (target === targetRef.current) return;

    const from = display;
    targetRef.current = target;
    startRef.current = { value: from, time: performance.now() };

    if (animRef.current) cancelAnimationFrame(animRef.current);

    const animate = (now: number) => {
      const elapsed = now - startRef.current.time;
      const t = Math.min(1, elapsed / durationMs);
      // Cubic ease-out: 1 - (1-t)^3
      const eased = 1 - Math.pow(1 - t, 3);
      const current = startRef.current.value + (targetRef.current - startRef.current.value) * eased;
      setDisplay(Math.round(current));

      if (t < 1) {
        animRef.current = requestAnimationFrame(animate);
      }
    };

    animRef.current = requestAnimationFrame(animate);
    return () => {
      if (animRef.current) cancelAnimationFrame(animRef.current);
    };
  }, [target, durationMs]); // eslint-disable-line react-hooks/exhaustive-deps

  return display;
}
