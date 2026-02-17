/**
 * Enrich exchange_data rows that have null subtitles (Polymarket) by parsing event_title.
 * Reclassifies market types (O/U misclassified as moneyline → total).
 * Expands 2-way ML contracts ("Team A vs. Team B") into separate rows.
 */

type ExchangeRow = {
  exchange: string;
  market_type: string;
  yes_price: number | null;
  no_price: number | null;
  subtitle: string | null;
  event_title: string;
  mapped_game_id?: string;
  snapshot_time?: string;
  [key: string]: any;
};

export function enrichExchangeRows(
  rows: ExchangeRow[],
  gameTeamsMap?: Record<string, { home: string; away: string }>
): ExchangeRow[] {
  const expanded: ExchangeRow[] = [];

  for (const row of rows) {
    // Kalshi rows already have subtitles — pass through
    if (row.subtitle) {
      expanded.push(row);
      continue;
    }

    const title = row.event_title || '';

    // --- Skip: 1H (first half) markets ---
    if (/^1H /i.test(title) || /: 1H /i.test(title)) continue;

    // --- Skip: Player props ("Name: Stat O/U X.5", no "vs" in title) ---
    if (!title.includes(' vs') && title.includes('O/U')) continue;

    // --- Skip: Both Teams to Score ---
    if (/Both Teams to Score/i.test(title)) continue;

    // --- ML: "Will X win on DATE?" ---
    const willWin = title.match(/^Will (.+?) win on /i);
    if (willWin) {
      expanded.push({ ...row, subtitle: willWin[1].trim() });
      continue;
    }

    // --- ML: "X vs. Y end in a draw?" ---
    if (/end in a draw/i.test(title)) {
      expanded.push({ ...row, subtitle: 'Draw' });
      continue;
    }

    // --- Spread: "Spread: Team (-X.5)" ---
    const spreadMatch = title.match(/^Spread: (.+)/i);
    if (spreadMatch) {
      expanded.push({ ...row, subtitle: spreadMatch[1].trim(), market_type: 'spread' });
      continue;
    }

    // --- Total: "Team A vs. Team B: O/U X.5" ---
    const ouMatch = title.match(/^.+? vs\.? .+?: O\/U (\d+\.?\d*)/i);
    if (ouMatch) {
      expanded.push({ ...row, subtitle: `O/U ${ouMatch[1]}`, market_type: 'total' });
      continue;
    }

    // --- ML: "Team A vs. Team B" (plain, 2-way) ---
    const vsMatch = title.match(/^(.+?) vs\.? (.+?)$/i);
    if (vsMatch) {
      const firstTeam = vsMatch[1].trim();
      const secondTeam = vsMatch[2].trim();
      // First team = YES side, second team = NO side
      expanded.push({ ...row, subtitle: firstTeam });
      expanded.push({
        ...row,
        subtitle: secondTeam,
        yes_price: row.no_price,
        no_price: row.yes_price,
      });
      continue;
    }

    // Unrecognized format — skip
  }

  return expanded;
}
