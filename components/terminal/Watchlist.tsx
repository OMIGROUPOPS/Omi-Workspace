"use client";

// OMI Terminal — Watchlist sidebar
// Category-grouped ticker list with two-line rows, sparklines, price flash animations.

import { useState, useMemo, useRef, useEffect } from "react";
import type { WatchlistItem, CategoryData, CategoryTicker } from "@/lib/terminal/types";
import { parseTickerLabel } from "@/lib/terminal/ticker-labels";

interface WatchlistProps {
  categories?: CategoryData[];
  items?: WatchlistItem[];
  selectedTicker?: string;
  onSelect?: (ticker: string) => void;
}

export default function Watchlist({
  categories,
  items = [],
  selectedTicker,
  onSelect,
}: WatchlistProps) {
  const [query, setQuery] = useState("");
  const [collapsed, setCollapsed] = useState<Record<string, boolean>>({});

  // Price history accumulation (no re-render cost)
  const priceHistoryRef = useRef<Map<string, number[]>>(new Map());

  // Accumulate price history on each categories poll
  useEffect(() => {
    if (!categories?.length) return;
    for (const cat of categories) {
      for (const t of cat.top_tickers) {
        if (t.mid === null || t.mid === undefined) continue;
        const hist = priceHistoryRef.current.get(t.ticker) ?? [];
        hist.push(t.mid);
        if (hist.length > 20) hist.shift();
        priceHistoryRef.current.set(t.ticker, hist);
      }
    }
  }, [categories]);

  const toggle = (cat: string) =>
    setCollapsed((prev) => ({ ...prev, [cat]: !prev[cat] }));

  const isAutoExpanded = (cat: CategoryData) => {
    if (cat.signals_count > 0) return true;
    if (cat.last_signal_time) {
      const age = Date.now() / 1000 - cat.last_signal_time;
      if (age < 300) return true;
    }
    return false;
  };

  const isCollapsed = (cat: CategoryData) => {
    if (cat.category in collapsed) return collapsed[cat.category];
    return !isAutoExpanded(cat);
  };

  const filteredCategories = useMemo(() => {
    if (!categories?.length) return [];
    if (!query) return categories;
    const q = query.toLowerCase();
    return categories
      .map((cat) => ({
        ...cat,
        top_tickers: cat.top_tickers.filter(
          (t: CategoryTicker) =>
            (t.team || "").toLowerCase().includes(q) ||
            t.ticker.toLowerCase().includes(q),
        ),
      }))
      .filter((cat) => cat.top_tickers.length > 0 || cat.category.toLowerCase().includes(q));
  }, [categories, query]);

  const useFlatList = !categories?.length;
  const flatFiltered = useMemo(() => {
    if (!useFlatList) return [];
    const q = query.toLowerCase();
    return q
      ? items.filter(
          (item) =>
            (item.info?.team || "").toLowerCase().includes(q) ||
            item.ticker.toLowerCase().includes(q),
        )
      : items;
  }, [items, query, useFlatList]);

  return (
    <div className="h-full flex flex-col">
      {/* Search */}
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="/ search"
        style={{
          width: "100%",
          background: "#111",
          border: "1px solid #222",
          borderRadius: "2px",
          padding: "3px 6px",
          fontSize: "9px",
          color: "#888",
          outline: "none",
          marginBottom: "4px",
          boxSizing: "border-box",
        }}
      />

      {/* Ticker list */}
      <div
        className="flex-1 overflow-y-auto"
        style={{ scrollbarWidth: "none" }}
      >
        {useFlatList ? (
          flatFiltered.length === 0 ? (
            <EmptyState text="Scanner Offline" />
          ) : (
            flatFiltered.map((item) => (
              <TickerRow
                key={item.ticker}
                ticker={item.ticker}
                label={item.info?.team || item.ticker.slice(-8)}
                mid={item.mid}
                spread={item.spread}
                move_30s={item.move_30s}
                kyle_lambda={item.kyle_lambda}
                priceHistory={priceHistoryRef.current.get(item.ticker) ?? []}
                isSelected={selectedTicker === item.ticker}
                onSelect={onSelect}
              />
            ))
          )
        ) : filteredCategories.length === 0 ? (
          <EmptyState text={query ? "No matches" : "Loading..."} />
        ) : (
          filteredCategories.map((cat) => {
            const hasSignals = cat.signals_count > 0;
            const recentSignal = cat.last_signal_time
              ? (Date.now() / 1000 - cat.last_signal_time) < 300
              : false;
            const dotColor = hasSignals || recentSignal ? "#00FF88" : "#333";

            return (
              <div key={cat.category}>
                {/* Category header */}
                <button
                  onClick={() => toggle(cat.category)}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "4px",
                    width: "100%",
                    padding: "3px 2px",
                    border: "none",
                    background: "rgba(255,102,0,0.04)",
                    cursor: "pointer",
                    borderBottom: "1px solid #141414",
                  }}
                >
                  <span style={{ fontSize: "7px", color: "#444", width: "8px", flexShrink: 0 }}>
                    {isCollapsed(cat) ? "\u25B8" : "\u25BE"}
                  </span>
                  {/* Signal dot */}
                  <span
                    style={{
                      width: "5px",
                      height: "5px",
                      borderRadius: "50%",
                      background: dotColor,
                      flexShrink: 0,
                      boxShadow: hasSignals ? `0 0 4px ${dotColor}` : "none",
                    }}
                  />
                  <span
                    style={{
                      fontSize: "8.5px",
                      color: "#888",
                      fontWeight: 600,
                      letterSpacing: "0.08em",
                      textTransform: "uppercase",
                      flex: 1,
                      textAlign: "left",
                      overflow: "hidden",
                      whiteSpace: "nowrap",
                      textOverflow: "ellipsis",
                    }}
                  >
                    {cat.category}
                  </span>
                  <div style={{ display: "flex", alignItems: "center", gap: "4px", flexShrink: 0 }}>
                    {cat.signals_count > 0 && (
                      <span style={{
                        fontSize: "7px",
                        fontWeight: 700,
                        padding: "0 3px",
                        borderRadius: "2px",
                        background: "rgba(0,255,136,0.15)",
                        color: "#00FF88",
                        lineHeight: "12px",
                      }}>
                        {cat.signals_count}
                      </span>
                    )}
                    <span
                      style={{
                        fontSize: "8px",
                        color: "#444",
                        fontVariantNumeric: "tabular-nums",
                      }}
                    >
                      {cat.active_tickers.toLocaleString()}
                    </span>
                  </div>
                </button>

                {/* Tickers (when expanded) */}
                {!isCollapsed(cat) &&
                  cat.top_tickers.map((item: CategoryTicker) => (
                    <TickerRow
                      key={item.ticker}
                      ticker={item.ticker}
                      label={parseTickerLabel(item.ticker, item.team, item.event_ticker)}
                      mid={item.mid}
                      spread={item.spread}
                      move_30s={item.move_30s}
                      kyle_lambda={item.kyle_lambda}
                      priceHistory={priceHistoryRef.current.get(item.ticker) ?? []}
                      isSelected={selectedTicker === item.ticker}
                      onSelect={onSelect}
                    />
                  ))}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}

// ── Empty state ─────────────────────────────────────────────

function EmptyState({ text }: { text: string }) {
  return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "48px", color: "#333", fontSize: "9px" }}>
      {text}
    </div>
  );
}

// ── Sparkline SVG ───────────────────────────────────────────

function Sparkline({ data, color }: { data: number[]; color: string }) {
  if (data.length < 2) return null;
  const w = 40, h = 16;
  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1;
  const points = data
    .map((v, i) => `${(i / (data.length - 1)) * w},${h - ((v - min) / range) * h}`)
    .join(" ");
  return (
    <svg width={w} height={h} style={{ flexShrink: 0 }}>
      <polyline points={points} fill="none" stroke={color} strokeWidth={1} opacity={0.6} />
    </svg>
  );
}

// ── Ticker row (two-line layout) ────────────────────────────

function TickerRow({
  ticker,
  label,
  mid,
  spread,
  move_30s,
  kyle_lambda,
  priceHistory,
  isSelected,
  onSelect,
}: {
  ticker: string;
  label: string;
  mid: number | null;
  spread: number;
  move_30s: number | null;
  kyle_lambda: number | null;
  priceHistory: number[];
  isSelected: boolean;
  onSelect?: (ticker: string) => void;
}) {
  const mv = move_30s;
  const priceColor =
    mv !== null && mv > 0 ? "#00FF88" : mv !== null && mv < 0 ? "#FF3366" : "#999";
  const borderColor =
    mv !== null && mv > 0 ? "#00FF88" : mv !== null && mv < 0 ? "#FF3366" : "#333";

  // Price flash tracking
  const prevMidRef = useRef<number | null>(mid);
  const [flashKey, setFlashKey] = useState(0);
  const [flashDir, setFlashDir] = useState<"up" | "down" | null>(null);

  useEffect(() => {
    if (prevMidRef.current !== null && mid !== null && mid !== prevMidRef.current) {
      setFlashDir(mid > prevMidRef.current ? "up" : "down");
      setFlashKey((k) => k + 1);
    }
    prevMidRef.current = mid;
  }, [mid]);

  return (
    <button
      onClick={() => onSelect?.(ticker)}
      style={{
        display: "flex",
        alignItems: "center",
        width: "100%",
        padding: "2px 3px 2px 0",
        fontSize: "9px",
        textAlign: "left",
        cursor: "pointer",
        border: "none",
        transition: "background 0.08s",
        background: isSelected ? "rgba(255,102,0,0.08)" : "transparent",
        color: isSelected ? "#FF6600" : "#999",
        borderLeft: isSelected ? "3px solid #FF6600" : `3px solid ${borderColor}`,
        position: "relative",
        overflow: "hidden",
      }}
    >
      {/* Flash overlay */}
      {flashDir && (
        <div
          key={flashKey}
          style={{
            position: "absolute",
            inset: 0,
            animation: `${flashDir === "up" ? "terminal-flash-green" : "terminal-flash-red"} 0.8s ease-out forwards`,
            pointerEvents: "none",
          }}
        />
      )}

      {/* Content */}
      <div style={{ flex: 1, minWidth: 0, overflow: "hidden", paddingLeft: "4px" }}>
        {/* Line 1: Label ......... Price */}
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", lineHeight: "14px" }}>
          <span
            style={{
              fontWeight: isSelected ? 600 : 500,
              whiteSpace: "nowrap",
              overflow: "hidden",
              textOverflow: "ellipsis",
              fontSize: "9px",
              color: isSelected ? "#FF6600" : "#ccc",
            }}
          >
            {label || ticker.slice(-8)}
          </span>
          <div style={{ display: "flex", alignItems: "center", gap: "2px", flexShrink: 0, marginLeft: "2px" }}>
            {mv !== null && mv !== 0 && (
              <span style={{ fontSize: "6px", color: priceColor, fontWeight: 700, lineHeight: 1 }}>
                {mv > 0 ? "\u25B2" : "\u25BC"}
              </span>
            )}
            <span
              style={{
                fontWeight: 600,
                fontVariantNumeric: "tabular-nums",
                color: priceColor,
                fontSize: "10px",
              }}
            >
              {mid !== null ? `${mid}\u00A2` : "\u2014"}
            </span>
          </div>
        </div>

        {/* Line 2: Ticker · spread · lambda    [sparkline] */}
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", lineHeight: "10px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "0", fontSize: "7px", color: "#444", overflow: "hidden" }}>
            <span style={{ textTransform: "uppercase", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis", maxWidth: "50px" }}>
              {ticker.slice(-8)}
            </span>
            <span style={{ color: "#333", margin: "0 2px" }}>{"\u00B7"}</span>
            <span style={{ fontVariantNumeric: "tabular-nums" }}>{spread}s</span>
            {kyle_lambda !== null && kyle_lambda !== undefined && (
              <>
                <span style={{ color: "#333", margin: "0 2px" }}>{"\u00B7"}</span>
                <span style={{ color: "#00BCD4", fontVariantNumeric: "tabular-nums" }}>{"\u03BB"}{kyle_lambda.toFixed(3)}</span>
              </>
            )}
          </div>
          <Sparkline data={priceHistory} color={priceColor} />
        </div>
      </div>
    </button>
  );
}
