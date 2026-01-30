import { NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);

// Weather.gov API (no API key required, US only)
const WEATHER_GOV_BASE = 'https://api.weather.gov';

// Open-Meteo API (no API key required, global)
const OPEN_METEO_BASE = 'https://api.open-meteo.com/v1/forecast';

interface WeatherData {
  temperature_f: number;
  feels_like_f: number;
  wind_speed_mph: number;
  wind_gust_mph: number | null;
  wind_direction: string;
  wind_degrees: number;
  humidity_pct: number;
  precipitation_pct: number;
  conditions: string;
  weather_icon: string;
}

interface GameWithVenue {
  id: string;
  sport: string;
  venue_name?: string;
  venue_city?: string;
  venue_state?: string;
  venue_lat?: number;
  venue_lon?: number;
  start_time?: string;
  is_dome?: boolean;
}

// NFL Stadium coordinates (major outdoor venues)
const NFL_VENUES: Record<string, { lat: number; lon: number; dome: boolean; city: string; state: string }> = {
  'Arrowhead Stadium': { lat: 39.0489, lon: -94.4839, dome: false, city: 'Kansas City', state: 'MO' },
  'Lambeau Field': { lat: 44.5013, lon: -88.0622, dome: false, city: 'Green Bay', state: 'WI' },
  'Highmark Stadium': { lat: 42.7738, lon: -78.7870, dome: false, city: 'Orchard Park', state: 'NY' },
  'Soldier Field': { lat: 41.8623, lon: -87.6167, dome: false, city: 'Chicago', state: 'IL' },
  'FirstEnergy Stadium': { lat: 41.5061, lon: -81.6995, dome: false, city: 'Cleveland', state: 'OH' },
  'Empower Field': { lat: 39.7439, lon: -105.0201, dome: false, city: 'Denver', state: 'CO' },
  'Lumen Field': { lat: 47.5952, lon: -122.3316, dome: false, city: 'Seattle', state: 'WA' },
  'MetLife Stadium': { lat: 40.8128, lon: -74.0742, dome: false, city: 'East Rutherford', state: 'NJ' },
  'Lincoln Financial Field': { lat: 39.9008, lon: -75.1675, dome: false, city: 'Philadelphia', state: 'PA' },
  'M&T Bank Stadium': { lat: 39.2780, lon: -76.6227, dome: false, city: 'Baltimore', state: 'MD' },
  'Gillette Stadium': { lat: 42.0909, lon: -71.2643, dome: false, city: 'Foxborough', state: 'MA' },
  'Hard Rock Stadium': { lat: 25.9580, lon: -80.2389, dome: false, city: 'Miami Gardens', state: 'FL' },
  'Raymond James Stadium': { lat: 27.9759, lon: -82.5033, dome: false, city: 'Tampa', state: 'FL' },
  'Nissan Stadium': { lat: 36.1665, lon: -86.7713, dome: false, city: 'Nashville', state: 'TN' },
  'Levi\'s Stadium': { lat: 37.4033, lon: -121.9694, dome: false, city: 'Santa Clara', state: 'CA' },
  'SoFi Stadium': { lat: 33.9535, lon: -118.3392, dome: true, city: 'Inglewood', state: 'CA' },
  'Allegiant Stadium': { lat: 36.0909, lon: -115.1833, dome: true, city: 'Las Vegas', state: 'NV' },
  'AT&T Stadium': { lat: 32.7473, lon: -97.0945, dome: true, city: 'Arlington', state: 'TX' },
  'Mercedes-Benz Stadium': { lat: 33.7553, lon: -84.4006, dome: true, city: 'Atlanta', state: 'GA' },
  'U.S. Bank Stadium': { lat: 44.9736, lon: -93.2575, dome: true, city: 'Minneapolis', state: 'MN' },
  'Lucas Oil Stadium': { lat: 39.7601, lon: -86.1639, dome: true, city: 'Indianapolis', state: 'IN' },
  'Ford Field': { lat: 42.3400, lon: -83.0456, dome: true, city: 'Detroit', state: 'MI' },
  'Caesars Superdome': { lat: 29.9511, lon: -90.0812, dome: true, city: 'New Orleans', state: 'LA' },
  'State Farm Stadium': { lat: 33.5276, lon: -112.2626, dome: true, city: 'Glendale', state: 'AZ' },
};

// Wind direction degrees to cardinal
function degreesToCardinal(degrees: number): string {
  const directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'];
  const index = Math.round(degrees / 22.5) % 16;
  return directions[index];
}

// WMO weather codes to conditions
function wmoToConditions(code: number): { conditions: string; icon: string } {
  const mapping: Record<number, { conditions: string; icon: string }> = {
    0: { conditions: 'Clear', icon: '☀️' },
    1: { conditions: 'Mostly Clear', icon: '🌤️' },
    2: { conditions: 'Partly Cloudy', icon: '⛅' },
    3: { conditions: 'Overcast', icon: '☁️' },
    45: { conditions: 'Fog', icon: '🌫️' },
    48: { conditions: 'Freezing Fog', icon: '🌫️' },
    51: { conditions: 'Light Drizzle', icon: '🌧️' },
    53: { conditions: 'Drizzle', icon: '🌧️' },
    55: { conditions: 'Heavy Drizzle', icon: '🌧️' },
    61: { conditions: 'Light Rain', icon: '🌧️' },
    63: { conditions: 'Rain', icon: '🌧️' },
    65: { conditions: 'Heavy Rain', icon: '🌧️' },
    71: { conditions: 'Light Snow', icon: '🌨️' },
    73: { conditions: 'Snow', icon: '🌨️' },
    75: { conditions: 'Heavy Snow', icon: '🌨️' },
    77: { conditions: 'Snow Grains', icon: '🌨️' },
    80: { conditions: 'Light Showers', icon: '🌦️' },
    81: { conditions: 'Showers', icon: '🌦️' },
    82: { conditions: 'Heavy Showers', icon: '🌦️' },
    85: { conditions: 'Light Snow Showers', icon: '🌨️' },
    86: { conditions: 'Snow Showers', icon: '🌨️' },
    95: { conditions: 'Thunderstorm', icon: '⛈️' },
    96: { conditions: 'Thunderstorm with Hail', icon: '⛈️' },
    99: { conditions: 'Severe Thunderstorm', icon: '⛈️' },
  };
  return mapping[code] || { conditions: 'Unknown', icon: '❓' };
}

// Calculate weather impact score (0-100)
function calculateWeatherImpact(weather: WeatherData, sport: string): number {
  let impact = 0;

  // Temperature impact
  if (weather.temperature_f < 32) impact += 25; // Freezing
  else if (weather.temperature_f < 45) impact += 15;
  else if (weather.temperature_f > 95) impact += 20; // Very hot
  else if (weather.temperature_f > 85) impact += 10;

  // Wind impact (especially important for NFL, golf)
  if (weather.wind_speed_mph > 25) impact += 30;
  else if (weather.wind_speed_mph > 15) impact += 20;
  else if (weather.wind_speed_mph > 10) impact += 10;

  // Wind gusts
  if (weather.wind_gust_mph && weather.wind_gust_mph > 35) impact += 15;

  // Precipitation
  if (weather.precipitation_pct > 80) impact += 20;
  else if (weather.precipitation_pct > 50) impact += 10;

  // Conditions
  const severeConditions = ['Heavy Rain', 'Heavy Snow', 'Thunderstorm', 'Severe Thunderstorm', 'Snow'];
  if (severeConditions.includes(weather.conditions)) {
    impact += 20;
  }

  // Sport-specific adjustments
  if (sport === 'football' && weather.wind_speed_mph > 15) {
    impact += 10; // Wind affects passing game significantly
  }

  return Math.min(100, impact);
}

async function fetchOpenMeteoWeather(lat: number, lon: number, gameTime?: Date): Promise<WeatherData | null> {
  try {
    const params = new URLSearchParams({
      latitude: lat.toString(),
      longitude: lon.toString(),
      hourly: 'temperature_2m,relative_humidity_2m,precipitation_probability,weather_code,wind_speed_10m,wind_direction_10m,wind_gusts_10m,apparent_temperature',
      temperature_unit: 'fahrenheit',
      wind_speed_unit: 'mph',
      timezone: 'America/New_York',
      forecast_days: '3'
    });

    const response = await fetch(`${OPEN_METEO_BASE}?${params}`, {
      headers: { 'User-Agent': 'OMI-Edge/1.0' },
      next: { revalidate: 0 }
    });

    if (!response.ok) {
      console.error(`Open-Meteo API error: ${response.status}`);
      return null;
    }

    const data = await response.json();
    const hourly = data.hourly;

    if (!hourly || !hourly.time || hourly.time.length === 0) {
      return null;
    }

    // Find the closest hour to game time, or use current hour
    let hourIndex = 0;
    if (gameTime) {
      const gameHour = gameTime.toISOString().slice(0, 13) + ':00';
      hourIndex = hourly.time.findIndex((t: string) => t.startsWith(gameHour.slice(0, 13)));
      if (hourIndex === -1) hourIndex = 0;
    }

    const weatherCode = hourly.weather_code?.[hourIndex] || 0;
    const { conditions, icon } = wmoToConditions(weatherCode);
    const windDegrees = hourly.wind_direction_10m?.[hourIndex] || 0;

    return {
      temperature_f: hourly.temperature_2m?.[hourIndex] || 0,
      feels_like_f: hourly.apparent_temperature?.[hourIndex] || hourly.temperature_2m?.[hourIndex] || 0,
      wind_speed_mph: hourly.wind_speed_10m?.[hourIndex] || 0,
      wind_gust_mph: hourly.wind_gusts_10m?.[hourIndex] || null,
      wind_direction: degreesToCardinal(windDegrees),
      wind_degrees: windDegrees,
      humidity_pct: hourly.relative_humidity_2m?.[hourIndex] || 0,
      precipitation_pct: hourly.precipitation_probability?.[hourIndex] || 0,
      conditions,
      weather_icon: icon
    };
  } catch (error) {
    console.error('Open-Meteo fetch error:', error);
    return null;
  }
}

async function fetchUpcomingOutdoorGames(): Promise<GameWithVenue[]> {
  // Fetch upcoming games from odds_data that are outdoor sports
  const { data: games, error } = await supabase
    .from('odds_data')
    .select('id, sport, home_team, away_team, start_time')
    .in('sport', ['americanfootball_nfl', 'baseball_mlb', 'soccer_mls', 'soccer_epl'])
    .gte('start_time', new Date().toISOString())
    .lte('start_time', new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString())
    .order('start_time', { ascending: true })
    .limit(50);

  if (error) {
    console.error('Error fetching games:', error);
    return [];
  }

  // Map games to venues
  return (games || []).map(game => {
    // Try to find venue from home team
    const homeTeam = game.home_team || '';

    // Check if home team matches any NFL venue city
    for (const [venueName, venue] of Object.entries(NFL_VENUES)) {
      if (homeTeam.toLowerCase().includes(venue.city.toLowerCase()) ||
          venueName.toLowerCase().includes(homeTeam.toLowerCase().split(' ')[0])) {
        return {
          id: game.id,
          sport: game.sport,
          venue_name: venueName,
          venue_city: venue.city,
          venue_state: venue.state,
          venue_lat: venue.lat,
          venue_lon: venue.lon,
          start_time: game.start_time,
          is_dome: venue.dome
        };
      }
    }

    // Default to a central US location if venue unknown
    return {
      id: game.id,
      sport: game.sport,
      venue_name: 'Unknown',
      venue_city: 'Unknown',
      venue_state: 'Unknown',
      venue_lat: 39.8283, // Center of US
      venue_lon: -98.5795,
      start_time: game.start_time,
      is_dome: false
    };
  });
}

export async function GET() {
  console.log('Starting weather sync...');

  const games = await fetchUpcomingOutdoorGames();
  console.log(`Found ${games.length} upcoming outdoor games`);

  let synced = 0;
  let skipped = 0;
  let errors = 0;

  for (const game of games) {
    try {
      // Skip dome stadiums
      if (game.is_dome) {
        skipped++;
        continue;
      }

      // Skip if no coordinates
      if (!game.venue_lat || !game.venue_lon) {
        skipped++;
        continue;
      }

      const gameTime = game.start_time ? new Date(game.start_time) : undefined;
      const weather = await fetchOpenMeteoWeather(game.venue_lat, game.venue_lon, gameTime);

      if (!weather) {
        errors++;
        continue;
      }

      const sportKey = game.sport?.split('_')[0] || 'unknown';
      const weatherImpact = calculateWeatherImpact(weather, sportKey);

      const weatherRecord = {
        game_id: game.id,
        sport: game.sport,
        venue_name: game.venue_name,
        venue_city: game.venue_city,
        venue_state: game.venue_state,
        venue_lat: game.venue_lat,
        venue_lon: game.venue_lon,
        temperature_f: weather.temperature_f,
        feels_like_f: weather.feels_like_f,
        wind_speed_mph: weather.wind_speed_mph,
        wind_gust_mph: weather.wind_gust_mph,
        wind_direction: weather.wind_direction,
        wind_degrees: weather.wind_degrees,
        humidity_pct: weather.humidity_pct,
        precipitation_pct: weather.precipitation_pct,
        conditions: weather.conditions,
        weather_icon: weather.weather_icon,
        is_dome: game.is_dome || false,
        weather_impact_score: weatherImpact,
        fetched_at: new Date().toISOString(),
        game_time: game.start_time
      };

      const { error } = await supabase
        .from('game_weather')
        .upsert(weatherRecord, { onConflict: 'game_id' });

      if (error) {
        console.error(`Error upserting weather for game ${game.id}:`, error.message);
        errors++;
      } else {
        synced++;
      }

      // Small delay between API calls
      await new Promise(resolve => setTimeout(resolve, 200));
    } catch (error) {
      console.error(`Error processing game ${game.id}:`, error);
      errors++;
    }
  }

  console.log(`Weather sync complete: ${synced} synced, ${skipped} skipped (domes), ${errors} errors`);

  return NextResponse.json({
    success: true,
    timestamp: new Date().toISOString(),
    results: {
      total_games: games.length,
      synced,
      skipped,
      errors
    }
  });
}

export const dynamic = 'force-dynamic';
export const maxDuration = 60;
