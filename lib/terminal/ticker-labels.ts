// Kalshi ticker → human-readable label parser
// Maps team abbreviations, parses event types, extracts spread numbers.

const TEAMS: Record<string, string> = {
  // NBA
  LAL: "Lakers", LAC: "Clippers", GSW: "Warriors", SAC: "Kings",
  PHX: "Suns", DEN: "Nuggets", MIN: "Wolves", OKC: "Thunder",
  DAL: "Mavs", HOU: "Rockets", SAS: "Spurs", MEM: "Grizzlies",
  NOP: "Pelicans", POR: "Blazers", UTA: "Jazz",
  BOS: "Celtics", NYK: "Knicks", BKN: "Nets", PHI: "76ers",
  TOR: "Raptors", MIL: "Bucks", CLE: "Cavs", CHI: "Bulls",
  IND: "Pacers", DET: "Pistons", ATL: "Hawks", MIA: "Heat",
  ORL: "Magic", CHA: "Hornets", WAS: "Wizards",
  // NCAAB
  DUKE: "Duke", UNC: "UNC", AUB: "Auburn", FLA: "Florida",
  TENN: "Tennessee", ALA: "Alabama", CONN: "UConn", PUR: "Purdue",
  ILL: "Illinois", MICH: "Michigan", MSU: "Mich St",
  OSU: "Ohio St", NCST: "NC State", WIS: "Wisconsin",
  MARQ: "Marquette", BAY: "Baylor", ISU: "Iowa St",
  TXAM: "Texas A&M", ARK: "Arkansas", LSU: "LSU",
  USC: "USC", UCLA: "UCLA", ARIZ: "Arizona",
  GONZ: "Gonzaga", UK: "Kentucky", KU: "Kansas",
  VAN: "Vanderbilt", MISS: "Ole Miss", STAN: "Stanford",
  COLO: "Colorado", OREG: "Oregon", WASH: "Washington",
  UTAH: "Utah", ND: "Notre Dame", PROV: "Providence",
  NOVA: "Villanova", XAVI: "Xavier", BUTL: "Butler",
  CREI: "Creighton", GTWN: "Georgetown", WVU: "West Virginia",
  TCU: "TCU", OKST: "Oklahoma St", IOWA: "Iowa",
  NEB: "Nebraska", MINN: "Minnesota", RUTS: "Rutgers",
  PSU: "Penn St", NW: "Northwestern", MD: "Maryland",
  IU: "Indiana", PITT: "Pittsburgh",
  // NFL
  KC: "Chiefs", BUF: "Bills", BAL: "Ravens", CIN: "Bengals",
  PIT: "Steelers", NYJ: "Jets", NE: "Patriots",
  JAX: "Jaguars", TEN: "Titans", SF: "49ers", SEA: "Seahawks",
  LAR: "Rams", ARI: "Cardinals", GB: "Packers",
  NO: "Saints", TB: "Bucs", CAR: "Panthers",
  NYG: "Giants", LV: "Raiders",
  // NHL
  BOS2: "Bruins", NYR: "Rangers", NYI: "Islanders",
  FLR: "Panthers", TBL: "Lightning", OTT: "Senators",
  MTL: "Canadiens", WPG: "Jets", EDM: "Oilers",
  CGY: "Flames", VGK: "Knights", COL: "Avalanche",
  DAL2: "Stars", STL: "Blues", NSH: "Predators",
  CBJ: "Blue Jackets", PHL: "Flyers", WSH: "Capitals",
};

const CITIES: Record<string, string> = {
  CHI: "Chicago", OAK: "Oakland", JAC: "Jacksonville",
  NO: "New Orleans", LV: "Las Vegas", SA: "San Antonio",
  SEA: "Seattle", KC: "Kansas City", MIA: "Miami",
  BUF: "Buffalo", TEN: "Nashville", JAX: "Jacksonville",
  IND: "Indianapolis", CLE: "Cleveland", CIN: "Cincinnati",
  PIT: "Pittsburgh", MIN: "Minneapolis", MIL: "Milwaukee",
  DEN: "Denver", PHX: "Phoenix", POR: "Portland",
};

/**
 * Parse a Kalshi ticker into a human-readable display label.
 * Handles sports teams, relocation events, crypto, and more.
 */
export function parseTickerLabel(
  ticker: string,
  team: string,
  eventTicker: string,
): string {
  const cleanTicker = ticker.replace(/-[YN]$/, "");
  const evUp = (eventTicker || "").toUpperCase();

  // Extract team code and spread number (e.g., DUKE8 → DUKE, 8)
  const teamDigits = team.match(/^([A-Z]+)(\d+)$/i);
  const cleanTeam = teamDigits ? teamDigits[1].toUpperCase() : team.toUpperCase();
  const spreadNum = teamDigits ? teamDigits[2] : null;

  // ── Relocation events ──
  if (evUp.includes("RELOCATION")) {
    const cityMatch = evUp.match(/RELOCATION([A-Z]+)/);
    const cityCode = cityMatch ? cityMatch[1] : "";
    const cityName = CITIES[cityCode] || titleCase(cityCode);
    if (cleanTeam === "REMAIN" || cleanTeam === "STAY") return `${cityName} Stays`;
    const dest = TEAMS[cleanTeam] || CITIES[cleanTeam] || cleanTeam;
    return `${cityName} \u2192 ${dest}`;
  }

  // ── Crypto events ──
  if (/^KX(BTC|ETH|SOL|XRP|DOGE)/i.test(evUp)) {
    const coin = evUp.match(/^KX(BTC|ETH|SOL|XRP|DOGE)/i)?.[1] || "";
    const priceMatch = cleanTicker.match(/T(\d+)/);
    if (priceMatch) {
      return `${coin} >${Number(priceMatch[1]).toLocaleString()}`;
    }
    return `${coin} ${cleanTeam}`;
  }

  // ── Financial / index events ──
  if (/INXD|SP500|NASDAQ|DOW|TREASURY|FED/i.test(evUp)) {
    const resolved = TEAMS[cleanTeam] || cleanTeam;
    return spreadNum ? `${resolved} +${spreadNum}` : resolved;
  }

  // ── Sports (default path) ──
  const resolved = TEAMS[cleanTeam] || cleanTeam;
  return spreadNum ? `${resolved} +${spreadNum}` : resolved;
}

/**
 * Parse event ticker into a short event description for the chart header.
 */
export function parseEventName(eventTicker: string): string {
  const ev = (eventTicker || "").toUpperCase();

  // Relocation
  if (ev.includes("RELOCATION")) {
    const cityMatch = ev.match(/RELOCATION([A-Z]+)/);
    const cityCode = cityMatch ? cityMatch[1] : "";
    return `${CITIES[cityCode] || titleCase(cityCode)} Relocation`;
  }

  // Sports
  const sportMatch = ev.match(/^KX(NBA|NFL|NCAA[A-Z]*|NHL|MLB|WNBA|MLS|EPL)/i);
  if (sportMatch) {
    let sport = sportMatch[1].toUpperCase();
    if (sport.startsWith("NCAA")) sport = "NCAAB";
    let type = "";
    if (ev.includes("SPREAD")) type = " Spread";
    else if (ev.includes("TOTAL")) type = " Total";
    else if (ev.includes("1H")) type = " 1H";

    // Try to extract team pair from event ticker
    // Pattern after sport+date: e.g. KXNCAAMB1HSPREAD-26MAR02DUKENCST
    const afterSport = ev.replace(/^KX[A-Z0-9]+?-\d+[A-Z]*\d*-?/, "");
    if (afterSport.length >= 4) {
      const pair = tryExtractTeamPair(afterSport);
      if (pair) {
        const [t1, t2] = pair;
        const n1 = TEAMS[t1] || t1;
        const n2 = TEAMS[t2] || t2;
        return `${n1} vs ${n2}${type}`;
      }
    }
    return `${sport}${type}`;
  }

  // Crypto
  if (/^KX(BTC|ETH|SOL|XRP|DOGE)/i.test(ev)) {
    const coin = ev.match(/^KX(BTC|ETH|SOL|XRP|DOGE)/i)?.[1] || "";
    return `${coin} Price`;
  }

  // Fallback: clean up event ticker
  const cleaned = eventTicker
    .replace(/^KX/i, "")
    .replace(/-\d+[A-Z]*\d*$/i, "")
    .substring(0, 24);
  return titleCase(cleaned);
}

function titleCase(s: string): string {
  if (!s) return s;
  if (s.length <= 3) return s.toUpperCase();
  return s.charAt(0).toUpperCase() + s.slice(1).toLowerCase();
}

function tryExtractTeamPair(s: string): [string, string] | null {
  const codes = Object.keys(TEAMS);
  // Sort by length descending to match longer codes first
  codes.sort((a, b) => b.length - a.length);
  for (const c1 of codes) {
    if (s.startsWith(c1)) {
      const rest = s.slice(c1.length);
      if (!rest) continue;
      for (const c2 of codes) {
        if (rest === c2 || rest.startsWith(c2)) {
          return [c1, c2];
        }
      }
      // Unknown second team
      if (rest.length >= 2 && rest.length <= 6) {
        return [c1, rest];
      }
    }
  }
  return null;
}
