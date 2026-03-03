"use client";

// OMI Terminal — Watchlist sidebar (Redesigned v2)
// Full readable market names, event context, sparklines, price flash.
// Shows "Chicago → Illinois" not "JBUR".

import { useState, useMemo, useRef, useEffect } from "react";
import type { WatchlistItem, CategoryData, CategoryTicker } from "@/lib/terminal/types";
import { parseTickerLabel, parseEventName } from "@/lib/terminal/ticker-labels";

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
            t.ticker.toLowerCase().includes(q) ||
            parseTickerLabel(t.ticker, t.team, t.event_ticker).toLowerCase().includes(q),
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
        placeholder="⌕ Search markets..."
        style={{
          width: "100%",
          background: "#111",
          border: "1px solid #222",
          borderRadius: "4px",
          padding: "6px 10px",
          fontSize: "10px",
          color: "#999",
          outline: "none",
          marginBottom: "6px",
          boxSizing: "border-box",
          transition: "border-color 0.15s, box-shadow 0.15s",
        }}
        onFocus={(e) => {
          e.currentTarget.style.borderColor = "rgba(255,102,0,0.4)";
          e.currentTarget.style.boxShadow = "0 0 8px rgba(255,102,0,0.1)";
        }}
        onBlur={(e) => {
          e.currentTarget.style.borderColor = "#222";
          e.currentTarget.style.boxShadow = "none";
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
                team={item.info?.team || ""}
                eventTicker={item.ticker.replace(/-[YN]$/, "")}
                eventName=""
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
            const isActive = hasSignals || recentSignal;

            return (
              <div key={cat.category}>
                {/* Category header */}
                <button
                  onClick={() => toggle(cat.category)}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "6px",
                    width: "100%",
                    padding: "6px 6px",
                    border: "none",
                    background: isActive ? "rgba(255,102,0,0.08)" : "rgba(255,255,255,0.02)",
                    cursor: "pointer",
                    borderBottom: "1px solid #151515",
                    borderLeft: isActive ? "3px solid #FF6600" : "3px solid #222",
                    transition: "background 0.15s",
                    marginTop: "2px",
                  }}
                >
                  <span style={{ fontSize: "8px", color: "#555", width: "8px", flexShrink: 0 }}>
                    {isCollapsed(cat) ? "\u25B8" : "\u25BE"}
                  </span>
                  {/* Signal dot */}
                  <span
                    style={{
                      width: "6px",
                      height: "6px",
                      borderRadius: "50%",
                      background: isActive ? "#00FF88" : "#333",
                      flexShrink: 0,
                      boxShadow: isActive ? "0 0 8px rgba(0,255,136,0.5)" : "none",
                      animation: isActive ? "terminal-pulse 2s ease-in-out infinite" : "none",
                    }}
                  />
                  <span
                    style={{
                      fontSize: "10px",
                      color: isActive ? "#ddd" : "#888",
                      fontWeight: 700,
                      letterSpacing: "0.06em",
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
                  <div style={{ display: "flex", alignItems: "center", gap: "6px", flexShrink: 0 }}>
                    {cat.signals_count > 0 && (
                      <span style={{
                        fontSize: "8px",
                        fontWeight: 700,
                        padding: "1px 5px",
                        borderRadius: "4px",
                        background: "rgba(0,255,136,0.15)",
                        color: "#00FF88",
                        lineHeight: "14px",
                      }}>
                        {cat.signals_count}
                      </span>
                    )}
                    <span
                      style={{
                        fontSize: "9px",
                        color: "#555",
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
                      team={item.team}
                      eventTicker={item.event_ticker}
                      eventName={parseEventName(item.event_ticker)}
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
    <div style={{
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center",
      height: "100px",
      color: "#444",
      fontSize: "10px",
      gap: "8px",
    }}>
      <span style={{ fontSize: "20px", opacity: 0.3 }}>{"\u25C8"}</span>
      {text}
    </div>
  );
}

// ── Sparkline SVG ───────────────────────────────────────────

function Sparkline({ data, color }: { data: number[]; color: string }) {
  if (data.length < 2) return null;
  const w = 44, h = 16;
  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1;
  const points = data
    .map((v, i) => `${(i / (data.length - 1)) * w},${h - ((v - min) / range) * (h - 2) - 1}`)
    .join(" ");

  // Last point for dot
  const lastX = w;
  const lastY = h - ((data[data.length - 1] - min) / range) * (h - 2) - 1;

  return (
    <svg width={w} height={h} style={{ flexShrink: 0 }}>
      <polyline points={points} fill="none" stroke={color} strokeWidth={1.2} opacity={0.6} />
      <circle cx={lastX} cy={lastY} r={2} fill={color} opacity={0.9} />
    </svg>
  );
}

// ── Ticker row — full readable name ────────────────────────

function TickerRow({
  ticker,
  team,
  eventTicker,
  eventName,
  mid,
  spread,
  move_30s,
  kyle_lambda,
  priceHistory,
  isSelected,
  onSelect,
}: {
  ticker: string;
  team: string;
  eventTicker: string;
  eventName: string;
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

  // Build full readable label
  const label = parseTickerLabel(ticker, team, eventTicker);

  return (
    <button
      onClick={() => onSelect?.(ticker)}
      style={{
        display: "flex",
        alignItems: "center",
        width: "100%",
        padding: "5px 6px 5px 0",
        fontSize: "10px",
        textAlign: "left",
        cursor: "pointer",
        border: "none",
        transition: "background 0.1s",
        background: isSelected ? "rgba(255,102,0,0.1)" : "transparent",
        color: isSelected ? "#FF6600" : "#ccc",
        borderLeft: isSelected ? "3px solid #FF6600" : "3px solid transparent",
        position: "relative",
        overflow: "hidden",
      }}
      onMouseEnter={(e) => { if (!isSelected) e.currentTarget.style.background = "rgba(255,255,255,0.03)"; }}
      onMouseLeave={(e) => { if (!isSelected) e.currentTarget.style.background = "transparent"; }}
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
      <div style={{ flex: 1, minWidth: 0, overflow: "hidden", paddingLeft: "6px" }}>
        {/* Line 1: Full market name + Price */}
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", lineHeight: "16px" }}>
          <span
            style={{
              fontWeight: isSelected ? 700 : 600,
              whiteSpace: "nowrap",
              overflow: "hidden",
              textOverflow: "ellipsis",
              fontSize: "10.5px",
              color: isSelected ? "#FF6600" : "#ddd",
              maxWidth: "120px",
            }}
            title={label}
          >
            {label || team || ticker.slice(-8)}
          </span>
          <div style={{ display: "flex", alignItems: "center", gap: "3px", flexShrink: 0, marginLeft: "6px" }}>
            {mv !== null && mv !== 0 && (
              <span style={{ fontSize: "8px", color: priceColor, fontWeight: 700, lineHeight: 1 }}>
                {mv > 0 ? "\u25B2" : "\u25BC"}
              </span>
            )}
            <span
              style={{
                fontWeight: 700,
                fontVariantNumeric: "tabular-nums",
                color: priceColor,
                fontSize: "11px",
              }}
            >
              {mid !== null ? `${mid}\u00A2` : "\u2014"}
            </span>
          </div>
        </div>

        {/* Line 2: Event name + spread + sparkline */}
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", lineHeight: "12px", marginTop: "2px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "0", fontSize: "8px", color: "#555", overflow: "hidden" }}>
            {eventName && (
              <span style={{
                whiteSpace: "nowrap",
                overflow: "hidden",
                textOverflow: "ellipsis",
                maxWidth: "80px",
                color: "#444",
              }}>
                {eventName}
              </span>
            )}
            {!eventName && (
              <span style={{
                whiteSpace: "nowrap",
                overflow: "hidden",
                textOverflow: "ellipsis",
                maxWidth: "55px",
                color: "#333",
                textTransform: "uppercase",
              }}>
                {ticker.slice(-10)}
              </span>
            )}
            <span style={{ color: "#2a2a2a", margin: "0 3px" }}>{"\u00B7"}</span>
            <span style={{ fontVariantNumeric: "tabular-nums", color: spread <= 2 ? "#666" : "#444" }}>{spread}s</span>
            {kyle_lambda !== null && kyle_lambda !== undefined && (
              <>
                <span style={{ color: "#2a2a2a", margin: "0 3px" }}>{"\u00B7"}</span>
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
