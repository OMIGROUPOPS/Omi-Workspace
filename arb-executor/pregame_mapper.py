#!/usr/bin/env python3
"""
pregame_mapper.py — Pre-Game Market Mapping Agent
==================================================

Runs before trading hours to build a verified lookup table mapping
every game between Kalshi and Polymarket US. Resolves:
  - Kalshi tickers ↔ PM slugs
  - PM outcome indices (which outcome_index = which team)
  - PM token IDs for direct orderbook access
  - Human-readable outcome names for verification

The executor loads this file at startup and skips ALL runtime
market discovery, slug parsing, and outcome index inference.

Usage:
  # Full afternoon sweep (run at ~3pm ET)
  python pregame_mapper.py

  # Rolling check for new listings (run every 15-30 min)
  python pregame_mapper.py --incremental

  # Verify a single game
  python pregame_mapper.py --verify "nba:DEN-NYK:2026-02-05"

  # Dry run (don't write file, just print what would be mapped)
  python pregame_mapper.py --dry-run

Output:
  verified_mappings.json — consumed by arb_executor_v7.py
"""

import argparse
import asyncio
import hashlib
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Dependencies
# ---------------------------------------------------------------------------
try:
    import aiohttp
except ImportError:
    print("ERROR: aiohttp required. Install with: pip install aiohttp")
    sys.exit(1)

# Import API signing from executor for authenticated endpoints
try:
    from arb_executor_v7 import (
        KalshiAPI, KALSHI_API_KEY, KALSHI_PRIVATE_KEY,
        PolymarketUSAPI, PM_US_API_KEY, PM_US_SECRET_KEY,
        CANONICAL_ABBREV, normalize_team_abbrev,
    )
    HAS_EXECUTOR = True
except ImportError:
    HAS_EXECUTOR = False
    print("WARNING: Could not import from arb_executor_v7.py - API auth unavailable")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
MAPPING_FILE = "verified_mappings.json"
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, f"mapper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

# API endpoints
KALSHI_BASE = "https://api.elections.kalshi.com"
PM_US_BASE = "https://api.polymarket.us"

# Kalshi series tickers by sport
SPORTS_CONFIG = [
    {
        "sport": "nba",
        "series": "KXNBAGAME",
        "display": "NBA",
    },
    {
        "sport": "nhl",
        "series": "KXNHLGAME",
        "display": "NHL",
    },
    {
        "sport": "cbb",
        "series": "KXNCAAMBGAME",
        "display": "CBB",
    },
    {
        "sport": "ufc",
        "series": "KXUFCFIGHT",
        "display": "UFC",
    },
]

# ---------------------------------------------------------------------------
# Team Abbreviation Mapping
# Canonical: Kalshi abbreviation -> PM slug abbreviation
# This is the SINGLE SOURCE OF TRUTH for cross-platform team identity.
# ---------------------------------------------------------------------------
# fmt: off
KALSHI_TO_PM_ABBREV = {
    # --- NBA ---
    "ATL": "atl", "BOS": "bos", "BKN": "bkn", "CHA": "cha",
    "CHI": "chi", "CLE": "cle", "DAL": "dal", "DEN": "den",
    "DET": "det", "GSW": "gs",  "HOU": "hou", "IND": "ind",
    "LAC": "lac", "LAL": "lal", "MEM": "mem", "MIA": "mia",
    "MIL": "mil", "MIN": "min", "NOP": "no",  "NYK": "ny",
    "OKC": "okc", "ORL": "orl", "PHI": "phi", "PHX": "phx",
    "POR": "por", "SAC": "sac", "SAS": "sa",  "TOR": "tor",
    "UTA": "uta", "WAS": "wsh",
    # --- NHL ---
    "ANA": "ana", "ARI": "ari", "BUF": "buf", "CAR": "car",
    "CBJ": "cbj", "CGY": "cgy", "COL": "col", "DAL": "dal",
    "EDM": "edm", "FLA": "fla", "LAK": "lak", "MIN": "min",
    "MTL": "mtl", "NJD": "njd", "NSH": "nas", "NYI": "nyi",
    "NYR": "nyr", "OTT": "ott", "PHI": "phi", "PIT": "pit",
    "SEA": "sea", "SJS": "sjs", "STL": "stl", "TBL": "tbl",
    "TOR": "tor", "UTA": "uta", "VAN": "van", "VGK": "vgk",
    "WPG": "wpg", "WSH": "was",
    # --- CBB (partial, extend as needed) ---
    # NOTE: Use Kalshi's actual abbreviations (check ticker format)
    "DUKE": "duke", "UNC": "unc", "KU": "kan", "UK": "ken",
    "GONZ": "gonz", "HOU": "hou", "PURDUE": "pur", "TENN": "ten",
    "AUBURN": "aub", "IOWA": "iowa", "BAY": "bay",  # Kalshi uses BAY, not BAYLOR
    "CONN": "conn", "ARIZ": "ariz", "CREI": "crei",
    "MARQ": "marq", "ISU": "isu", "MONT": "mont",  # Montana
}

# Reverse mapping: PM slug abbreviation -> Kalshi abbreviation
PM_TO_KALSHI_ABBREV = {}
for k_abbr, pm_abbr in KALSHI_TO_PM_ABBREV.items():
    PM_TO_KALSHI_ABBREV[pm_abbr] = k_abbr

# Additional CBB abbreviation mappings: PM slug -> Kalshi ticker
# This handles the many CBB teams with different abbreviation conventions
CBB_PM_TO_KALSHI = {
    # PM uses longer names, Kalshi uses shorter
    "baylor": "BAY",     # Baylor (displayAbbrev uses full name)
    "lr": "UALR",        # Arkansas Little Rock (PM uses LR)
    "mont": "MONT",      # Montana (distinguish from MEM Memphis)
    "web": "WEB",        # Weber State
    "nw": "NW",          # Northwestern
    "albny": "ALBY",     # Albany
    "bryant": "BRY",     # Bryant
    "brown": "BRWN",     # Brown
    "drexel": "DREX",    # Drexel
    "bradly": "BRAD",    # Bradley
    "niowa": "UNI",      # Northern Iowa
    "bella": "BELL",     # Bellarmine
    "stetsn": "STET",    # Stetson
    "belm": "BEL",       # Belmont
    "illchi": "LCHI",    # Loyola Chicago (Illinois)
    "loych": "LCHI",     # Loyola Chicago variant
    "david": "DAV",      # Davidson
    "cans": "CAN",       # Canisius
    "wvir": "WVU",       # West Virginia
    "samf": "SAM",       # Samford
    "drake": "DRKE",     # Drake
    "illst": "ILST",     # Illinois State
    "ndkst": "NDSU",     # North Dakota State
    "cencon": "CCSU",    # Central Connecticut State
    "chist": "CHS",      # Chicago State
    "char": "COFC",      # Charleston (College of Charleston)
    "merc": "MER",       # Mercer
    "flgc": "FGCU",      # Florida Gulf Coast
    "ekent": "EKY",      # Eastern Kentucky
    "hofst": "HOF",      # Hofstra
    "neast": "NE",       # Northeastern
    "nhvn": "NHC",       # New Haven
    "liub": "LIU",       # LIU Brooklyn
    "manh": "MAN",       # Manhattan
    "stpete": "SPC",     # Saint Peter's
    "siena": "SIE",      # Siena
    "arlr": "UALR",      # Arkansas Little Rock
    "linw": "LINW",      # Lindenwood (same)
    "maine": "ME",       # Maine
    "verm": "UVM",       # Vermont
    "tentch": "TNTC",    # Tennessee Tech
    "will": "WIU",       # Western Illinois
    "tmrt": "UTM",       # UT Martin
    "uscb": "UCSB",      # UC Santa Barbara
    "ucdv": "UCD",       # UC Davis
    "ucirv": "UCI",      # UC Irvine
    "csunr": "CSN",      # Cal State Northridge
    "csufl": "CSF",      # Cal State Fullerton
    "ucrvs": "UCRV",     # UC Riverside
    "fairdk": "FDU",     # Fairleigh Dickinson (FDU not FAIR)
    "jac": "JVST",       # Jacksonville State
    "abchr": "AC",       # Abilene Christian
    "utahv": "UVU",      # Utah Valley
    "syra": "SYR",       # Syracuse (Kalshi ticker uses SYR)
    "uconn": "CONN",     # UConn
    "stjohn": "SJU",     # St. John's
    "woff": "WOF",       # Wofford
    "wcar": "WCU",       # Western Carolina
    # More PM -> Kalshi mappings
    "ncatst": "NCAT",    # NC A&T
    "aubrn": "AUB",      # Auburn
    "mspst": "MSST",     # Mississippi State
    "bowlgr": "BGSU",    # Bowling Green
    "arkst": "ARST",     # Arkansas State
    "lafay": "LAF",      # Lafayette
    "okst": "OKST",      # Oklahoma State
    "arz": "ARIZ",       # Arizona
    "ballst": "BALL",    # Ball State
    "lamon": "LAM",      # Lamar
    "bayl": "BAY",       # Baylor
    "iowast": "ISU",     # Iowa State
    "ala": "ALA",        # Alabama
    "emich": "EMU",      # Eastern Michigan
    "applst": "APP",     # Appalachian State
    "ark": "ARK",        # Arkansas
    "siue": "SIUE",      # SIU Edwardsville (same)
    "clvst": "CLEV",     # Cleveland State
    "iupui": "IUPU",     # IUPUI
    "cmich": "CMU",      # Central Michigan
    "loulaf": "ULL",     # Louisiana Lafayette
    "umass": "MASS",     # UMass
    "coast": "CCU",      # Coastal Carolina
    "cornel": "COR",     # Cornell
    "colmb": "CLMB",     # Columbia
    "prnce": "PRIN",     # Princeton (Kalshi uses PRIN, not PRINCE)
    "rich": "RICH",      # Richmond (same)
    "ri": "URI",         # Rhode Island
    "geows": "GW",       # George Washington
    "mtnst": "MTU",      # Middle Tennessee State
    "del": "DEL",        # Delaware (same)
    "ndak": "UND",       # North Dakota
    "depaul": "DEP",     # DePaul
    "prov": "PROV",      # Providence (same)
    "gb": "UWGB",        # Green Bay (UW Green Bay)
    "purdue": "PUR",     # Purdue
    "ore": "ORE",        # Oregon (same)
    "smu": "SMU",        # SMU (same)
    "pitt": "PITT",      # Pittsburgh (same)
    # --- Additional CBB mappings (round 2) ---
    "cabap": "CBU",      # California Baptist
    "cita": "CIT",       # The Citadel
    "calpol": "CP",      # Cal Poly
    "eill": "EIU",       # Eastern Illinois
    "tenst": "TNST",     # Tennessee State
    "evans": "EVAN",     # Evansville
    "ewash": "EWU",      # Eastern Washington
    "idaho": "IDHO",     # Idaho
    "monst": "MTST",     # Montana State (slug version)
    "idhst": "IDST",     # Idaho State
    "narz": "NAU",       # Northern Arizona
    "jax": "JAC",        # Jacksonville (not Jacksonville State)
    "queen": "QUC",      # Queens
    "jaxst": "JVST",     # Jacksonville State
    "wkent": "WKU",      # Western Kentucky
    "lbst": "LBSU",      # Long Beach State
    "lemyn": "LMC",      # Le Moyne
    "maslow": "MASSL",   # UMass Lowell
    "mary": "MD",        # Maryland
    "ohiost": "OSU",     # Ohio State
    "mphs": "MEM",       # Memphis
    "mhst": "MORE",      # Morehead State
    "semst": "SEMO",     # SE Missouri State
    "merri": "MRMK",     # Merrimack
    "mstm": "MSM",       # Mount St. Mary's
    "marist": "MRST",    # Marist
    "rider": "RID",      # Rider
    "murst": "MURR",     # Murray State
    "sill": "SIU",       # Southern Illinois
    "ncol": "UNCO",      # Northern Colorado
    "webst": "WEB",      # Weber State
    "ncw": "UNCW",       # UNC Wilmington
    "nfl": "UNF",        # North Florida
    "uwg": "UWGA",       # West Georgia
    "tarl": "TARL",      # Tarleton State
    "stnh": "STNH",      # Stonehill (also used in slug)
    # --- Added 2026-02-08 to fix unmatched games ---
    "alaam": "AAMU",     # Alabama A&M
    "grmbst": "GRAM",    # Grambling State
    "alast": "ALST",     # Alabama State
    "south": "SOU",      # Southern University
    "alcst": "ALCN",     # Alcorn State
    "msvlst": "MVSU",    # Mississippi Valley State
    "jackst": "JKST",    # Jackson State
    "bcook": "COOK",     # Bethune-Cookman
    "txs": "TXSO",       # Texas Southern
    "nal": "UNA",        # North Alabama
    "charlt": "CHAR",    # Charlotte
    "delst": "DSU",      # Delaware State
    "ncc": "NCCU",       # NC Central
    "flam": "FAMU",      # Florida A&M
    "pvam": "PV",        # Prairie View A&M
    "ncg": "UNCG",       # UNC Greensboro
    "furman": "FUR",     # Furman
    "houbap": "HCU",     # Houston Christian (Houston Baptist)
    "mcnst": "MCNS",     # McNeese State
    "howrd": "HOW",      # Howard
    "incar": "IW",       # Incarnate Word
    "selou": "SELA",     # SE Louisiana
    "indst": "INST",     # Indiana State
    "lamar": "LAM",      # Lamar
    "minnst": "MINN",    # Minnesota
    "nichls": "NICH",    # Nicholls State
    "sfaus": "SFA",      # Stephen F. Austin
    "txamc": "ETAM",     # Texas A&M Commerce (East Texas A&M)
    "stfpa": "SFPA",     # St. Francis PA
    "amcc": "AMCC",      # Texas A&M Corpus Christi
    "uno": "UNO",        # New Orleans
    # --- Additional fixes 2026-02-08 ---
    "tulsa": "TLSA",     # Tulsa
    "sfl": "USF",        # South Florida (USF)
    "wichst": "WICH",    # Wichita State
    "tulane": "TULN",    # Tulane
    "txtech": "TTU",     # Texas Tech
    "chist": "CHS",      # Chicago State
    # --- Comprehensive CBB match-rate fix (2026-02-13) ---
    # Fixes ~80 PM→Kalshi abbreviation mismatches found via --debug-keys
    "airf": "AFA",       # Air Force
    "frest": "FRES",     # Fresno State
    "akron": "AKR",      # Akron
    "sc": "SCAR",        # South Carolina
    "amercn": "AMER",    # American University
    "jmad": "JMU",       # James Madison
    "ausp": "PEAY",      # Austin Peay
    "toledo": "TOL",     # Toledo
    "boise": "BSU",      # Boise State
    "boscol": "BC",      # Boston College
    "bostu": "BU",       # Boston University
    "sacred": "SHU",     # Sacred Heart
    "dxst": "UTU",       # Dixie State / Utah Tech
    "chsou": "CHSO",     # Charleston Southern
    "radf": "RAD",       # Radford
    "clmsn": "CLEM",     # Clemson
    "nill": "NIU",       # Northern Illinois
    "george": "GTWN",    # Georgetown
    "coppst": "COPP",    # Coppin State
    "creigh": "CREI",    # Creighton
    "hawaii": "HAW",     # Hawaii
    "colst": "CSU",      # Colorado State
    "wyom": "WYO",       # Wyoming
    "msrst": "MOSU",     # Missouri State
    "norfst": "NORF",    # Norfolk State
    "stbon": "SBON",     # St. Bonaventure
    "ecar": "ECU",       # East Carolina
    "wmich": "WMU",      # Western Michigan
    "etnst": "ETSU",     # East Tennessee State
    "flint": "FIU",      # Florida International
    "loutch": "LT",      # Louisiana Tech
    "fl": "FLA",         # Florida
    "fordm": "FOR",      # Fordham
    "flst": "FSU",       # Florida State
    "vtech": "VT",       # Virginia Tech
    "vamil": "VMI",      # VMI
    "gas": "GASO",       # Georgia Southern
    "marsh": "MRSH",     # Marshall
    "old": "ODU",        # Old Dominion
    "gcan": "GC",        # Grand Canyon
    "sjst": "SJSU",      # San Jose State
    "gmsn": "GMU",       # George Mason
    "gnzg": "GONZ",      # Gonzaga
    "sanclr": "SCU",     # Santa Clara
    "gtech": "GT",       # Georgia Tech
    "harvrd": "HARV",    # Harvard
    "kanst": "KSU",      # Kansas State
    "mdes": "UMES",      # Maryland Eastern Shore
    "hpnt": "HP",        # High Point
    "gardwb": "WEBB",    # Gardner-Webb
    "nmxst": "NMSU",     # New Mexico State
    "smho": "SHSU",      # Sam Houston State
    "kenest": "KENN",    # Kennesaw State
    "lehi": "LEH",       # Lehigh
    "librty": "LIB",     # Liberty
    "lipsc": "LIP",      # Lipscomb
    "longwd": "LONG",    # Longwood
    "scup": "SCUS",      # SC Upstate
    "loymry": "LMU",     # Loyola Marymount
    "niagra": "NIAG",    # Niagara
    "utahst": "USU",     # Utah State
    "miaoh": "MOH",      # Miami Ohio
    "missr": "MIZ",      # Missouri
    "tx": "TEX",         # Texas
    "morgst": "MORG",    # Morgan State
    "scarst": "SCST",    # SC State
    "sacst": "SAC",      # Sacramento State
    "ncashe": "UNCA",    # UNC Asheville
    "presb": "PRE",      # Presbyterian
    "nevada": "NEV",     # Nevada
    "sdst": "SDSU",      # San Diego State
    "nhamp": "UNH",      # New Hampshire
    "oral": "ORU",       # Oral Roberts
    "sdkst": "SDST",     # South Dakota State
    "vir": "UVA",        # Virginia
    "stmry": "SMC",      # Saint Mary's
    "pacfc": "PAC",      # Pacific
    "portst": "PRST",    # Portland State
    "tamu": "TXAM",      # Texas A&M (main campus, not Corpus Christi)
    "soumis": "USM",     # Southern Miss
    "stmn": "UST",       # St. Thomas Minnesota
    "sutah": "SUU",      # Southern Utah
    "txa": "UTA",        # UT Arlington
    "mst": "MSU",        # Michigan State
    "wisc": "WIS",       # Wisconsin
    "ga": "UGA",         # Georgia
    "okl": "OU",         # Oklahoma
    "stlou": "SLU",      # Saint Louis
    "flatl": "FAU",      # Florida Atlantic
    "seton": "HALL",     # Seton Hall
    "butl": "BUTL",      # Butler
    "rutger": "RUTG",    # Rutgers
    "det": "DET",        # Detroit Mercy
    "yngst": "YSU",      # Youngstown State
    "robms": "RMU",      # Robert Morris
    "oak": "OAK",        # Oakland
    "valp": "VALP",      # Valparaiso
    "ntx": "NTX",        # North Texas
    "templ": "TMPL",     # Temple
    "sf": "USF",         # San Francisco
    "sd": "USD",         # San Diego
    "pur": "PUR",        # Purdue (override PM_TO_KALSHI reverse mapping)
    "aub": "AUB",        # Auburn (override PM_TO_KALSHI reverse mapping)
    "monst": "MTST",     # Montana State (distinct from mtnst=Middle Tennessee)
    "sala": "USA",       # South Alabama
    "cah": "CAL",        # California (Cal)
    "col": "COLO",       # Colorado (CBB; NHL uses COL for Avalanche)
    # "no" → UNO handled in SPORT_PM_OVERRIDES to avoid clobbering NBA NOP
    "mrcy": "MHU",       # Mount Saint Mary's (Mercy variant)
    "kentst": "KENT",    # Kent State
    "wrght": "WRST",     # Wright State
    "quin": "QUIN",      # Quinnipiac (same)
    "utah": "UTAH",      # Utah (same)
    "utsa": "UTSA",      # UT San Antonio (same)
    "camp": "CAMP",      # Campbell (same)
    "uab": "UAB",        # UAB (same)
    "neom": "NEOM",      # Nebraska Omaha (same)
    "den": "DEN",        # Denver (same)
}

# Merge CBB mappings into PM_TO_KALSHI_ABBREV
PM_TO_KALSHI_ABBREV.update(CBB_PM_TO_KALSHI)

# Additional mappings for PM displayAbbreviation (different from slug abbrevs!)
# These are the team abbreviations PM shows in marketSides.team.displayAbbreviation
# which often differ from the slug abbreviations
# NOTE: Keys must be LOWERCASE since lookup uses abbrev.lower()
PM_DISPLAY_ABBREV_TO_KALSHI = {
    # displayAbbreviation -> Kalshi ticker (all keys lowercase!)
    # --- NBA abbreviation fixes ---
    "was": "WSH",      # Washington Wizards (PM uses WAS, Kalshi uses WSH)
    "pho": "PHX",      # Phoenix Suns (PM sometimes uses PHO)
    "gs": "GSW",       # Golden State (PM slug uses gs, display uses GSW)
    "sa": "SAS",       # San Antonio (PM slug uses sa)
    "no": "NOP",       # New Orleans (PM slug uses no)
    "ny": "NYK",       # New York Knicks (PM slug uses ny)
    # --- CBB displayAbbreviation mappings ---
    "acu": "AC",       # Abilene Christian
    "ucr": "UCRV",     # UC Riverside
    "csuf": "CSF",     # Cal State Fullerton
    "luc": "LCHI",     # Loyola Chicago
    "hu": "HOF",       # Hofstra
    "neu": "NE",       # Northeastern
    "spu": "SPC",      # Saint Peter's
    "oma": "NEOM",     # Nebraska Omaha
    "unh": "UNH",      # New Hampshire (NOT New Haven NHC - nhvn slug handles NHC)
    "csun": "CSN",     # Cal State Northridge
    "ue": "EVAN",      # Evansville
    "sto": "STNH",     # Stonehill
    "lem": "LMC",      # Le Moyne
    "uml": "MASSL",    # UMass Lowell
    "umd": "MD",       # Maryland
    "mount": "MSM",    # Mount St. Mary's
    "merr": "MRMK",    # Merrimack
    "mar": "MRST",     # Marist
    "w&m": "WM",       # William & Mary
    "cit": "CIT",      # The Citadel
    "sam": "SAM",      # Samford
    "tar": "TARL",     # Tarleton State (displayAbbrev)
    "wag": "WAG",      # Wagner
    "ccsu": "CCSU",    # Central Connecticut State
    "fgcu": "FGCU",    # Florida Gulf Coast
    "njit": "NJIT",    # NJIT
    "bing": "BING",    # Binghamton
    "bry": "BRY",      # Bryant
    "me": "ME",        # Maine
    "ucf": "UCF",      # UCF
    "cin": "CIN",      # Cincinnati
    "ucd": "UCD",      # UC Davis
    "cp": "CP",        # Cal Poly
    # CBB displayAbbreviation that match Kalshi (identity mappings for safety)
    "unco": "UNCO",    # Northern Colorado (displayAbbrev = UNCO, not ncol)
    "idst": "IDST",    # Idaho State (displayAbbrev = IDST, not idhst)
    "chat": "CHAT",    # Chattanooga
    "ark": "ARK",      # Arkansas
    "msst": "MSST",    # Mississippi State
    "ariz": "ARIZ",    # Arizona
    "okst": "OKST",    # Oklahoma State
    # --- Round 2: displayAbbreviation fixes (2026-02-13) ---
    "colum": "CLMB",   # Columbia
    "corn": "COR",     # Cornell
    "creigh": "CREI",  # Creighton
    "nova": "VILL",    # Villanova
    "etamu": "ETAM",   # East Texas A&M
    "most": "MOSU",    # Missouri State
    "sbu": "SBON",     # St. Bonaventure
    "gsu": "GAST",     # Georgia State
    "gcu": "GC",       # Grand Canyon
    "hpu": "HP",       # High Point
    "uca": "CARK",     # Central Arkansas
    "upst": "SCUS",    # SC Upstate
    "ncsu": "NCST",    # NC State
    "mtsu": "MTU",     # Middle Tennessee State
    "sdksu": "SDST",   # South Dakota State
    "kc": "UMKC",      # Kansas City (UMKC)
    "tom": "UST",      # St. Thomas Minnesota
    "m-oh": "MOH",     # Miami Ohio
    "ut": "UTU",       # Utah Tech (formerly Dixie State)
    "sfu": "SFPA",     # St. Francis PA
    "merc": "MHU",     # Mount Saint Mary's (PM uses MERC displayAbbrev)
    "tamu": "TXAM",    # Texas A&M (override slug tamu→AMCC for displayAbbrev)
    "haw": "HAW",      # Hawaii (identity - prevent fallthrough)
    "wcu": "WCU",      # Western Carolina (identity)
    "liu": "LIU",      # LIU (identity)
    "crei": "CREI",    # Creighton (override reverse mapping crei→CREIGH)
}

PM_TO_KALSHI_ABBREV.update(PM_DISPLAY_ABBREV_TO_KALSHI)

# Sport-specific PM→Kalshi overrides
# These resolve conflicts where the same PM abbreviation means different
# teams in different sports (e.g., "no" = NOP in NBA, UNO in CBB).
# Applied BEFORE the general PM_TO_KALSHI_ABBREV lookup.
SPORT_PM_OVERRIDES: dict[str, dict[str, str]] = {
    "cbb": {
        "no": "UNO",     # New Orleans (vs NBA NOP = Pelicans)
    },
}

# Known single-word school names that are NOT mascots
_SINGLE_WORD_SCHOOLS = {
    'Duke', 'Gonzaga', 'Purdue', 'Villanova', 'Creighton', 'Syracuse',
    'Stanford', 'Princeton', 'Harvard', 'Yale', 'Cornell', 'Dartmouth',
    'Columbia', 'Penn', 'Brown', 'Marquette', 'Baylor', 'Butler',
    'Georgetown', 'Vanderbilt', 'Michigan', 'Wisconsin', 'Minnesota',
    'Maryland', 'Rutgers', 'Nebraska', 'Northwestern', 'Indiana',
    'Oregon', 'Arizona', 'Colorado', 'Utah', 'California', 'Houston',
    'Cincinnati', 'Memphis', 'Tulane', 'Dayton', 'Richmond', 'Fordham',
    'Drexel', 'Delaware', 'Bucknell', 'Lafayette', 'Colgate', 'Army',
    'Navy', 'Lehigh', 'Vermont', 'Maine', 'Marshall', 'Louisiana',
    'Clemson', 'Virginia', 'Pittsburgh', 'Louisville', 'Auburn', 'Alabama',
    'Tennessee', 'Kentucky', 'Florida', 'Georgia', 'Mississippi', 'Arkansas',
    'Missouri', 'Xavier', 'Providence', 'Mercer', 'Furman', 'Samford',
    'Belmont', 'Drake', 'Bradley', 'Evansville', 'Valparaiso',
    'Wofford', 'Chattanooga', 'Jacksonville', 'Stetson', 'Liberty',
    'Lipscomb', 'Bellarmine', 'Niagara', 'Marist', 'Fairfield', 'Siena',
    'Canisius', 'Quinnipiac', 'Monmouth', 'Hofstra', 'Towson', 'Elon',
    'Hampton', 'Campbell', 'Charleston', 'Radford', 'Longwood',
    'Winthrop', 'Gardner-Webb', 'Kennesaw', 'Stetson', 'Denver',
}

def _is_mascot_only(name: str) -> bool:
    """Check if a team name looks like just a mascot (e.g. 'Wildcats', 'Eagles')."""
    if not name:
        return True
    words = name.strip().split()
    if len(words) >= 3:
        return False  # Multi-word names are likely full (e.g. "Maine Black Bears")
    if len(words) == 2:
        # Two words could be full ("Seton Hall") or mascot-ish ("Golden Eagles")
        # If first word is a common mascot prefix, it's still a mascot
        return False  # Err on the side of keeping 2-word names
    # Single word: mascot unless it's a known school name
    return name not in _SINGLE_WORD_SCHOOLS

# Full team names by sport (Kalshi abbreviation -> full franchise name)
# Split by sport to avoid collisions (CHI = Bulls in NBA, Blackhawks in NHL)
_NBA_FULL_NAMES = {
    "ATL": "Atlanta Hawks", "BOS": "Boston Celtics", "BKN": "Brooklyn Nets",
    "CHA": "Charlotte Hornets", "CHI": "Chicago Bulls", "CLE": "Cleveland Cavaliers",
    "DAL": "Dallas Mavericks", "DEN": "Denver Nuggets", "DET": "Detroit Pistons",
    "GSW": "Golden State Warriors", "HOU": "Houston Rockets", "IND": "Indiana Pacers",
    "LAC": "Los Angeles Clippers", "LAL": "Los Angeles Lakers", "MEM": "Memphis Grizzlies",
    "MIA": "Miami Heat", "MIL": "Milwaukee Bucks", "MIN": "Minnesota Timberwolves",
    "NOP": "New Orleans Pelicans", "NYK": "New York Knicks", "OKC": "Oklahoma City Thunder",
    "ORL": "Orlando Magic", "PHI": "Philadelphia 76ers", "PHX": "Phoenix Suns",
    "POR": "Portland Trail Blazers", "SAC": "Sacramento Kings", "SAS": "San Antonio Spurs",
    "TOR": "Toronto Raptors", "UTA": "Utah Jazz", "WAS": "Washington Wizards",
    "WSH": "Washington Wizards",  # Kalshi uses WSH not WAS
}
_NHL_FULL_NAMES = {
    "ANA": "Anaheim Ducks", "ARI": "Arizona Coyotes", "BOS": "Boston Bruins",
    "BUF": "Buffalo Sabres", "CAR": "Carolina Hurricanes", "CBJ": "Columbus Blue Jackets",
    "CGY": "Calgary Flames", "CHI": "Chicago Blackhawks", "COL": "Colorado Avalanche",
    "DAL": "Dallas Stars", "DET": "Detroit Red Wings", "EDM": "Edmonton Oilers",
    "FLA": "Florida Panthers", "LAK": "Los Angeles Kings", "MIN": "Minnesota Wild",
    "MTL": "Montreal Canadiens", "NJD": "New Jersey Devils", "NSH": "Nashville Predators",
    "NYI": "New York Islanders", "NYR": "New York Rangers", "OTT": "Ottawa Senators",
    "PHI": "Philadelphia Flyers", "PIT": "Pittsburgh Penguins", "SEA": "Seattle Kraken",
    "SJS": "San Jose Sharks", "STL": "St. Louis Blues", "TBL": "Tampa Bay Lightning",
    "TOR": "Toronto Maple Leafs", "UTA": "Utah Hockey Club", "VAN": "Vancouver Canucks",
    "VGK": "Vegas Golden Knights", "WPG": "Winnipeg Jets", "WSH": "Washington Capitals",
}
SPORT_FULL_NAMES = {"nba": _NBA_FULL_NAMES, "nhl": _NHL_FULL_NAMES}
# Flat fallback (NBA + NHL, NBA wins collisions — only used for backward compat)
TEAM_FULL_NAMES = {**_NHL_FULL_NAMES, **_NBA_FULL_NAMES}

# PM outcome name keywords -> Kalshi abbreviation
# Used for fuzzy verification when PM outcome names don't exactly match
PM_NAME_KEYWORDS = {
    # --- NBA ---
    # IMPORTANT: Only use UNIQUE mascot names that won't match CBB teams!
    # REMOVED: "hawks" (CBB has Jayhawks, Redhawks, Fighting Hawks, etc.)
    # REMOVED: "grizzlies" (CBB Montana Grizzlies)
    # REMOVED: "wolves" (too short, could match partial)
    "atlanta hawks": "ATL", "celtics": "BOS", "nets": "BKN", "hornets": "CHA",
    "bulls": "CHI", "cavaliers": "CLE", "cavs": "CLE",
    "mavericks": "DAL", "mavs": "DAL", "nuggets": "DEN",
    "pistons": "DET", "warriors": "GSW", "rockets": "HOU",
    "pacers": "IND", "clippers": "LAC", "lakers": "LAL",
    "memphis grizzlies": "MEM", "heat": "MIA", "bucks": "MIL",
    "timberwolves": "MIN", "pelicans": "NOP",
    "knicks": "NYK", "thunder": "OKC", "magic": "ORL",
    "76ers": "PHI", "sixers": "PHI", "suns": "PHX",
    "trail blazers": "POR", "blazers": "POR",
    "sacramento kings": "SAC",  # Full name to avoid collision with LA Kings (NHL)
    "spurs": "SAS", "raptors": "TOR", "jazz": "UTA",
    "wizards": "WSH",  # Kalshi uses WSH, not WAS
    # --- NHL ---
    # IMPORTANT: Only use UNIQUE mascot names that won't match CBB teams!
    # REMOVED: "wild" (matches CBB Wildcats), "grizzlies" (CBB Montana Grizzlies)
    # REMOVED: "hawks" (used by CBB teams like Jayhawks, Redhawks, Fighting Hawks)
    "anaheim ducks": "ANA", "coyotes": "ARI", "sabres": "BUF",
    "hurricanes": "CAR", "blue jackets": "CBJ", "flames": "CGY",
    "avalanche": "COL", "dallas stars": "DAL", "oilers": "EDM",
    "florida panthers": "FLA", "los angeles kings": "LAK", "minnesota wild": "MIN",
    "canadiens": "MTL", "habs": "MTL", "devils": "NJD",
    "predators": "NSH", "preds": "NSH", "islanders": "NYI",
    "rangers": "NYR", "senators": "OTT", "sens": "OTT",
    "penguins": "PIT", "pens": "PIT", "kraken": "SEA",
    "sharks": "SJS", "blues": "STL", "lightning": "TBL",
    "canucks": "VAN", "golden knights": "VGK",
    "jets": "WPG", "capitals": "WSH", "caps": "WSH",
    # --- CBB UNIQUE MASCOTS (only truly unique identifiers) ---
    # IMPORTANT: Ambiguous mascots (Bulldogs, Eagles, Wildcats, Tigers, etc.)
    # are intentionally OMITTED - let marketSides crossref handle them
    "razorbacks": "ARK",           # Arkansas (UNIQUE)
    "tar heels": "UNC",            # North Carolina (UNIQUE)
    "blue devils": "DUKE",         # Duke (UNIQUE)
    "blue demons": "DEP",          # DePaul (UNIQUE)
    "demon deacons": "WAKE",       # Wake Forest (UNIQUE)
    "jayhawks": "KU",              # Kansas (UNIQUE)
    "hoosiers": "IND",             # Indiana (UNIQUE)
    "fighting irish": "ND",        # Notre Dame (UNIQUE)
    "nittany lions": "PSU",        # Penn State (UNIQUE)
    "buckeyes": "OSU",             # Ohio State (UNIQUE)
    "wolverines": "MICH",          # Michigan (UNIQUE)
    "hawkeyes": "IOWA",            # Iowa (UNIQUE)
    "cyclones": "ISU",             # Iowa State (UNIQUE)
    "boilermakers": "PUR",         # Purdue (UNIQUE)
    "badgers": "WIS",              # Wisconsin (UNIQUE)
    "golden gophers": "MINN",      # Minnesota (UNIQUE)
    "cornhuskers": "NEB",          # Nebraska (UNIQUE)
    "volunteers": "TENN",          # Tennessee (UNIQUE)
    "crimson tide": "ALA",         # Alabama (UNIQUE)
    "gamecocks": "SCAR",           # South Carolina (UNIQUE)
    "commodores": "VAN",           # Vanderbilt (UNIQUE)
    "longhorns": "TEX",            # Texas (UNIQUE)
    "sooners": "OU",               # Oklahoma (UNIQUE)
    "red raiders": "TTU",          # Texas Tech (UNIQUE)
    "horned frogs": "TCU",         # TCU (UNIQUE)
    "hoyas": "GTWN",               # Georgetown (UNIQUE)
    "johnnies": "SJU",             # St. John's (UNIQUE)
    "red storm": "SJU",            # St. John's (UNIQUE)
    "bluejays": "CREI",            # Creighton (UNIQUE)
    "sun devils": "ASU",           # Arizona State (UNIQUE)
    "zags": "GONZ",                # Gonzaga (UNIQUE)
    "anteaters": "UCI",            # UC Irvine (UNIQUE)
    "gauchos": "UCSB",             # UC Santa Barbara (UNIQUE)
    "matadors": "CSN",             # Cal State Northridge (UNIQUE)
    "49ers": "LBSU",               # Long Beach State (UNIQUE)
    "aztecs": "SDSU",              # San Diego State (UNIQUE)
    "hokies": "VT",                # Virginia Tech (UNIQUE)
    "yellow jackets": "GT",        # Georgia Tech (UNIQUE)
    "orange": "SYR",               # Syracuse (Kalshi uses SYR)
    "spiders": "RICH",             # Richmond (UNIQUE)
    "flyers": "DAY",               # Dayton (UNIQUE)
    "musketeers": "XAV",           # Xavier (UNIQUE)
    "red foxes": "MRST",           # Marist (UNIQUE)
    "peacocks": "SPC",             # Saint Peter's (UNIQUE)
    "jaspers": "MAN",              # Manhattan (UNIQUE)
    "stags": "FAIR",               # Fairfield (UNIQUE)
    "great danes": "ALBY",         # Albany (UNIQUE)
    "river hawks": "MASSL",        # UMass Lowell (UNIQUE)
    "lancers": "CBU",              # California Baptist (UNIQUE)
    "black knights": "ARMY",       # Army (UNIQUE)
    "midshipmen": "NAVY",          # Navy (UNIQUE)
    "leopards": "LAF",             # Lafayette (UNIQUE)
    "crusaders": "HC",             # Holy Cross (UNIQUE)
    "mountain hawks": "LEH",       # Lehigh (UNIQUE)
    "seawolves": "STON",           # Stony Brook (UNIQUE)
    "tribe": "WM",                 # William & Mary (UNIQUE)
    "pride": "HOF",                # Hofstra (UNIQUE)
    "phoenix": "ELON",             # Elon (UNIQUE)
    "colonials": "GW",             # George Washington (UNIQUE)
    "bonnies": "SBON",             # St. Bonaventure (UNIQUE)
    "mocs": "CHAT",                # Chattanooga (UNIQUE)
    "hatters": "STET",             # Stetson (UNIQUE)
    "screaming eagles": "USI",     # Southern Indiana (UNIQUE)
    "leathernecks": "WIU",         # Western Illinois (UNIQUE)
    "fighting hawks": "UND",       # North Dakota (UNIQUE)
    "vandals": "IDHO",             # Idaho (UNIQUE)
    "bengals": "IDST",             # Idaho State (UNIQUE)
    "lumberjacks": "NAU",          # Northern Arizona (UNIQUE)
    "chippewas": "CMU",            # Central Michigan (UNIQUE)
    "ragin' cajuns": "ULL",        # Louisiana (UNIQUE)
    "fighting camels": "CAMP",     # Campbell (UNIQUE)
    "chargers": "NHC",             # New Haven (UNIQUE)
    "royals": "QUC",               # Queens (UNIQUE)
    "ospreys": "UNF",              # North Florida (UNIQUE)
    "quakers": "PENN",             # Penn (UNIQUE)
    "black bears": "ME",           # Maine (UNIQUE)
    # REMOVED: "catamounts" - shared by Vermont (UVM) AND Western Carolina (WCU)
    "skyhawks": "UTM",             # UT Martin (UNIQUE)
    "colonels": "EKY",             # Eastern Kentucky (UNIQUE)
    "bobcats": "MTST",             # Montana State (UNIQUE for MTST)
    # REMOVED: "grizzlies" (ambiguous - Montana CBB vs Memphis NBA)
    # REMOVED: "bears" (ambiguous - Baylor, Northern Colorado, etc.)
    # Let crossref fallback handle these using PM marketSides data
}
# fmt: on

# Pro-sport abbreviations (NBA + NHL) used to prevent cross-sport keyword
# matching. When identifying teams for a CBB game, reject any match that
# resolves to an NBA/NHL abbreviation — let the marketSides fallback handle it.
_NBA_ABBREVS = {
    "ATL", "BOS", "BKN", "CHA", "CHI", "CLE", "DAL", "DEN", "DET", "GSW",
    "HOU", "IND", "LAC", "LAL", "MEM", "MIA", "MIL", "MIN", "NOP", "NYK",
    "OKC", "ORL", "PHI", "PHX", "POR", "SAC", "SAS", "TOR", "UTA", "WSH",
}
_NHL_ABBREVS = {
    "ANA", "ARI", "BUF", "CAR", "CBJ", "CGY", "COL", "EDM", "FLA", "LAK",
    "MTL", "NJD", "NSH", "NYI", "NYR", "OTT", "PIT", "SEA", "SJS", "STL",
    "TBL", "VAN", "VGK", "WPG",
}
_PRO_SPORT_ABBREVS = _NBA_ABBREVS | _NHL_ABBREVS

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
os.makedirs(LOG_DIR, exist_ok=True)

logger = logging.getLogger("mapper")
logger.setLevel(logging.DEBUG)

# Console handler
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S"))
logger.addHandler(ch)

# File handler
fh = logging.FileHandler(LOG_FILE)
fh.setLevel(logging.DEBUG)
fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
logger.addHandler(fh)


# ---------------------------------------------------------------------------
# Kalshi API (read-only, no signing needed for public endpoints)
# For authenticated endpoints, import signing from arb_executor_v7
# ---------------------------------------------------------------------------
class KalshiClient:
    """Kalshi client for market discovery. Uses auth from executor."""

    def __init__(self, session: aiohttp.ClientSession):
        self.session = session
        self.base = KALSHI_BASE
        # Use authenticated API if available
        if HAS_EXECUTOR:
            self._api = KalshiAPI(KALSHI_API_KEY, KALSHI_PRIVATE_KEY)
        else:
            self._api = None

    async def get_markets_for_series(self, series_ticker: str) -> list[dict]:
        """Fetch all active markets for a series ticker."""
        markets = []
        cursor = None
        while True:
            # Build path with query params (matching executor format)
            path = f'/trade-api/v2/markets?series_ticker={series_ticker}&status=open&limit=200'
            if cursor:
                path += f'&cursor={cursor}'

            url = f"{self.base}{path}"

            # Auth headers (sign path without query params)
            headers = {}
            if self._api:
                headers = self._api._headers('GET', path)

            try:
                async with self.session.get(url, headers=headers,
                                            timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status != 200:
                        body = await resp.text()
                        logger.error(f"Kalshi markets fetch failed: {resp.status} - {body[:200]}")
                        break
                    data = await resp.json()
                    batch = data.get("markets", [])
                    markets.extend(batch)
                    cursor = data.get("cursor")
                    if not cursor or not batch:
                        break
            except Exception as e:
                logger.error(f"Kalshi API error: {e}")
                break

        return markets

    def parse_kalshi_ticker(self, ticker: str, series: str) -> Optional[dict]:
        """
        Parse a Kalshi ticker into components.
        Example: KXNBAGAME-26FEB05DENNYK-NYK
        Returns: {game_id: '26FEB05DENNYK', team: 'NYK', date: '2026-02-05'}
        """
        parts = ticker.split("-")
        if len(parts) != 3 or parts[0] != series:
            return None

        game_id = parts[1]  # e.g., '26FEB05DENNYK'
        team = parts[2]     # e.g., 'NYK'

        # Parse date from game_id: '26FEB05...' -> 2026-02-05
        try:
            date_str = game_id[:7]  # '26FEB05'
            year = 2000 + int(date_str[:2])
            month_str = date_str[2:5]
            day = int(date_str[5:7])
            months = {
                "JAN": 1, "FEB": 2, "MAR": 3, "APR": 4,
                "MAY": 5, "JUN": 6, "JUL": 7, "AUG": 8,
                "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12,
            }
            month = months.get(month_str)
            if not month:
                return None
            date = f"{year}-{month:02d}-{day:02d}"
        except (ValueError, IndexError):
            return None

        return {
            "game_id": game_id,
            "team": team,
            "date": date,
            "ticker": ticker,
        }


# ---------------------------------------------------------------------------
# Polymarket US API Client
# ---------------------------------------------------------------------------
class PolymarketUSClient:
    """PM US client for market discovery and outcome verification. Uses auth from executor."""

    def __init__(self, session: aiohttp.ClientSession):
        self.session = session
        self.base = PM_US_BASE
        # Use authenticated API if available
        if HAS_EXECUTOR:
            self._api = PolymarketUSAPI(PM_US_API_KEY, PM_US_SECRET_KEY)
        else:
            self._api = None

    def _headers(self, method: str, path: str) -> dict:
        """Get auth headers for PM US API."""
        if self._api:
            return self._api._headers(method, path)
        return {'Content-Type': 'application/json'}

    async def get_active_markets(self) -> list[dict]:
        """Fetch all active, open markets with pagination (API caps at 200/request)."""
        markets = []
        path = '/v1/markets'
        page_size = 200
        offset = 0
        try:
            while True:
                query = f'?active=true&closed=false&limit={page_size}&offset={offset}'
                url = f"{self.base}{path}{query}"
                async with self.session.get(url, headers=self._headers('GET', path),
                                            timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    if resp.status != 200:
                        body = await resp.text()
                        logger.error(f"PM US markets fetch failed: {resp.status} - {body[:200]}")
                        break
                    data = await resp.json()
                    batch = data.get("markets", data) if isinstance(data, dict) else data
                    if not isinstance(batch, list):
                        break
                    markets.extend(batch)
                    if len(batch) < page_size:
                        break
                    offset += page_size
        except Exception as e:
            logger.error(f"PM US API error: {e}")

        return markets

    async def get_market_detail(self, slug: str) -> Optional[dict]:
        """Fetch detailed market info including outcome names and token IDs."""
        path = f'/v1/markets/{slug}'
        url = f"{self.base}{path}"
        try:
            async with self.session.get(url, headers=self._headers('GET', path),
                                        timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status != 200:
                    body = await resp.text()
                    logger.warning(f"PM US market detail failed for {slug}: {resp.status} - {body[:200]}")
                    return None
                return await resp.json()
        except Exception as e:
            logger.error(f"PM US detail error for {slug}: {e}")
            return None

    def parse_pm_slug(self, slug: str) -> Optional[dict]:
        """
        Parse a PM US slug into components.
        Example: aec-nba-den-ny-2026-02-05
        Returns: {sport: 'nba', teams: ['den', 'ny'], date: '2026-02-05'}
        """
        parts = slug.split("-")
        if len(parts) < 6 or parts[0] != "aec":
            return None

        sport = parts[1]
        date = f"{parts[-3]}-{parts[-2]}-{parts[-1]}"

        # Teams are everything between sport and date
        teams = parts[2:-3]

        return {
            "sport": sport,
            "teams": teams,
            "date": date,
            "slug": slug,
        }


# ---------------------------------------------------------------------------
# Outcome Verification
# ---------------------------------------------------------------------------
def verify_outcome_name(outcome_name: str, expected_kalshi_abbrev: str, sport: str) -> bool:
    """
    Verify that a PM outcome name matches the expected Kalshi team.

    Uses multiple strategies:
    1. Direct full name match
    2. Keyword/mascot match
    3. City name match

    Returns True if we're confident the outcome matches the expected team.
    """
    name_lower = outcome_name.lower().strip()

    # Strategy 1: Full name match
    full_name = TEAM_FULL_NAMES.get(expected_kalshi_abbrev, "")
    if full_name and full_name.lower() in name_lower:
        return True
    if full_name and name_lower in full_name.lower():
        return True

    # Strategy 2: Keyword/mascot match
    for keyword, abbrev in PM_NAME_KEYWORDS.items():
        if keyword in name_lower and abbrev == expected_kalshi_abbrev:
            return True

    # Strategy 3: City name match (extract city from full name)
    if full_name:
        # "New York Knicks" -> check if "new york" is in outcome name
        city_parts = full_name.split()
        # Try progressively shorter prefixes of the name
        for i in range(len(city_parts) - 1, 0, -1):
            city = " ".join(city_parts[:i]).lower()
            if len(city) >= 4 and city in name_lower:
                return True

    return False


def identify_team_from_outcome(outcome_name: str, sport: str) -> Optional[str]:
    """
    Given a PM outcome name, identify which Kalshi team abbreviation it corresponds to.
    Returns the Kalshi abbreviation or None if unidentifiable.
    """
    name_lower = outcome_name.lower().strip()

    # Check all keywords
    best_match = None
    best_match_len = 0

    for keyword, abbrev in PM_NAME_KEYWORDS.items():
        if keyword in name_lower and len(keyword) > best_match_len:
            best_match = abbrev
            best_match_len = len(keyword)

    if best_match:
        # Prevent cross-sport matching: don't return NBA/NHL abbreviations
        # for CBB games (e.g. "warriors" in "Rainbow Warriors" → GSW is wrong)
        if sport == "cbb" and best_match in _PRO_SPORT_ABBREVS:
            return None
        if sport in ("nba", "nhl") and best_match not in _PRO_SPORT_ABBREVS:
            return None
        # Prevent NBA↔NHL cross-matching (e.g. "Kings" → SAC instead of LAK)
        if sport == "nhl" and best_match in _NBA_ABBREVS:
            return None
        if sport == "nba" and best_match in _NHL_ABBREVS:
            return None
        return best_match

    # Check full team names
    # IMPORTANT: Require high similarity to avoid partial matches like
    # "Grizzlies" matching "Memphis Grizzlies" in CBB context
    for abbrev, full_name in TEAM_FULL_NAMES.items():
        full_lower = full_name.lower()
        # Exact containment in either direction
        if full_lower in name_lower:
            return abbrev
        # For outcome contained in full name, require at least 60% length match
        # This prevents "Grizzlies" (9 chars) matching "Memphis Grizzlies" (17 chars)
        if name_lower in full_lower:
            ratio = len(name_lower) / len(full_lower)
            if ratio >= 0.60:
                return abbrev

    return None


# ---------------------------------------------------------------------------
# Core Mapping Logic
# ---------------------------------------------------------------------------
class PreGameMapper:
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.mappings: dict = {}
        self.stats = {
            "kalshi_markets": 0,
            "pm_markets": 0,
            "matched": 0,
            "verified": 0,
            "failed_verification": 0,
            "unmatched_kalshi": 0,
            "unmatched_pm": 0,
            "skipped_existing": 0,
        }

    def load_existing_mappings(self) -> dict:
        """Load existing mappings file if present."""
        if os.path.exists(MAPPING_FILE):
            try:
                with open(MAPPING_FILE, "r") as f:
                    data = json.load(f)
                    logger.info(f"Loaded {len(data.get('games', {}))} existing mappings")
                    return data
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Could not load existing mappings: {e}")
        return {"generated_at": None, "games": {}}

    def make_cache_key(self, sport: str, team1: str, team2: str, date: str) -> str:
        """
        Build canonical cache key matching arb_executor_v7.py format.
        MUST use same normalize_team_abbrev() as executor or keys won't match.
        Teams are normalized then sorted alphabetically.
        NOTE: UFC fighter codes must NOT go through normalize_team_abbrev
        because codes like 'VER' collide with college basketball (Vermont -> UVM).
        """
        if sport.lower() == "ufc":
            # UFC: use raw uppercase fighter codes, no canonical normalization
            norm1 = team1.upper()
            norm2 = team2.upper()
        elif HAS_EXECUTOR:
            norm1 = normalize_team_abbrev(team1)
            norm2 = normalize_team_abbrev(team2)
        else:
            norm1 = team1.upper()
            norm2 = team2.upper()
        teams = sorted([norm1, norm2])
        return f"{sport.lower()}:{teams[0]}-{teams[1]}:{date}"

    async def run(self, incremental: bool = False, verify_key: Optional[str] = None, debug_keys: bool = False):
        """Main mapping flow."""
        start_time = time.time()
        today = datetime.now(timezone(timedelta(hours=-5))).strftime("%Y-%m-%d")
        logger.info(f"{'='*60}")
        logger.info(f"Pre-Game Mapper — {today}")
        logger.info(f"Mode: {'incremental' if incremental else 'full sweep'}")
        logger.info(f"{'='*60}")

        # Load existing mappings for incremental mode
        existing = self.load_existing_mappings() if incremental else {"games": {}}

        async with aiohttp.ClientSession() as session:
            kalshi = KalshiClient(session)
            pm = PolymarketUSClient(session)

            # --- Step 1: Fetch all Kalshi markets ---
            logger.info("Step 1/5: Fetching Kalshi markets...")
            kalshi_games = {}  # cache_key -> {game_id, teams: {abbrev: ticker}, date}

            for sport_cfg in SPORTS_CONFIG:
                markets = await kalshi.get_markets_for_series(sport_cfg["series"])
                logger.info(f"  {sport_cfg['display']}: {len(markets)} markets")

                for mkt in markets:
                    ticker = mkt.get("ticker", "")
                    parsed = kalshi.parse_kalshi_ticker(ticker, sport_cfg["series"])
                    if not parsed:
                        continue

                    # Only today's games (or tomorrow for late listings)
                    if parsed["date"] != today:
                        # Allow tomorrow's games too
                        tomorrow = (datetime.now(timezone(timedelta(hours=-5))) + timedelta(days=1)).strftime("%Y-%m-%d")
                        if parsed["date"] != tomorrow:
                            continue

                    game_id = parsed["game_id"]
                    team = parsed["team"]
                    date = parsed["date"]

                    # Build a game entry keyed by game_id
                    if game_id not in kalshi_games:
                        kalshi_games[game_id] = {
                            "game_id": game_id,
                            "sport": sport_cfg["sport"],
                            "sport_display": sport_cfg["display"],
                            "date": date,
                            "teams": {},
                        }
                    kalshi_games[game_id]["teams"][team] = ticker
                    # Store Kalshi yes_bid for pm_long_team sanity check
                    yes_bid = mkt.get("yes_bid")
                    if yes_bid is not None:
                        if "prices" not in kalshi_games[game_id]:
                            kalshi_games[game_id]["prices"] = {}
                        kalshi_games[game_id]["prices"][team] = int(yes_bid)
                    # Store Kalshi full team name from yes_sub_title (e.g. "Seton Hall")
                    ysub = mkt.get("yes_sub_title", "")
                    if ysub:
                        if "kalshi_names" not in kalshi_games[game_id]:
                            kalshi_games[game_id]["kalshi_names"] = {}
                        kalshi_games[game_id]["kalshi_names"][team] = ysub
                    # Store event title once (e.g. "Seton Hall at UConn Winner?")
                    if "title" not in kalshi_games[game_id]:
                        kalshi_games[game_id]["title"] = mkt.get("title", "")

            # Build cache keys for Kalshi games
            kalshi_by_cache_key = {}
            for game_id, game in kalshi_games.items():
                teams = list(game["teams"].keys())
                if len(teams) != 2:
                    logger.debug(f"  Skipping {game_id}: {len(teams)} teams (need exactly 2)")
                    continue
                cache_key = self.make_cache_key(game["sport"], teams[0], teams[1], game["date"])
                kalshi_by_cache_key[cache_key] = game

            self.stats["kalshi_markets"] = len(kalshi_by_cache_key)
            logger.info(f"  Total Kalshi games (today/tomorrow): {len(kalshi_by_cache_key)}")

            # --- Step 2: Fetch all PM US markets ---
            logger.info("Step 2/5: Fetching PM US markets...")
            pm_markets_raw = await pm.get_active_markets()
            logger.info(f"  Raw PM markets: {len(pm_markets_raw)}")

            # Parse and index PM markets by cache key
            pm_by_cache_key = {}
            for mkt in pm_markets_raw:
                slug = mkt.get("slug", "")
                parsed = pm.parse_pm_slug(slug)
                if not parsed:
                    continue

                # Map PM sport to our sport names
                pm_sport = parsed["sport"]
                if pm_sport not in ("nba", "nhl", "cbb", "ufc"):
                    continue

                pm_teams = parsed["teams"]
                date = parsed["date"]

                # Convert PM team abbreviations to Kalshi abbreviations
                # Sport-specific overrides first, then general PM_TO_KALSHI_ABBREV
                sport_overrides = SPORT_PM_OVERRIDES.get(pm_sport, {})
                kalshi_teams = []
                for pt in pm_teams:
                    # UFC special handling: PM uses first3+last3 format (e.g., 'bramor')
                    # Kalshi uses last 3 chars of last name (e.g., 'MOR')
                    if pm_sport == "ufc" and len(pt) >= 3:
                        kt = pt[-3:].upper()
                    else:
                        kt = sport_overrides.get(pt)
                        if not kt:
                            kt = PM_TO_KALSHI_ABBREV.get(pt)
                        if not kt and HAS_EXECUTOR:
                            # Try normalizing through executor's canonical map
                            kt = normalize_team_abbrev(pt.upper())
                        if not kt:
                            kt = pt.upper()  # Fallback: use raw uppercase
                    kalshi_teams.append(kt)

                if len(kalshi_teams) >= 2:
                    cache_key = self.make_cache_key(pm_sport, kalshi_teams[0], kalshi_teams[1], date)
                    pm_by_cache_key[cache_key] = {
                        "slug": slug,
                        "market_data": mkt,
                        "pm_teams": pm_teams,
                        "kalshi_teams": kalshi_teams,
                        # Extract outcomes and marketSides from listing response
                        "outcomes": mkt.get("outcomes", []),
                        "market_sides": mkt.get("marketSides", []),
                    }

            self.stats["pm_markets"] = len(pm_by_cache_key)
            logger.info(f"  Parsed PM games: {len(pm_by_cache_key)}")

            # --- Step 3: Match games across platforms ---
            logger.info("Step 3/5: Matching games across platforms...")
            matched_keys = set(kalshi_by_cache_key.keys()) & set(pm_by_cache_key.keys())
            self.stats["matched"] = len(matched_keys)
            self.stats["unmatched_kalshi"] = len(kalshi_by_cache_key) - len(matched_keys)
            self.stats["unmatched_pm"] = len(pm_by_cache_key) - len(matched_keys)
            logger.info(f"  Matched: {len(matched_keys)}")
            logger.info(f"  Kalshi-only: {self.stats['unmatched_kalshi']}")
            logger.info(f"  PM-only: {self.stats['unmatched_pm']}")

            # Debug key analysis
            if debug_keys:
                print("\n" + "="*80)
                print("DEBUG: CACHE KEY ANALYSIS")
                print("="*80)

                kalshi_keys = set(kalshi_by_cache_key.keys())
                pm_keys = set(pm_by_cache_key.keys())
                kalshi_only = kalshi_keys - pm_keys
                pm_only = pm_keys - kalshi_keys

                print(f"\n--- MATCHED KEYS ({len(matched_keys)}) ---")
                for k in sorted(matched_keys)[:20]:
                    print(f"  {k}")
                if len(matched_keys) > 20:
                    print(f"  ... and {len(matched_keys) - 20} more")

                print(f"\n--- KALSHI-ONLY KEYS ({len(kalshi_only)}) ---")
                for k in sorted(kalshi_only):
                    game = kalshi_by_cache_key[k]
                    teams = list(game['teams'].keys())
                    print(f"  {k}")
                    print(f"    -> game_id: {game['game_id']}, teams: {teams}")

                print(f"\n--- PM-ONLY KEYS ({len(pm_only)}) ---")
                for k in sorted(pm_only):
                    info = pm_by_cache_key[k]
                    print(f"  {k}")
                    print(f"    -> slug: {info['slug']}")
                    print(f"    -> pm_teams (raw): {info['pm_teams']}")
                    print(f"    -> kalshi_teams (normalized): {info['kalshi_teams']}")

                # Analyze potential date mismatches
                print(f"\n--- DATE MISMATCH ANALYSIS ---")
                date_mismatches = []
                for pm_key in pm_only:
                    pm_parts = pm_key.split(':')
                    if len(pm_parts) == 3:
                        pm_sport, pm_teams_str, pm_date = pm_parts
                        # Check if same sport+teams exist on Kalshi with different date
                        for k_key in kalshi_only:
                            k_parts = k_key.split(':')
                            if len(k_parts) == 3:
                                k_sport, k_teams_str, k_date = k_parts
                                if pm_sport == k_sport and pm_teams_str == k_teams_str:
                                    date_mismatches.append((pm_key, k_key, pm_date, k_date))

                if date_mismatches:
                    print(f"  Found {len(date_mismatches)} potential date mismatches:")
                    for pm_k, k_k, pm_d, k_d in date_mismatches[:10]:
                        print(f"    PM: {pm_k}")
                        print(f"    Kalshi: {k_k}")
                        print(f"    Dates: PM={pm_d} vs Kalshi={k_d}")
                        print()
                else:
                    print("  No date mismatches found (teams match but dates don't)")

                # Analyze team normalization failures
                print(f"\n--- TEAM NORMALIZATION ANALYSIS ---")
                # Extract unique team pairs from PM-only
                pm_team_pairs = {}
                for k in pm_only:
                    parts = k.split(':')
                    if len(parts) == 3:
                        sport, teams_str, date = parts
                        key = f"{sport}:{teams_str}"
                        if key not in pm_team_pairs:
                            pm_team_pairs[key] = []
                        pm_team_pairs[key].append(date)

                # Extract from Kalshi-only
                kalshi_team_pairs = {}
                for k in kalshi_only:
                    parts = k.split(':')
                    if len(parts) == 3:
                        sport, teams_str, date = parts
                        key = f"{sport}:{teams_str}"
                        if key not in kalshi_team_pairs:
                            kalshi_team_pairs[key] = []
                        kalshi_team_pairs[key].append(date)

                print(f"  Unique PM team pairs (no Kalshi match): {len(pm_team_pairs)}")
                print(f"  Unique Kalshi team pairs (no PM match): {len(kalshi_team_pairs)}")

                # Show raw PM slugs that failed to match
                print(f"\n--- RAW PM SLUGS (first 30 unmatched) ---")
                unmatched_pm_slugs = []
                for mkt in pm_markets_raw:
                    slug = mkt.get("slug", "")
                    parsed = pm.parse_pm_slug(slug)
                    if parsed:
                        pm_sport = parsed["sport"]
                        if pm_sport in ("nba", "nhl", "cbb", "ufc"):
                            pm_teams = parsed["teams"]
                            date = parsed["date"]
                            kalshi_teams = []
                            for pt in pm_teams:
                                if pm_sport == "ufc" and len(pt) >= 3:
                                    kt = pt[-3:].upper()
                                else:
                                    kt = PM_TO_KALSHI_ABBREV.get(pt)
                                    if not kt and HAS_EXECUTOR:
                                        kt = normalize_team_abbrev(pt.upper())
                                    if not kt:
                                        kt = pt.upper()
                                kalshi_teams.append(kt)
                            if len(kalshi_teams) >= 2:
                                cache_key = self.make_cache_key(pm_sport, kalshi_teams[0], kalshi_teams[1], date)
                                if cache_key not in kalshi_keys:
                                    unmatched_pm_slugs.append({
                                        'slug': slug,
                                        'sport': pm_sport,
                                        'pm_teams': pm_teams,
                                        'kalshi_teams': kalshi_teams,
                                        'date': date,
                                        'cache_key': cache_key,
                                    })

                for item in unmatched_pm_slugs[:30]:
                    print(f"  {item['slug']}")
                    print(f"    sport={item['sport']}, pm_teams={item['pm_teams']} -> kalshi_teams={item['kalshi_teams']}")
                    print(f"    date={item['date']}, cache_key={item['cache_key']}")

                print("\n" + "="*80)
                print("END DEBUG KEY ANALYSIS")
                print("="*80 + "\n")

                # Exit early in debug mode
                return

            # Single-game verification mode
            if verify_key:
                matched_keys = {verify_key} if verify_key in matched_keys else set()
                if not matched_keys:
                    logger.error(f"Game {verify_key} not found in matched games")
                    return

            # Skip already-verified in incremental mode
            if incremental:
                new_keys = set()
                for key in matched_keys:
                    if key in existing.get("games", {}) and existing["games"][key].get("verified"):
                        self.stats["skipped_existing"] += 1
                    else:
                        new_keys.add(key)
                logger.info(f"  Skipping {self.stats['skipped_existing']} already verified")
                matched_keys = new_keys

            # --- Step 4: Verify outcomes using listing data ---
            # NOTE: PM /v1/markets/{slug} detail endpoint returns 404.
            # All data comes from the listing response already stored in pm_info.
            logger.info(f"Step 4/5: Verifying {len(matched_keys)} games...")
            verified_games = {}

            for i, cache_key in enumerate(sorted(matched_keys)):
                k_game = kalshi_by_cache_key[cache_key]
                pm_info = pm_by_cache_key[cache_key]
                slug = pm_info["slug"]
                mkt_data = pm_info["market_data"]

                logger.debug(f"  [{i+1}/{len(matched_keys)}] Verifying {cache_key} ({slug})")

                # Normalize Kalshi team keys for consistent comparison
                # Kalshi tickers use raw abbrevs (WAS, TB, LA, NJ) but cache keys
                # and PM mappings use canonical abbrevs (WSH, TBL, LAK, NJD)
                k_teams_normalized = {}
                for raw_team, ticker in k_game["teams"].items():
                    # UFC: skip normalize_team_abbrev to avoid collisions
                    if k_game.get("sport") == "ufc":
                        norm_team = raw_team.upper()
                    else:
                        norm_team = normalize_team_abbrev(raw_team) if HAS_EXECUTOR else raw_team
                    k_teams_normalized[norm_team] = ticker

                # Use outcomes from listing response (no detail endpoint needed)
                outcomes_raw = pm_info.get("outcomes", [])
                market_sides = pm_info.get("market_sides", [])

                # outcomes may be a JSON string like '["Team A", "Team B"]' — parse it
                if isinstance(outcomes_raw, str):
                    try:
                        outcomes = json.loads(outcomes_raw)
                    except (json.JSONDecodeError, ValueError):
                        outcomes = []
                else:
                    outcomes = outcomes_raw if isinstance(outcomes_raw, list) else []

                if len(outcomes) < 2:
                    logger.warning(f"  SKIP {cache_key}: Only {len(outcomes)} outcomes")
                    self.stats["failed_verification"] += 1
                    continue

                # Identify which outcome index maps to which team
                outcome_map = {}  # index -> kalshi_abbrev
                verification_details = []

                # CRITICAL FIX (2026-02-07): outcomeIndex in the PM trading API
                # corresponds to the `outcomes` array index, NOT the marketSides index!
                #
                # Test evidence: When sending outcomeIndex=0 on slug aec-nba-hou-okc-2026-02-07
                # with outcomes=["Rockets","Thunder"], we get position in "Rockets".
                # This proves outcomes[0] = outcomeIndex 0.
                #
                # The marketSides array may have a DIFFERENT order, so we must use
                # the outcomes array directly for determining outcomeIndex.

                # Strategy 1: Use outcomes array (PRIMARY - this is what trading API uses)
                # The outcomes array contains team names like ["Rockets", "Thunder"]
                for idx, outcome_name in enumerate(outcomes[:2]):
                    outcome_str = str(outcome_name).strip()
                    if not outcome_str:
                        continue

                    # Try to identify the team from the outcome name
                    identified = identify_team_from_outcome(outcome_str, k_game["sport"])
                    if identified:
                        outcome_map[idx] = {"team": identified, "name": outcome_str}
                        verification_details.append({
                            "index": idx,
                            "pm_name": outcome_str,
                            "mapped_to": identified,
                            "full_name": TEAM_FULL_NAMES.get(identified, "?"),
                            "method": "outcomes_array",
                        })
                    else:
                        logger.warning(f"  Could not identify team from outcome: '{outcome_str}'")

                # Strategy 1.5 (UFC): Match outcome names against Kalshi fighter names
                # For UFC, identify_team_from_outcome won't find fighters in keyword tables.
                # Instead, match PM outcome names against Kalshi's yes_sub_title names.
                if len(outcome_map) < 2 and k_game["sport"] == "ufc":
                    kalshi_names = k_game.get("kalshi_names", {})
                    if kalshi_names:
                        logger.debug(f"  {cache_key}: UFC fighter matching, kalshi_names={kalshi_names}")
                        for idx, outcome_name in enumerate(outcomes[:2]):
                            if idx in outcome_map:
                                continue  # Already mapped
                            outcome_str = str(outcome_name).strip().lower()
                            best_match_abbrev = None
                            best_match_score = 0
                            for abbrev, full_name in kalshi_names.items():
                                norm_abbrev = abbrev.upper()  # UFC: skip normalize_team_abbrev to avoid collisions
                                name_lower = full_name.lower().strip()
                                # Try exact match
                                if outcome_str == name_lower:
                                    best_match_abbrev = norm_abbrev
                                    best_match_score = 100
                                    break
                                # Try substring: outcome contains last name or full name
                                name_parts = name_lower.split()
                                if len(name_parts) >= 2:
                                    last_name = name_parts[-1]
                                    first_name = name_parts[0]
                                    # Check if outcome contains the last name
                                    if last_name in outcome_str and len(last_name) >= 3:
                                        score = len(last_name)
                                        if score > best_match_score:
                                            best_match_abbrev = norm_abbrev
                                            best_match_score = score
                                    # Check if full name is substring of outcome
                                    if name_lower in outcome_str:
                                        best_match_abbrev = norm_abbrev
                                        best_match_score = 100
                                        break
                                    # Check if outcome is substring of full name
                                    if outcome_str in name_lower and len(outcome_str) >= 4:
                                        score = len(outcome_str)
                                        if score > best_match_score:
                                            best_match_abbrev = norm_abbrev
                                            best_match_score = score
                            if best_match_abbrev:
                                outcome_map[idx] = {"team": best_match_abbrev, "name": str(outcome_name)}
                                verification_details.append({
                                    "index": idx,
                                    "pm_name": str(outcome_name),
                                    "mapped_to": best_match_abbrev,
                                    "full_name": kalshi_names.get(best_match_abbrev, kalshi_names.get(best_match_abbrev.upper(), "?")),
                                    "method": "ufc_fighter_name_match",
                                })
                                logger.debug(f"  UFC matched outcome[{idx}]='{outcome_name}' -> {best_match_abbrev}")

                # Strategy 2: If outcomes array failed, try using marketSides as backup
                # But note: marketSides index may NOT match outcomeIndex!
                # We can use marketSides for team identification, then match to outcomes.
                if len(outcome_map) < 2 and market_sides and len(market_sides) >= 2:
                    logger.warning(f"  {cache_key}: Falling back to marketSides (cross-referencing with outcomes)")
                    outcome_map = {}
                    verification_details = []

                    # Build a map of team name -> kalshi abbrev from marketSides
                    sport_overrides = SPORT_PM_OVERRIDES.get(k_game["sport"], {})
                    marketside_teams = {}
                    for side in market_sides[:2]:
                        team_info = side.get("team", {}) if isinstance(side, dict) else {}
                        if not team_info:
                            continue
                        # UFC: displayAbbreviation is full last name (e.g. 'Moutinho'),
                        # abbreviation is the 6-char slug code (e.g. 'krimou').
                        # Use abbreviation for UFC to extract correct last-3-chars.
                        if k_game["sport"] == "ufc":
                            abbrev = (team_info.get("abbreviation", "")
                                      or team_info.get("displayAbbreviation", ""))
                        else:
                            abbrev = (team_info.get("displayAbbreviation", "")
                                      or team_info.get("abbreviation", ""))
                        team_name = team_info.get("name", "")
                        if team_name and abbrev:
                            # UFC: use last 3 chars of abbreviation (same as PM slug logic)
                            if k_game["sport"] == "ufc" and len(abbrev) >= 3:
                                kalshi_abbrev = abbrev[-3:].upper()
                            else:
                                kalshi_abbrev = sport_overrides.get(abbrev.lower())
                                if not kalshi_abbrev:
                                    kalshi_abbrev = PM_TO_KALSHI_ABBREV.get(abbrev.lower())
                                if not kalshi_abbrev and HAS_EXECUTOR:
                                    kalshi_abbrev = normalize_team_abbrev(abbrev.upper())
                                if not kalshi_abbrev:
                                    kalshi_abbrev = abbrev.upper()
                            marketside_teams[team_name.lower()] = kalshi_abbrev

                    # Now match outcomes array to marketSides teams
                    # Outcome names are often just mascots ("Bulldogs") while
                    # marketSides has full names ("Mississippi State Bulldogs")

                    # Check for identical outcomes (e.g., "Rams" vs "Rams")
                    # When outcomes are identical, substring matching can't distinguish them.
                    # Fall back to positional mapping: marketSides[i] -> outcomes[i].
                    outcome_strs = [str(o).strip().lower() for o in outcomes[:2]]
                    if (len(outcome_strs) == 2 and outcome_strs[0] == outcome_strs[1]
                            and len(marketside_teams) == 2):
                        # Identical mascots — use marketSides order as positional mapping
                        logger.warning(f"  {cache_key}: Identical outcomes {outcomes[:2]}, using positional mapping")
                        ms_abbrevs = list(marketside_teams.values())
                        for idx in range(2):
                            outcome_map[idx] = {"team": ms_abbrevs[idx], "name": str(outcomes[idx])}
                            verification_details.append({
                                "index": idx,
                                "pm_name": str(outcomes[idx]),
                                "mapped_to": ms_abbrevs[idx],
                                "full_name": TEAM_FULL_NAMES.get(ms_abbrevs[idx], "?"),
                                "method": "marketSides_positional",
                            })
                    else:
                        for idx, outcome_name in enumerate(outcomes[:2]):
                            outcome_str = str(outcome_name).strip().lower()
                            matched_kalshi = None

                            # Try exact match first
                            if outcome_str in marketside_teams:
                                matched_kalshi = marketside_teams[outcome_str]
                            else:
                                # Try substring match: is the mascot contained in full team name?
                                for full_name, kalshi_abbr in marketside_teams.items():
                                    if outcome_str in full_name:
                                        matched_kalshi = kalshi_abbr
                                        break

                            if matched_kalshi:
                                outcome_map[idx] = {"team": matched_kalshi, "name": str(outcome_name)}
                                verification_details.append({
                                    "index": idx,
                                    "pm_name": str(outcome_name),
                                    "mapped_to": matched_kalshi,
                                    "full_name": TEAM_FULL_NAMES.get(matched_kalshi, "?"),
                                    "method": "marketSides_crossref",
                                })

                # Validate: both teams in the game should be mapped
                k_teams = set(k_teams_normalized.keys())
                mapped_teams = set(v["team"] for v in outcome_map.values())

                if len(outcome_map) != 2:
                    logger.warning(
                        f"  FAIL {cache_key}: Mapped {len(outcome_map)}/2 outcomes. "
                        f"Outcomes: {outcomes}"
                    )
                    self.stats["failed_verification"] += 1
                    continue

                if mapped_teams != k_teams:
                    logger.warning(
                        f"  FAIL {cache_key}: Team mismatch. "
                        f"Kalshi={k_teams}, PM mapped={mapped_teams}"
                    )
                    self.stats["failed_verification"] += 1
                    continue

                # Cross-verify: confirm each outcome name matches expected team
                for idx, outcome_data in outcome_map.items():
                    team_abbrev = outcome_data["team"]
                    # Use the team name from marketSides, not outcomes array
                    outcome_name = outcome_data["name"]
                    if not verify_outcome_name(outcome_name, team_abbrev, k_game["sport"]):
                        logger.warning(
                            f"  WEAK MATCH {cache_key}: outcome[{idx}]='{outcome_name}' "
                            f"-> {team_abbrev} (no name confirmation)"
                        )
                        # Still allow — abbreviation match from marketSides is reliable

                # Extract token IDs and long/short info from marketSides
                # CRITICAL: PM US sports markets are BINARY - only ONE tradeable side!
                # The team with "long": true is the tradeable side.
                # - BUY_YES = bet on the "long" team
                # - SELL_YES = bet AGAINST the "long" team = bet on the other team
                token_ids = {}
                pm_long_team = None  # The team where long=true
                if market_sides:
                    for idx, side in enumerate(market_sides[:2]):
                        if isinstance(side, dict):
                            token_id = side.get("tokenId", side.get("token_id", ""))
                            if token_id:
                                token_ids[idx] = str(token_id)
                            # Check if this side is the "long" side
                            if side.get("long") is True:
                                team_info = side.get("team", {})
                                # UFC: use abbreviation (6-char slug code), not displayAbbreviation (full last name)
                                if k_game["sport"] == "ufc":
                                    abbrev = (team_info.get("abbreviation", "")
                                              or team_info.get("displayAbbreviation", ""))
                                else:
                                    abbrev = (team_info.get("displayAbbreviation", "")
                                              or team_info.get("abbreviation", ""))
                                if abbrev:
                                    # Map PM abbreviation to Kalshi abbreviation
                                    sport_ov = SPORT_PM_OVERRIDES.get(k_game["sport"], {})
                                    # UFC: use last 3 chars, skip normalize_team_abbrev
                                    if k_game["sport"] == "ufc" and len(abbrev) >= 3:
                                        kalshi = abbrev[-3:].upper()
                                    else:
                                        kalshi = sport_ov.get(abbrev.lower())
                                        if not kalshi:
                                            kalshi = PM_TO_KALSHI_ABBREV.get(abbrev.lower())
                                        if not kalshi and HAS_EXECUTOR:
                                            kalshi = normalize_team_abbrev(abbrev.upper())
                                        if not kalshi:
                                            kalshi = abbrev.upper()
                                    pm_long_team = kalshi
                                    logger.debug(f"  {cache_key}: pm_long_team={pm_long_team} (from displayAbbrev={abbrev}, side[{idx}].long=True)")

                # Also check top-level market_data for token fields
                if not token_ids:
                    tokens = mkt_data.get("tokens", [])
                    if tokens:
                        for idx, token_entry in enumerate(tokens[:2]):
                            if isinstance(token_entry, dict):
                                token_ids[idx] = token_entry.get("token_id", token_entry.get("tokenId", ""))
                            elif isinstance(token_entry, str):
                                token_ids[idx] = token_entry

                # Build team_names lookup: kalshi_abbrev -> PM full team name
                team_names = {}
                if market_sides:
                    _sport_ov = SPORT_PM_OVERRIDES.get(k_game["sport"], {})
                    for _side in market_sides[:2]:
                        _ti = _side.get("team", {}) if isinstance(_side, dict) else {}
                        if not _ti:
                            continue
                        # UFC: use abbreviation (6-char slug code), not displayAbbreviation (full last name)
                        if k_game.get("sport") == "ufc":
                            _ab = (_ti.get("abbreviation", "") or _ti.get("displayAbbreviation", ""))
                        else:
                            _ab = (_ti.get("displayAbbreviation", "") or _ti.get("abbreviation", ""))
                        _fn = _ti.get("name", "")
                        if _ab and _fn:
                            # UFC: use last 3 chars, skip normalize_team_abbrev
                            if k_game.get("sport") == "ufc" and len(_ab) >= 3:
                                _ka = _ab[-3:].upper()
                            else:
                                _ka = _sport_ov.get(_ab.lower()) or PM_TO_KALSHI_ABBREV.get(_ab.lower())
                                if not _ka and HAS_EXECUTOR:
                                    _ka = normalize_team_abbrev(_ab.upper())
                                if not _ka:
                                    _ka = _ab.upper()
                            team_names[_ka] = _fn
                # Prefer sport-specific full names for NBA/NHL
                _sport_names = SPORT_FULL_NAMES.get(k_game.get("sport", ""), {})
                for _ta in k_teams_normalized:
                    if _ta in _sport_names:
                        team_names[_ta] = _sport_names[_ta]
                # For CBB and UFC: fall back to Kalshi yes_sub_title for names
                _k_names = k_game.get("kalshi_names", {})
                if k_game.get("sport") in ("cbb", "ufc"):
                    for _ta, _name in list(team_names.items()):
                        if _is_mascot_only(_name) and _ta in _k_names:
                            team_names[_ta] = _k_names[_ta]
                    # Fill missing teams/fighters from Kalshi names
                    for _ta in k_teams_normalized:
                        if _ta not in team_names and _ta in _k_names:
                            team_names[_ta] = _k_names[_ta]

                # Build the verified mapping entry
                entry = {
                    "cache_key": cache_key,
                    "sport": k_game["sport"],
                    "sport_display": k_game["sport_display"],
                    "date": k_game["date"],
                    "game_id": k_game["game_id"],
                    # PM US details
                    "pm_slug": slug,
                    "pm_condition_id": mkt_data.get("conditionId", mkt_data.get("condition_id", "")),
                    # CRITICAL: pm_long_team is the team where marketSides has long=true
                    # This determines which team is traded with BUY_YES vs SELL_YES
                    "pm_long_team": pm_long_team,
                    "pm_outcomes": {
                        str(idx): {
                            "team": outcome_data["team"],
                            "outcome_name": outcome_data["name"],
                            "token_id": token_ids.get(idx, ""),
                            "outcome_index": idx,
                        }
                        for idx, outcome_data in outcome_map.items()
                    },
                    # Kalshi details (normalized team abbrevs as keys)
                    "kalshi_tickers": k_teams_normalized,
                    # Full team names from PM API (kalshi_abbrev -> "School Name Mascot")
                    "team_names": team_names,
                    # Verification metadata
                    "verified": True,
                    "verified_at": datetime.now(timezone.utc).isoformat(),
                    "verification_details": verification_details,
                }

                # Add convenience lookups by team
                for idx, outcome_data in outcome_map.items():
                    team_abbrev = outcome_data["team"]
                    entry[f"team_{team_abbrev.lower()}_outcome_index"] = idx
                    entry[f"team_{team_abbrev.lower()}_token_id"] = token_ids.get(idx, "")

                # ── pm_long_team sanity check using Kalshi prices ──
                # PM bestBid is in long-team frame. If it diverges from Kalshi
                # price for pm_long_team by >15c, the long flag may be wrong.
                if pm_long_team:
                    k_prices = k_game.get("prices", {})
                    k_long_price = k_prices.get(pm_long_team)
                    pm_best_bid_raw = mkt_data.get("bestBid")
                    pm_best_bid = None
                    if pm_best_bid_raw is not None:
                        try:
                            val = float(pm_best_bid_raw)
                            # PM prices may be 0-1 (decimal) or 0-100 (cents)
                            pm_best_bid = int(val * 100) if val <= 1 else int(val)
                        except (ValueError, TypeError):
                            pass

                    if k_long_price is not None and pm_best_bid is not None and pm_best_bid > 0:
                        diff = abs(k_long_price - pm_best_bid)
                        inv_diff = abs(k_long_price - (100 - pm_best_bid))
                        if diff > 15 and inv_diff < diff:
                            # Other team in the game
                            other_teams = [t for t in k_teams_normalized if t != pm_long_team]
                            other_team = other_teams[0] if other_teams else "?"
                            logger.warning(
                                f"  [SWAP] {cache_key}: pm_long_team {pm_long_team} "
                                f"price mismatch! Kalshi {pm_long_team}={k_long_price}c "
                                f"vs PM bestBid={pm_best_bid}c (diff={diff}c). "
                                f"Inverted={100 - pm_best_bid}c (diff={inv_diff}c). "
                                f"Swapping pm_long_team to {other_team}"
                            )
                            entry["pm_long_team"] = other_team
                            entry["pm_long_team_swapped"] = True
                            entry["pm_long_team_original"] = pm_long_team

                verified_games[cache_key] = entry
                self.stats["verified"] += 1
                team0 = outcome_map.get(0, {}).get("team", "?") if outcome_map.get(0) else "?"
                team1 = outcome_map.get(1, {}).get("team", "?") if outcome_map.get(1) else "?"
                swap_note = " [SWAPPED]" if entry.get("pm_long_team_swapped") else ""
                logger.info(
                    f"  [OK] {cache_key}: "
                    f"outcome[0]={team0} "
                    f"outcome[1]={team1}"
                    f"{swap_note}"
                )

            # --- Step 5: Write output ---
            logger.info(f"Step 5/5: Writing mappings...")

            # Merge with existing in incremental mode
            if incremental:
                all_games = existing.get("games", {})
                all_games.update(verified_games)
            else:
                all_games = verified_games

            output = {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "generator": "pregame_mapper.py",
                "date": today,
                "stats": self.stats,
                "games": all_games,
            }

            if self.dry_run:
                logger.info("DRY RUN — not writing file")
                print(json.dumps(output, indent=2))
            else:
                # Merge with existing mappings
                existing = {}
                try:
                    with open(MAPPING_FILE, "r") as f:
                        existing = json.load(f)
                except (FileNotFoundError, json.JSONDecodeError):
                    pass
                existing.update(output)
                with open(MAPPING_FILE, "w") as f:
                    json.dump(existing, f, indent=2)
                logger.info(f"Wrote {len(output)} new/updated mappings ({len(existing)} total) to {MAPPING_FILE}")

        # --- Summary ---
        elapsed = time.time() - start_time
        logger.info(f"\n{'='*60}")
        logger.info(f"MAPPING COMPLETE in {elapsed:.1f}s")
        logger.info(f"  Kalshi games:        {self.stats['kalshi_markets']}")
        logger.info(f"  PM US games:         {self.stats['pm_markets']}")
        logger.info(f"  Matched:             {self.stats['matched']}")
        logger.info(f"  Verified:            {self.stats['verified']}")
        logger.info(f"  Failed verification: {self.stats['failed_verification']}")
        if incremental:
            logger.info(f"  Skipped (existing):  {self.stats['skipped_existing']}")
        logger.info(f"{'='*60}")

        # Log unmatched games for debugging
        if self.stats["unmatched_kalshi"] > 0:
            logger.debug("Unmatched Kalshi games:")
            for key in sorted(kalshi_by_cache_key.keys()):
                if key not in pm_by_cache_key:
                    logger.debug(f"  {key}")

        return output


# ---------------------------------------------------------------------------
# Executor Integration Helpers
# ---------------------------------------------------------------------------
def load_verified_mappings(filepath: str = MAPPING_FILE) -> dict:
    """
    Load verified mappings for use by the executor.
    Returns a dict keyed by cache_key.

    Usage in arb_executor_v7.py:
        from pregame_mapper import load_verified_mappings
        VERIFIED_MAPS = load_verified_mappings()

        # During scan, look up a game:
        mapping = VERIFIED_MAPS.get(cache_key)
        if not mapping or not mapping.get('verified'):
            logger.warning(f"UNVERIFIED MAPPING: {cache_key}, skipping trade")
            continue

        # Use pre-resolved values:
        pm_slug = mapping['pm_slug']
        pm_outcome_index = mapping[f'team_{team.lower()}_outcome_index']
        pm_token_id = mapping[f'team_{team.lower()}_token_id']
        kalshi_ticker = mapping['kalshi_tickers'][team]
    """
    if not os.path.exists(filepath):
        logger.warning(f"No mapping file found at {filepath}")
        return {}

    try:
        with open(filepath, "r") as f:
            data = json.load(f)

        games = data.get("games", {})
        generated = data.get("generated_at", "unknown")

        # Check staleness
        try:
            gen_time = datetime.fromisoformat(generated.replace("Z", "+00:00"))
            age_hours = (datetime.now(timezone.utc) - gen_time).total_seconds() / 3600
            if age_hours > 12:
                logger.warning(f"Mapping file is {age_hours:.1f} hours old — consider refreshing")
        except (ValueError, TypeError):
            pass

        logger.info(f"Loaded {len(games)} verified mappings (generated: {generated})")
        return games

    except (json.JSONDecodeError, KeyError) as e:
        logger.error(f"Failed to load mappings: {e}")
        return {}


def get_mapping_for_game(
    mappings: dict, cache_key: str
) -> Optional[dict]:
    """
    Get verified mapping for a specific game.
    Returns None if not found or not verified (executor should refuse to trade).
    """
    mapping = mappings.get(cache_key)
    if not mapping:
        return None
    if not mapping.get("verified"):
        return None
    return mapping


def get_team_outcome_index(mapping: dict, team_abbrev: str) -> Optional[int]:
    """Get the PM outcome index for a specific team in a verified mapping."""
    key = f"team_{team_abbrev.lower()}_outcome_index"
    return mapping.get(key)


def get_team_token_id(mapping: dict, team_abbrev: str) -> Optional[str]:
    """Get the PM token ID for a specific team in a verified mapping."""
    key = f"team_{team_abbrev.lower()}_token_id"
    val = mapping.get(key)
    return val if val else None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Pre-game market mapping agent for arb_executor_v7"
    )
    parser.add_argument(
        "--incremental",
        action="store_true",
        help="Only map new/unverified games (skip already verified)",
    )
    parser.add_argument(
        "--verify",
        type=str,
        default=None,
        help="Verify a single game by cache key (e.g., 'nba:DEN-NYK:2026-02-05')",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print mappings without writing file",
    )
    parser.add_argument(
        "--debug-keys",
        action="store_true",
        help="Print detailed cache key analysis for debugging match failures",
    )
    args = parser.parse_args()

    mapper = PreGameMapper(dry_run=args.dry_run)
    asyncio.run(mapper.run(incremental=args.incremental, verify_key=args.verify, debug_keys=args.debug_keys))


if __name__ == "__main__":
    main()
