const ODDS_API_BASE = 'https://api.the-odds-api.com/v4';

export interface OddsApiGame {
  id: string;
  sport_key: string;
  sport_title: string;
  commence_time: string;
  home_team: string;
  away_team: string;
  bookmakers: OddsApiBookmaker[];
}

export interface OddsApiBookmaker {
  key: string;
  title: string;
  last_update: string;
  markets: OddsApiMarket[];
}

export interface OddsApiMarket {
  key: string;
  last_update: string;
  outcomes: OddsApiOutcome[];
}

export interface OddsApiOutcome {
  name: string;
  description?: string;
  price: number;
  point?: number;
}

export function createOddsApiClient(apiKey: string) {
  
  async function fetchOdds(
    sportKey: string,
    options: { 
      regions?: string; 
      markets?: string; 
      oddsFormat?: string 
    } = {}
  ): Promise<OddsApiGame[]> {
    const { 
      regions = 'us', 
      markets = 'h2h,spreads,totals', 
      oddsFormat = 'american' 
    } = options;

    const params = new URLSearchParams({
      apiKey,
      regions,
      markets,
      oddsFormat,
    });

    const url = `${ODDS_API_BASE}/sports/${sportKey}/odds?${params}`;
    const res = await fetch(url);

    if (!res.ok) {
      throw new Error(`Odds API error: ${res.status}`);
    }

    const remaining = res.headers.get('x-requests-remaining');
    // API usage tracked silently

    return res.json();
  }

  async function fetchEvents(sportKey: string): Promise<{ id: string; sport_key: string; commence_time: string; home_team: string; away_team: string }[]> {
    const url = `${ODDS_API_BASE}/sports/${sportKey}/events?apiKey=${apiKey}`;
    const res = await fetch(url);

    if (!res.ok) {
      throw new Error(`Odds API error: ${res.status}`);
    }

    return res.json();
  }

  async function fetchEventOdds(
    sportKey: string,
    eventId: string,
    options: { 
      regions?: string; 
      markets?: string; 
      oddsFormat?: string 
    } = {}
  ): Promise<OddsApiGame> {
    const { 
      regions = 'us', 
      markets = 'h2h,spreads,totals', 
      oddsFormat = 'american' 
    } = options;

    const params = new URLSearchParams({
      apiKey,
      regions,
      markets,
      oddsFormat,
    });

    const url = `${ODDS_API_BASE}/sports/${sportKey}/events/${eventId}/odds?${params}`;
    const res = await fetch(url);

    if (!res.ok) {
      throw new Error(`Odds API error: ${res.status}`);
    }

    const remaining = res.headers.get('x-requests-remaining');
    // API usage tracked silently

    return res.json();
  }

  async function fetchSports(): Promise<{ key: string; title: string; active: boolean }[]> {
    const url = `${ODDS_API_BASE}/sports?apiKey=${apiKey}`;
    const res = await fetch(url);

    if (!res.ok) {
      throw new Error(`Odds API error: ${res.status}`);
    }

    return res.json();
  }

  async function fetchScores(
    sportKey: string, 
    daysFrom: number = 1
  ): Promise<any[]> {
    const params = new URLSearchParams({
      apiKey,
      daysFrom: daysFrom.toString(),
    });

    const url = `${ODDS_API_BASE}/sports/${sportKey}/scores?${params}`;
    const res = await fetch(url);

    if (!res.ok) {
      throw new Error(`Odds API error: ${res.status}`);
    }

    return res.json();
  }

  return {
    fetchOdds,
    fetchEvents,
    fetchEventOdds,
    fetchSports,
    fetchScores,
  };
}