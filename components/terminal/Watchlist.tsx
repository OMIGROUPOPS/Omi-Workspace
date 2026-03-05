"use client";

// OMI Terminal — Watchlist sidebar (Modular Box v4)
// Inner content of parent TermBox — no outer border/header.
// Full readable market names, event context, sparklines, price flash.
// Collapsible categories. Fetches full market names from /api/kalshi/market.

import { useState, useMemo, useRef, useEffect, useCallback } from "react";
import type { WatchlistItem, CategoryData, CategoryTicker } from "@/lib/terminal/types";
import { parseTickerLabel, parseEventName } from "@/lib/terminal/ticker-labels";

interface WatchlistProps {
  categories?: CategoryData[];
  items?: WatchlistItem[];
  selectedTicker?: string;
  onSelect?: (ticker: string) => void;
}

// ── Market name cache ──────────────────────────────────────
const marketNameCache = new Map<string, string>();
const pendingFetches = new Set<string>();

async function fetchMarketName(ticker: string): Promise<string | null> {
  if (marketNameCache.has(ticker)) return marketNameCache.get(ticker)!;
  if (pendingFetches.has(ticker)) return null;
  pendingFetches.add(ticker);
  try {
    const res = await fetch(`/api/kalshi/market?ticker=${encodeURIComponent(ticker)}`, { cache: "no-store" });
    if (res.ok) {
      const data = await res.json();
      const title = data?.market?.title || data?.title || null;
      if (title) {
        marketNameCache.set(ticker, title);
        return title;
      }
    }
  } catch {
    // fallback to parsed label
  } finally {
    pendingFetches.delete(ticker);
  }
  return null;
}

export default function Watchlist({
  categories,
  items = [],
  selectedTicker,
  onSelect,
}: WatchlistProps) {
  const [query, setQuery] = useState("");
  const [collapsed, setCollapsed] = useState<Record<string, boolean>>({});
  const [, setNameTick] = useState(0); // force re-render when names arrive

  // Price history accumulation (no re-render cost)
  const priceHistoryRef = useRef<Map<string, number[]>>(new Map());

  // Batch fetch market names for visible tickers
  const fetchNamesForTickers = useCallback((tickers: string[]) => {
    const toFetch = tickers.filter(t => !marketNameCache.has(t) && !pendingFetches.has(t));
    if (toFetch.length === 0) return;
    // Fetch in batches of 5 to avoid hammering
    const batch = toFetch.slice(0, 5);
    Promise.all(batch.map(fetchMarketName)).then(() => {
      setNameTick(t => t + 1);
    });
  }, []);

  // Accumulate price history on each categories poll
  useEffect(() => {
    if (!categories?.length) return;
    const tickers: string[] = [];
    for (const cat of categories) {
      for (const t of cat.top_tickers) {
        if (t.mid === null || t.mid === undefined) continue;
        const hist = priceHistoryRef.current.get(t.ticker) ?? [];
        hist.push(t.mid);
        if (hist.length > 20) hist.shift();
        priceHistoryRef.current.set(t.ticker, hist);
        tickers.push(t.ticker);
      }
    }
    fetchNamesForTickers(tickers);
  }, [categories, fetchNamesForTickers]);

  const toggle = (cat: string) =>
    setCollapsed((prev) => ({ ...prev, [cat]: !prev[cat] }));

  const isAutoExpanded = (cat: CategoryData) => {
    // Only auto-expand if the category has actual tickers to show
    if (cat.top_tickers.length === 0) return false;
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
    // Sort: categories with tickers first, empty ones at the bottom
    const sorted = [...categories].sort((a, b) => {
      const aHas = a.top_tickers.length > 0 ? 1 : 0;
      const bHas = b.top_tickers.length > 0 ? 1 : 0;
      return bHas - aHas;
    });
    if (!query) return sorted;
    const q = query.toLowerCase();
    return sorted
      .map((cat) => ({
        ...cat,
        top_tickers: cat.top_tickers.filter(
          (t: CategoryTicker) =>
            (t.team || "").toLowerCase().includes(q) ||
            t.ticker.toLowerCase().includes(q) ||
            parseTickerLabel(t.ticker, t.team, t.event_ticker).toLowerCase().includes(q) ||
            (marketNameCache.get(t.ticker) || "").toLowerCase().includes(q),
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
    <div
      style={{
        height: "100%",
        display: "flex",
        flexDirection: "column",
        background: "transparent",
      }}
    >
      {/* Search */}
      <div style={{ flexShrink: 0, padding: "0 0 6px 0" }}>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search markets..."
          style={{
            width: "100%",
            background: "rgba(255,255,255,0.03)",
            border: "1px solid #1e1e1e",
            borderRadius: "3px",
            padding: "5px 8px",
            fontSize: "10px",
            color: "#999",
            outline: "none",
            boxSizing: "border-box",
            transition: "border-color 0.15s, box-shadow 0.15s",
            fontFamily: "inherit",
          }}
          onFocus={(e) => {
            e.currentTarget.style.borderColor = "rgba(255,102,0,0.35)";
            e.currentTarget.style.boxShadow = "0 0 6px rgba(255,102,0,0.08)";
          }}
          onBlur={(e) => {
            e.currentTarget.style.borderColor = "#1e1e1e";
            e.currentTarget.style.boxShadow = "none";
          }}
        />
      </div>

      {/* Ticker list */}
      <div
        style={{
          flex: 1,
          overflowY: "auto",
          scrollbarWidth: "none",
        }}
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
                    gap: "5px",
                    width: "100%",
                    padding: "5px 8px 5px 6px",
                    border: "none",
                    background: isActive ? "rgba(255,102,0,0.05)" : "rgba(255,255,255,0.012)",
                    cursor: "pointer",
                    borderBottom: "1px solid #111",
                    borderLeft: isActive ? "2px solid #FF6600" : "2px solid #1a1a1a",
                    transition: "background 0.15s",
                    marginTop: "1px",
                    borderRadius: "0 2px 2px 0",
                    fontFamily: "inherit",
                  }}
                >
                  <span style={{ fontSize: "7px", color: "#3a3a3a", width: "8px", flexShrink: 0 }}>
                    {isCollapsed(cat) ? "▸" : "▾"}
                  </span>

                  {isActive && (
                    <span
                      style={{
                        width: "4px",
                        height: "4px",
                        borderRadius: "50%",
                        background: "#00FF88",
                        flexShrink: 0,
                        boxShadow: "0 0 5px rgba(0,255,136,0.45)",
                        animation: "terminal-pulse 2s ease-in-out infinite",
                      }}
                    />
                  )}

                  <span
                    style={{
                      fontSize: "9px",
                      color: isActive ? "#c0c0c0" : "#555",
                      fontWeight: 700,
                      letterSpacing: "0.07em",
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

                  <div style={{ display: "flex", alignItems: "center", gap: "5px", flexShrink: 0 }}>
                    {cat.signals_count > 0 && (
                      <span
                        style={{
                          fontSize: "7px",
                          fontWeight: 700,
                          padding: "1px 4px",
                          borderRadius: "3px",
                          background: "rgba(0,255,136,0.1)",
                          color: "#00FF88",
                          lineHeight: "12px",
                        }}
                      >
                        {cat.signals_count}
                      </span>
                    )}
                    <span
                      style={{
                        fontSize: "8px",
                        color: "#3a3a3a",
                        fontVariantNumeric: "tabular-nums",
                      }}
                    >
                      {cat.active_tickers}
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
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        height: "80px",
        color: "#333",
        fontSize: "10px",
        gap: "8px",
      }}
    >
      <span style={{ fontSize: "16px", opacity: 0.25 }}>◈</span>
      {text}
    </div>
  );
}

// ── Sparkline SVG ───────────────────────────────────────────

function Sparkline({ data, color }: { data: number[]; color: string }) {
  if (data.length < 2) return null;
  const w = 40, h = 14;
  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1;
  const points = data
    .map((v, i) => `${(i / (data.length - 1)) * w},${h - ((v - min) / range) * (h - 2) - 1}`)
    .join(" ");

  const lastX = w;
  const lastY = h - ((data[data.length - 1] - min) / range) * (h - 2) - 1;

  return (
    <svg width={w} height={h} style={{ flexShrink: 0 }}>
      <polyline points={points} fill="none" stroke={color} strokeWidth={1} opacity={0.5} />
      <circle cx={lastX} cy={lastY} r={1.5} fill={color} opacity={0.8} />
    </svg>
  );
}

// ── Ticker row — full readable name ────────────────────────────

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

  // Use cached full market name, or fallback to parsed label
  const fullName = marketNameCache.get(ticker);
  const label = fullName || parseTickerLabel(ticker, team, eventTicker);

  return (
    <button
      onClick={() => onSelect?.(ticker)}
      style={{
        display: "flex",
        alignItems: "center",
        width: "100%",
        padding: "4px 8px 4px 0",
        fontSize: "10px",
        textAlign: "left",
        cursor: "pointer",
        border: "none",
        transition: "background 0.1s",
        background: isSelected ? "rgba(255,102,0,0.07)" : "transparent",
        color: isSelected ? "#FF6600" : "#ccc",
        borderLeft: isSelected ? "2px solid #FF6600" : "2px solid transparent",
        position: "relative",
        overflow: "hidden",
        fontFamily: "inherit",
      }}
      onMouseEnter={(e) => {
        if (!isSelected) e.currentTarget.style.background = "rgba(255,255,255,0.018)";
      }}
      onMouseLeave={(e) => {
        if (!isSelected) e.currentTarget.style.background = "transparent";
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
      <div style={{ flex: 1, minWidth: 0, overflow: "hidden", paddingLeft: "6px" }}>
        {/* Line 1: Full market name + Price */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            lineHeight: "15px",
          }}
        >
          <span
            style={{
              fontWeight: isSelected ? 700 : 500,
              whiteSpace: "nowrap",
              overflow: "hidden",
              textOverflow: "ellipsis",
              fontSize: fullName ? "9.5px" : "10px",
              color: isSelected ? "#FF6600" : "#ddd",
              flex: 1,
              minWidth: 0,
            }}
            title={fullName || label}
          >
            {label}
          </span>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "2px",
              flexShrink: 0,
              marginLeft: "4px",
            }}
          >
            {mv !== null && mv !== 0 && (
              <span
                style={{
                  fontSize: "7px",
                  color: priceColor,
                  fontWeight: 700,
                  lineHeight: 1,
                }}
              >
                {mv > 0 ? "▲" : "▼"}
              </span>
            )}
            <span
              style={{
                fontWeight: 700,
                fontVariantNumeric: "tabular-nums",
                color: priceColor,
                fontSize: "10px",
              }}
            >
              {mid !== null ? `${mid}¢` : "—"}
            </span>
          </div>
        </div>

        {/* Line 2: Event name + spread + sparkline */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            lineHeight: "11px",
            marginTop: "1px",
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "0",
              fontSize: "8px",
              color: "#555",
              overflow: "hidden",
            }}
          >
            {eventName ? (
              <span
                style={{
                  whiteSpace: "nowrap",
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                  maxWidth: "80px",
                  color: "#3a3a3a",
                }}
              >
                {eventName}
              </span>
            ) : (
              <span
                style={{
                  whiteSpace: "nowrap",
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                  maxWidth: "55px",
                  color: "#2a2a2a",
                  textTransform: "uppercase",
                }}
              >
                {ticker.slice(-10)}
              </span>
            )}
            <span style={{ color: "#1e1e1e", margin: "0 3px" }}>·</span>
            <span
              style={{
                fontVariantNumeric: "tabular-nums",
                color: spread <= 2 ? "#555" : "#3a3a3a",
              }}
            >
              {spread}s
            </span>
            {kyle_lambda !== null && kyle_lambda !== undefined && (
              <>
                <span style={{ color: "#1e1e1e", margin: "0 3px" }}>·</span>
                <span
                  style={{ color: "#00BCD4", fontVariantNumeric: "tabular-nums" }}
                >
                  λ{kyle_lambda.toFixed(3)}
                </span>
              </>
            )}
          </div>
          <Sparkline data={priceHistory} color={priceColor} />
        </div>
      </div>
    </button>
  );
}
