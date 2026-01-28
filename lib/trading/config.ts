export const BOT_SERVER_URL =
  process.env.NEXT_PUBLIC_BOT_SERVER_URL || "http://localhost:8001";

export const WS_URL = BOT_SERVER_URL.replace("http", "ws") + "/ws";

export const COLORS = {
  emerald: "#10b981",
  red: "#ef4444",
  amber: "#f59e0b",
  cyan: "#06b6d4",
  violet: "#8b5cf6",
  blue: "#3b82f6",
  orange: "#f97316",
  slate: "#64748b",
} as const;

export const SPORT_COLORS: Record<string, string> = {
  MLB: COLORS.emerald,
  NBA: COLORS.orange,
  NFL: COLORS.blue,
  NHL: COLORS.cyan,
  SOCCER: COLORS.violet,
  MMA: COLORS.red,
  DEFAULT: COLORS.slate,
};

export const ROI_BUCKETS = [
  { range: "<0%", min: -Infinity, max: 0 },
  { range: "0-1%", min: 0, max: 1 },
  { range: "1-2%", min: 1, max: 2 },
  { range: "2-3%", min: 2, max: 3 },
  { range: "3-5%", min: 3, max: 5 },
  { range: "5-10%", min: 5, max: 10 },
  { range: "10%+", min: 10, max: Infinity },
] as const;
