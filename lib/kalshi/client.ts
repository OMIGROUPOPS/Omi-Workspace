// Kalshi API Client — typed wrappers for portfolio & trading endpoints
// Uses Node crypto RSA-PSS signing via auth.ts

import { signRequest } from "./auth";

const BASE_URL = "https://api.elections.kalshi.com";

// ── Generic fetch helper ────────────────────────────────────

async function kalshiFetch<T>(
  method: string,
  path: string,
  body?: unknown,
): Promise<T> {
  // path includes /trade-api/v2/...
  const headers = signRequest(method, path);
  const url = `${BASE_URL}${path}`;

  const opts: RequestInit = {
    method: method.toUpperCase(),
    headers: { ...headers },
    cache: "no-store",
  };
  if (body && (method === "POST" || method === "PUT" || method === "DELETE")) {
    opts.body = JSON.stringify(body);
  }

  const res = await fetch(url, opts);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Kalshi ${method} ${path} → ${res.status}: ${text}`);
  }

  // DELETE may return empty body
  const text = await res.text();
  if (!text) return {} as T;
  return JSON.parse(text) as T;
}

// ── Types ───────────────────────────────────────────────────

export interface KalshiBalance {
  balance: number; // cents
  portfolio_value: number;
  updated_ts: number;
}

export interface KalshiMarketPosition {
  ticker: string;
  position: number;
  position_fp: string;
  market_exposure: number;
  market_exposure_dollars: string;
  resting_orders_count: number;
  total_traded: number;
  total_traded_dollars: string;
  realized_pnl: number;
  realized_pnl_dollars: string;
  fees_paid: number;
  fees_paid_dollars: string;
  last_updated_ts: string;
}

export interface KalshiEventPosition {
  event_ticker: string;
  event_exposure: number;
  event_exposure_dollars: string;
  total_cost: number;
  total_cost_dollars: string;
  total_cost_shares: number;
  realized_pnl: number;
  realized_pnl_dollars: string;
  fees_paid: number;
  fees_paid_dollars: string;
}

export interface KalshiPositionsResponse {
  market_positions: KalshiMarketPosition[];
  event_positions: KalshiEventPosition[];
  cursor: string;
}

export interface KalshiFill {
  fill_id: string;
  trade_id: string;
  ticker: string;
  market_ticker: string;
  order_id: string;
  side: "yes" | "no";
  action: "buy" | "sell";
  count: number;
  count_fp: string;
  yes_price: number;
  yes_price_fixed: string;
  no_price: number;
  no_price_fixed: string;
  price: number;
  fee_cost: string;
  created_time: string;
  is_taker: boolean;
  ts: number;
}

export interface KalshiFillsResponse {
  fills: KalshiFill[];
  cursor: string;
}

export interface KalshiOrder {
  order_id: string;
  ticker: string;
  event_ticker: string;
  action: "buy" | "sell";
  side: "yes" | "no";
  type: "limit" | "market";
  status: "resting" | "canceled" | "executed" | "pending";
  yes_price: number;
  no_price: number;
  remaining_count: number;
  count: number;
  created_time: string;
  expiration_time?: string;
  queue_position?: number;
}

export interface KalshiOrdersResponse {
  orders: KalshiOrder[];
  cursor: string;
}

export interface KalshiCreateOrderRequest {
  ticker: string;
  action: "buy" | "sell";
  side: "yes" | "no";
  type: "limit" | "market";
  count: number;
  yes_price?: number;
  no_price?: number;
  expiration_time?: string;
  sell_position_floor?: number;
  buy_max_cost?: number;
}

export interface KalshiCreateOrderResponse {
  order: KalshiOrder;
}

// ── API methods ─────────────────────────────────────────────

export async function getBalance(): Promise<KalshiBalance> {
  return kalshiFetch<KalshiBalance>("GET", "/trade-api/v2/portfolio/balance");
}

export async function getPositions(
  limit = 100,
  settlementStatus: "unsettled" | "settled" | "all" = "unsettled",
): Promise<KalshiPositionsResponse> {
  const params = new URLSearchParams({
    limit: limit.toString(),
    settlement_status: settlementStatus,
  });
  return kalshiFetch<KalshiPositionsResponse>(
    "GET",
    `/trade-api/v2/portfolio/positions?${params.toString()}`,
  );
}

export async function getFills(limit = 20): Promise<KalshiFillsResponse> {
  const params = new URLSearchParams({ limit: limit.toString() });
  return kalshiFetch<KalshiFillsResponse>(
    "GET",
    `/trade-api/v2/portfolio/fills?${params.toString()}`,
  );
}

export async function getOrders(
  status?: "resting" | "canceled" | "executed" | "pending",
  limit = 50,
): Promise<KalshiOrdersResponse> {
  const params = new URLSearchParams({ limit: limit.toString() });
  if (status) params.set("status", status);
  return kalshiFetch<KalshiOrdersResponse>(
    "GET",
    `/trade-api/v2/portfolio/orders?${params.toString()}`,
  );
}

export async function createOrder(
  order: KalshiCreateOrderRequest,
): Promise<KalshiCreateOrderResponse> {
  return kalshiFetch<KalshiCreateOrderResponse>(
    "POST",
    "/trade-api/v2/portfolio/orders",
    order,
  );
}

export async function cancelOrder(orderId: string): Promise<void> {
  await kalshiFetch<unknown>(
    "DELETE",
    `/trade-api/v2/portfolio/orders/${orderId}`,
  );
}
