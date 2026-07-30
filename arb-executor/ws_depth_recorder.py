#!/usr/bin/env python3
"""OMQS harness WS capture (spec v2 §2): sub-second per-level book + trades for the full tennis slate.
Subscribes orderbook_delta + trade + market_lifecycle_v2 for both legs of every today/tomorrow event,
logs RAW WS messages verbatim with receive-timestamps (book reconstructed offline -> no capturer bugs).
READ-ONLY: WS market-data subscription + disk write only; touches no orders/trading."""
import os,time,json,gzip,asyncio,base64,datetime,glob,urllib.request,re,sys,hashlib
from pathlib import Path
import websockets
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
HERE=Path("/root/Omi-Workspace/arb-executor")
for ln in (HERE/".env").read_text().splitlines():
    if "=" in ln and not ln.startswith("#"): k,v=ln.split("=",1); os.environ.setdefault(k.strip(),v.strip().strip('"'))
AK=os.environ["KALSHI_API_KEY"]; PK=serialization.load_pem_private_key((HERE/"kalshi.pem").read_bytes(),password=None,backend=default_backend())
WS_URL="wss://api.elections.kalshi.com/trade-api/ws/v2"; WS_PATH="/trade-api/ws/v2"
RESTB="https://api.elections.kalshi.com"   # paths already carry /trade-api/v2
SER=[
    "KXATPMATCH","KXWTAMATCH",
    "KXATPCHALLENGERMATCH","KXWTACHALLENGERMATCH",
    "KXITFMATCH","KXITFWMATCH",
]
OUT=HERE/"data/durable/ws_depth_recorder"; OUT.mkdir(exist_ok=True)
ET=datetime.timezone(datetime.timedelta(hours=-4))
SESSION_ID=datetime.datetime.now(datetime.timezone.utc).strftime(
    "%Y%m%dT%H%M%SZ"
)
def sign(ts,method,path):
    return base64.b64encode(PK.sign(f"{ts}{method}{path}".encode(),padding.PSS(mgf=padding.MGF1(hashes.SHA256()),salt_length=padding.PSS.DIGEST_LENGTH),hashes.SHA256())).decode()
def rest(path):
    ts=str(int(time.time()*1000)); h={"KALSHI-ACCESS-KEY":AK,"KALSHI-ACCESS-SIGNATURE":sign(ts,"GET",path.split("?")[0]),"KALSHI-ACCESS-TIMESTAMP":ts}
    return json.loads(urllib.request.urlopen(urllib.request.Request(RESTB+path,headers=h),timeout=20).read())
MONTH={'JAN':1,'FEB':2,'MAR':3,'APR':4,'MAY':5,'JUN':6,'JUL':7,'AUG':8,'SEP':9,'OCT':10,'NOV':11,'DEC':12}
def ev_date(et):
    m=re.search(r"-(\d{2})([A-Z]{3})(\d{2})",et)
    if not m: return None
    return datetime.date(2000+int(m.group(1)),MONTH[m.group(2)],int(m.group(3)))
def discover():
    """all market tickers (both legs) for events dated today or tomorrow."""
    today=datetime.datetime.now(ET).date(); tom=today+datetime.timedelta(days=1)
    tk=set()
    for s in SER:
        cur=None
        for _ in range(40):
            try: d=rest(f"/trade-api/v2/events?series_ticker={s}&with_nested_markets=true&limit=200&status=settled,open,closed,unopened"+(f"&cursor={cur}" if cur else ""))
            except Exception as e: break
            for ev in d.get("events",[]):
                et=ev.get("event_ticker",""); dt=ev_date(et)
                if dt not in (today,tom): continue
                for mk in ev.get("markets",[]):
                    if mk.get("ticker"): tk.add(mk["ticker"])
            cur=d.get("cursor")
            if not cur: break
    return tk
_w={"hr":None,"fh":None,"n":0}
_books={}

def _source_epoch(message):
    """Return a provider timestamp when the frame carries one; never invent it."""
    candidates=[]
    if isinstance(message,dict):
        candidates.extend(message.get(k) for k in ("ts","timestamp","time"))
        body=message.get("msg")
        if isinstance(body,dict):
            candidates.extend(body.get(k) for k in ("ts","timestamp","time"))
    for value in candidates:
        if value is None or isinstance(value,bool):
            continue
        try:
            if isinstance(value,str) and not value.replace(".","",1).isdigit():
                parsed=datetime.datetime.fromisoformat(value.replace("Z","+00:00"))
                return parsed.timestamp()
            number=float(value)
            if number>1e15: number/=1_000_000
            elif number>1e12: number/=1_000
            return number
        except (TypeError,ValueError,OverflowError):
            continue
    return None

def _apply_book_message(message):
    """Reconstruct the top of book while retaining every raw WS message."""
    if not isinstance(message,dict):
        return None
    kind=message.get("type")
    body=message.get("msg")
    if not isinstance(body,dict):
        return None
    ticker=body.get("market_ticker")
    if not ticker:
        return None
    if kind=="orderbook_snapshot":
        book={"yes":{},"no":{}}
        for side in ("yes","no"):
            for level in body.get(side) or []:
                if isinstance(level,(list,tuple)) and len(level)>=2:
                    price,qty=int(level[0]),int(level[1])
                    if qty>0: book[side][price]=qty
        _books[ticker]=book
    elif kind=="orderbook_delta":
        side=body.get("side")
        if side not in ("yes","no"):
            return None
        try:
            price,delta=int(body["price"]),int(body["delta"])
        except (KeyError,TypeError,ValueError):
            return None
        book=_books.setdefault(ticker,{"yes":{},"no":{}})
        quantity=book[side].get(price,0)+delta
        if quantity>0: book[side][price]=quantity
        else: book[side].pop(price,None)
    else:
        return None
    book=_books[ticker]
    yes_bid=max(book["yes"],default=None)
    no_bid=max(book["no"],default=None)
    return {
        "market_ticker":ticker,
        "yes_bid":yes_bid,
        "yes_ask":None if no_bid is None else 100-no_bid,
        "no_bid":no_bid,
        "no_ask":None if yes_bid is None else 100-yes_bid,
        "denominator_status":(
            "AVAILABLE"
            if yes_bid is not None and no_bid is not None
            else "NO_DENOMINATOR"
        ),
    }

def writer(obj):
    hr=datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d_%H")
    if hr!=_w["hr"]:
        if _w["fh"]: _w["fh"].close()
        # A process can be terminated between gzip blocks.  Never append a
        # restarted process behind that possibly incomplete member: give each
        # recorder session its own immutable stream.  Existing glob consumers
        # already read ``ws_*.jsonl.gz``.
        _w["fh"]=gzip.open(
            OUT/f"ws_{hr}_{SESSION_ID}_{os.getpid()}.jsonl.gz","at"
        ); _w["hr"]=hr
    _w["fh"].write(json.dumps(obj,separators=(",",":"))+"\n"); _w["n"]+=1
    if _w["n"]%200==0: _w["fh"].flush()
def status(m): print(f"[{datetime.datetime.now(ET).strftime('%H:%M:%S')}] {m}",flush=True)
async def run():
    subscribed=set(); msg_id=0; last_disc=0
    while True:
        try:
            ts=str(int(time.time()*1000))
            headers={"KALSHI-ACCESS-KEY":AK,"KALSHI-ACCESS-SIGNATURE":sign(ts,"GET",WS_PATH),"KALSHI-ACCESS-TIMESTAMP":ts}
            async with websockets.connect(WS_URL,additional_headers=headers,ping_interval=30,ping_timeout=10,max_size=10_000_000) as ws:
                status("WS connected"); subscribed=set()
                async def subscribe(tks):
                    nonlocal msg_id
                    new=[t for t in tks if t not in subscribed]
                    for i in range(0,len(new),50):
                        msg_id+=1; batch=new[i:i+50]
                        await ws.send(json.dumps({"id":msg_id,"cmd":"subscribe","params":{"channels":["orderbook_delta","trade","market_lifecycle_v2"],"market_tickers":batch}}))
                        subscribed.update(batch)
                    if new: status(f"subscribed +{len(new)} (total {len(subscribed)})")
                slate=discover(); last_disc=time.time(); await subscribe(list(slate))
                writer({"t":time.time(),"ev":"recorder_start","subscribed":len(subscribed)})
                while True:
                    try: raw=await asyncio.wait_for(ws.recv(),timeout=20)
                    except asyncio.TimeoutError:
                        if time.time()-last_disc>300:
                            slate=discover(); last_disc=time.time(); await subscribe(list(slate))
                        continue
                    now=time.time()
                    try: m=json.loads(raw)
                    except: continue
                    source_epoch=_source_epoch(m)
                    writer({
                        "t":round(now,3),
                        "received_at_utc":datetime.datetime.fromtimestamp(
                            now,datetime.timezone.utc
                        ).isoformat(),
                        "source_epoch":source_epoch,
                        "staleness_ms":(
                            None if source_epoch is None
                            else round(max(0.0,now-source_epoch)*1000,3)
                        ),
                        "staleness_status":(
                            "MEASURED"
                            if source_epoch is not None
                            else "NO_SOURCE_TIMESTAMP"
                        ),
                        "raw_ws_sha256":hashlib.sha256(raw.encode()).hexdigest(),
                        "bbo":_apply_book_message(m),
                        "m":m,
                    })
                    if time.time()-last_disc>300:
                        slate=discover(); last_disc=time.time(); await subscribe(list(slate))
        except Exception as e:
            status(f"WS error: {e}; reconnect in 5s"); await asyncio.sleep(5)
asyncio.run(run())
