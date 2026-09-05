// Selection and decoding only; prices, clocks, metrics and text are builder output.
export const SILENT = "STORE SILENT";
export type LegDisplay = {
  current_rest: number | null;
  rest_known: boolean;
  rest_label: string;
  member_count: number | null;
  member_label: string;
  member_percent: number | null;
  sentence: string;
  belief: string;
  authors: string;
  family: string | null;
  band_line: string;
  band: [number, number] | null;
  q10: number | null;
  action: string | null;
  lane: string | null;
  hand_line: string;
  saw: string;
};
export type Receipt = {
  index: number;
  t: number;
  minutesToBell: number;
  clock_label: string;
  title: string;
  kind: string;
  receipt: string | null;
  receipt_id: string | null;
  detail_url: string | null;
  legs: Record<
    string,
    { rest?: { cents: number; lane: string | null } | null; fill?: { cents: number } | null }
  >;
  display: {
    legs: Record<string, LegDisplay>;
    pair_sum: number | null;
    pair_label: string;
    pair_percent: number | null;
    above_par: boolean | null;
    fills: string;
  };
};
export type Bench = {
  minutes_to_bell: number;
  status: string | null;
  validity: {
    status: string | null;
    share: number | null;
    ess: number | null;
    label: string;
    meter_percent: number | null;
  };
  roles: Record<string, string | null>;
  rules: Record<
    string,
    {
      ess: number | null;
      label: string;
      status: string | null;
      sides: Record<string, { status: string | null; ess: number | null; family: string | null }>;
    }
  >;
};
export type Checkpoint = {
  minutesToBell: number;
  label: string;
  playable: boolean;
  position_percent: number | null;
  frame: number;
  receipt_index: number | null;
  bench: Bench | null;
};
export type Frame = {
  hover_lines: string[];
  minutesToBell: number;
  hours: number;
  clock_label: string;
  receipt_index: number | null;
  checkpoint_index: number;
  pre_first_tick: boolean;
  plot_remaining: number;
  plot_progress: number;
  firstLast: number | null;
  firstBid: number | null;
  firstAsk: number | null;
  firstRest: number | null;
  secondLast: number | null;
  secondBid: number | null;
  secondAsk: number | null;
  secondRest: number | null;
  firstBand: [number, number] | null;
  firstQ10: number | null;
  secondBand: [number, number] | null;
  secondQ10: number | null;
};
export type BidAction = {
  id: string;
  leg: string;
  kind: string;
  glyph: string;
  stack_offset_px: number;
  label: string;
  receipt_index: number;
  hover_lines: string[];
  markers: Record<
    string,
    {
      display_progress: number;
      boundary: string | null;
      price: number | null;
      label: string;
    }
  >;
  fill?: {
    summary: string;
    floor_line: string;
    placing_sentence_lines: string[];
  };
};
export type FaceData = {
  version: number;
  legs: string[];
  category: string | null;
  truth?: {
    role: string;
    table_commit: string;
    row_sha256: string | null;
    status: string;
    reason: string | null;
    legs: Record<
      string,
      {
        status: string;
        reason: string | null;
        line: string;
        floor_cents: number | null;
        minutes_to_bell: number | null;
        marker_label: string | null;
        chart_label: string | null;
        markers: Record<
          string,
          {
            progress: number;
            display_progress: number;
            boundary: string | null;
            glyph: string;
            label: string;
            price: number | null;
          }
        >;
      }
    >;
    pair: { line: string; discount_line: string; compact_line: string };
  };
  provenance: Record<string, string | null>;
  bell: { t: number; timestamp_epoch: number; source: string | null };
  first_tick: { epoch: number; mtb_first: number; source: string; clock_label: string };
  bench: {
    present: boolean;
    label: string | null;
    clock_status: string;
    clock_delta_seconds: number | null;
  };
  os: Receipt[];
  render: {
    bid_actions: BidAction[];
    columns: string[];
    ticks: unknown[][];
    total_frames: number;
    receipt_count: number;
    play_start_frame: number;
    checkpoints: Checkpoint[];
    axis: {
      start_minutes_to_bell: number;
      end_minutes_to_bell: number;
      ticks: number[];
      price_domain: [number, number] | null;
      price_ticks: number[];
    };
    inspection_axis: {
      start_minutes_to_bell: number;
      end_minutes_to_bell: number;
      ticks: number[];
      price_domain: [number, number] | null;
      price_ticks: number[];
    };
    fill_events: {
      leg: string;
      minutesToBell: number;
      cents: number;
      label: string;
      receipt_index: number;
      plot_progress: number;
      inspection_progress: number;
      plot_price: number | null;
      inspection_price: number | null;
    }[];
    misses: { leg: string; cents: number; never_returned: boolean | null; label: string }[];
    verification: Record<string, unknown>;
  };
};
export type Game = {
  event: string;
  category: string | null;
  os_sha: string | null;
  trace_sha: string | null;
  url: string;
  version: number;
};
export type LoadedGame = { face: FaceData; frames: Frame[] };
async function json<T>(url: string, signal?: AbortSignal): Promise<T> {
  const response = await fetch(url, { signal, cache: "no-cache" });
  if (!response.ok) throw new Error(`${url}: HTTP ${response.status}`);
  return response.json();
}
export const loadGameIndex = (signal?: AbortSignal) =>
  json<{ games: Game[] }>("/data/index.json", signal);
export async function loadTuneGame(url: string, signal?: AbortSignal): Promise<LoadedGame> {
  const face = await json<FaceData>(url, signal);
  const dictionary = (face as FaceData & { dictionary?: unknown[] }).dictionary;
  if (dictionary) {
    const decode = (v: unknown): unknown =>
      v && typeof v === "object"
        ? "$ref" in v
          ? dictionary[(v as { $ref: number }).$ref]
          : Array.isArray(v)
            ? v.map(decode)
            : Object.fromEntries(Object.entries(v).map(([k, x]) => [k, decode(x)]))
        : v;
    face.os = face.os.map((r) => decode(r) as Receipt);
  }
  if (
    face.version !== 2 ||
    !face.render?.ticks?.length ||
    !face.render.columns.includes("plot_remaining")
  )
    throw new Error("This game needs rerun_game.ps1 to produce FACE v2 data");
  const frames = face.render.ticks.map(
    (row) =>
      Object.fromEntries(
        face.render.columns.map((key, index) => [key, row[index]]),
      ) as unknown as Frame,
  );
  return { face, frames };
}
export const loadReceipt = (url: string, signal?: AbortSignal) =>
  json<{ source: unknown; inspector: unknown; row: unknown }>(url, signal);
export function frameForReceipt(frames: Frame[], receipt: Receipt): number {
  const exact = frames.findIndex((f) => f.receipt_index === receipt.index);
  if (exact >= 0) return exact;
  const index = frames.findIndex((f) => f.minutesToBell <= receipt.minutesToBell);
  return index < 0 ? frames.length - 1 : index;
}
