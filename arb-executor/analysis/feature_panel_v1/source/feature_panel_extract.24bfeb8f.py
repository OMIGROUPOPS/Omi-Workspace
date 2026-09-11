#!/usr/bin/env python3
"""Bounded, read-only source adapter for the tick-library feature experiment.

Runs on droplet A at nice 10. The cutter, store and original Spaces objects
are inputs; only the explicitly selected feature_panel_v1 directory is written.
One library leg is resident at a time. Raw positive-print witnesses are a
separate local/private output, never a file to commit.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict, deque
from contextlib import ExitStack, closing, nullcontext
from datetime import datetime, timedelta, timezone
import csv
import gzip
import hashlib
import hmac
import http.client
import importlib.util
import io
import itertools
import json
import math
import os
from pathlib import Path
import statistics
import sqlite3
import subprocess
import sys
import time
import urllib.parse

sys.dont_write_bytecode = True
SCHEMA = "TICK_LIBRARY_FEATURE_SOURCES_V1"
REMOTE_ROOT = Path("/mnt/omi-trading-data-nyc3/library/feature_panel_v1")
ET = timezone(timedelta(hours=-4))  # Filed Spaces recorder/parser clock.


def finite(value):
    try:
        result = float(value)
    except (ValueError, TypeError):
        return None
    return result if math.isfinite(result) else None


def source_epoch(value):
    # Exact recorder format fast path; avoid strptime's repeated format/locale
    # machinery for millions of rows. Fallback preserves irregular valid input.
    if len(value)==22 and value[4]=="-" and value[7]=="-" and value[10]==" " and value[13]==":" and value[16]==":" and value[19]==" " and value[20:] in ("AM","PM"):
        hour=int(value[11:13])
        if not 1<=hour<=12:
            raise ValueError("INVALID_SOURCE_HOUR")
        return datetime(int(value[:4]),int(value[5:7]),int(value[8:10]),
            hour%12+(12 if value[20:]=="PM" else 0),int(value[14:16]),int(value[17:19]),tzinfo=ET).timestamp()
    return datetime.strptime(value, "%Y-%m-%d %I:%M:%S %p").replace(tzinfo=ET).timestamp()


def minute_end(ts):
    return (math.floor(ts / 60) + 1) * 60


def print_key(row):
    return (float(row["ts"]), float(row["price"]), float(row["size"]))


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


class HashReader(io.RawIOBase):
    def __init__(self, source):
        self.source = source
        self.digest = hashlib.sha256()
        self.md5 = hashlib.md5(usedforsecurity=False)
        self.bytes = 0
        self.read_seconds = 0.0

    def readable(self):
        return True

    def readinto(self, target):
        started=time.monotonic()
        block = self.source.read(len(target))
        self.read_seconds+=time.monotonic()-started
        self.digest.update(block)
        self.md5.update(block)
        self.bytes += len(block)
        target[:len(block)] = block
        return len(block)


def spaces_environment(repo_root):
    """Credentials never leave subprocess environment or appear in receipts."""
    env = dict(os.environ)
    envfile = Path(repo_root) / "arb-executor/.env"
    if envfile.exists():
        for line in envfile.read_text(encoding="utf-8").splitlines():
            if line.strip() and not line.lstrip().startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                env.setdefault(key.strip(), value.strip().strip('"').strip("'"))
    env.update(RCLONE_CONFIG_SPACES_TYPE="s3", RCLONE_CONFIG_SPACES_PROVIDER="DigitalOcean",
        RCLONE_CONFIG_SPACES_ACCESS_KEY_ID=env.get("SPACES_KEY", ""),
        RCLONE_CONFIG_SPACES_SECRET_ACCESS_KEY=env.get("SPACES_SECRET", ""),
        RCLONE_CONFIG_SPACES_ENDPOINT="nyc3.digitaloceanspaces.com")
    return env


class SpacesClient:
    """Persistent SigV4 GET, inherited transport form from consolidation.

    No listing, upload or mutation method. Response is streamed, not read into
    a whole-object byte string. Authentication is never written to outputs.
    """
    def __init__(self, env):
        self.key=env.get("SPACES_KEY", "")
        self.secret=env.get("SPACES_SECRET", "")
        if not self.key or not self.secret:
            raise ValueError("SPACES_CREDENTIALS_NOT_CONFIGURED")
        self.connection=None

    def open(self, key):
        host="nyc3.digitaloceanspaces.com"
        path="/omi-tick-archive/"+urllib.parse.quote(key,safe="/-_.~")
        now=datetime.now(timezone.utc)
        amz=now.strftime("%Y%m%dT%H%M%SZ");day=now.strftime("%Y%m%d")
        payload=hashlib.sha256(b"").hexdigest()
        canonical_headers=f"host:{host}\nx-amz-content-sha256:{payload}\nx-amz-date:{amz}\n"
        signed="host;x-amz-content-sha256;x-amz-date"
        canonical="\n".join(["GET",path,"",canonical_headers,signed,payload])
        scope=f"{day}/nyc3/s3/aws4_request"
        sign_text="\n".join(["AWS4-HMAC-SHA256",amz,scope,hashlib.sha256(canonical.encode()).hexdigest()])
        signing=("AWS4"+self.secret).encode()
        for component in (day,"nyc3","s3","aws4_request"):
            signing=hmac.new(signing,component.encode(),hashlib.sha256).digest()
        signature=hmac.new(signing,sign_text.encode(),hashlib.sha256).hexdigest()
        headers={"Host":host,"x-amz-date":amz,"x-amz-content-sha256":payload,
            "Authorization":f"AWS4-HMAC-SHA256 Credential={self.key}/{scope}, SignedHeaders={signed}, Signature={signature}"}
        for attempt in range(2):
            if self.connection is None:
                self.connection=http.client.HTTPSConnection(host,443,timeout=120)
            try:
                self.connection.request("GET",path,headers=headers)
                response=self.connection.getresponse()
                if response.status!=200:
                    response.close()
                    raise RuntimeError("SOURCE_OBJECT_HTTP_STATUS:"+str(response.status))
                return response
            except (http.client.HTTPException,OSError):
                self.connection.close();self.connection=None
                if attempt:
                    raise RuntimeError("SOURCE_OBJECT_CONNECTION_FAILED") from None


def read_object(obj, client, consume):
    if not obj.startswith(("spaces:ticks/", "spaces:trades/")) or ".." in obj:
        raise ValueError("UNSUPPORTED_OR_UNSAFE_SOURCE_OBJECT")
    started=time.monotonic()
    response=client.open(obj.split(":",1)[1])
    response_etag=(response.getheader("ETag") or "").strip('"')
    hashed = HashReader(response)
    rows = 0
    callback_seconds=0.0
    try:
        with io.BufferedReader(hashed) as buffered, gzip.GzipFile(fileobj=buffered) as zipped:
            with io.TextIOWrapper(zipped, encoding="utf-8-sig", errors="strict", newline="") as text:
                reader = csv.DictReader(text)
                columns = reader.fieldnames or []
                for ordinal, row in enumerate(reader):
                    callback_started=time.monotonic()
                    consume(row, ordinal)
                    callback_seconds+=time.monotonic()-callback_started
                    rows += 1
    finally:
        response.close()
    print("SOURCE_PROGRESS "+json.dumps(dict(object=obj,compressed_bytes=hashed.bytes,
        raw_rows=rows,download_and_parse_seconds=time.monotonic()-started,
        network_read_seconds=hashed.read_seconds,callback_seconds=callback_seconds)),flush=True)
    return dict(object=obj, compressed_sha256=hashed.digest.hexdigest(),
                compressed_md5=hashed.md5.hexdigest(), compressed_bytes=hashed.bytes, raw_rows=rows, columns=columns,
                observed_etag=response_etag,
                hash_basis="Entire original compressed object streamed by read-only persistent SigV4 HTTPS GET")


def book_from_source(raw, ordinal, obj, parsed_epoch=None):
    ts = source_epoch(raw["ts_et"]) if parsed_epoch is None else parsed_epoch
    result = dict(source_epoch=ts, available_epoch=ts, original_timestamp=raw["ts_et"],
        receipt_epoch=None, receipt_clock_status="NOT_STORED; recorded ET-second clock only",
        source_object=obj, source_row=ordinal,
        bids=[[finite(raw.get("bid_1")), finite(raw.get("bid_1_sz"))]],
        asks=[[finite(raw.get("ask_1")), finite(raw.get("ask_1_sz"))]])
    for name in ("bid_depth_5", "ask_depth_5", "depth_ratio", "mid", "last_trade"):
        result[name] = finite(raw.get(name))
    oi_names = [name for name in ("open_interest", "open_interest_fp", "open_interest_ffill") if name in raw]
    result["open_interest"] = {name: finite(raw[name]) for name in oi_names}
    result["open_interest_status"] = "SOURCE_FIELD" if oi_names else "STORE_SILENT: field absent"
    result["depth_status"] = ("COMPLETE_FIVE_LEVEL_FIELDS" if all(
        f"{side}_{i}" in raw and f"{side}_{i}_sz" in raw for side in ("bid", "ask") for i in range(1, 6))
        else "STORE_SILENT: incomplete ladder columns")
    return result


def attach_takers(accepted, original, unverified_spaces=False):
    """Attach only exact surviving Spaces prints, preserving cutter precedence.

    Within an exact source key, the cutter's cross-source conflict keeps the
    last rowid, so retain the corresponding last N original source rows. Never
    infer aggressor for backfill/public rows or price/book direction.
    """
    needed = Counter(print_key(row) for row in accepted if row["src"] == "spaces_trades" and not unverified_spaces)
    queues = {}
    for key, count in needed.items():
        matches = original.get(key, [])
        if len(matches) < count:
            raise ValueError("ORIGINAL_SPACES_PRINT_JOIN_MISMATCH:" + repr(key))
        queues[key] = deque(matches[-count:])
    output = []
    for row in accepted:
        new = dict(row)
        if row["src"]=="spaces_trades" and unverified_spaces:
            new.update(taker_side=None,taker_status="STORE_SILENT: original object binding unverified; excluded from model")
            output.append(new)
            continue
        if row["src"] == "spaces_trades":
            source = queues[print_key(row)].popleft()
            token = source["taker_side"]
            new.update(taker_side=token if token in ("yes", "no") else None,
                taker_status="STORED" if token in ("yes", "no") else "STORE_SILENT: unknown source token",
                original_source_row=source["source_row"], original_source_object=source["source_object"])
        else:
            new.update(taker_side=None, taker_status="STORE_SILENT: surviving source lacks aggressor extract")
        output.append(new)
    return output


def two_sided_book(book):
    bid,bid_size=book["bids"][0]
    ask,ask_size=book["asks"][0]
    return (all(value is not None for value in (bid,bid_size,ask,ask_size))
            and bid>0 and ask>0 and bid<ask and bid_size>0 and ask_size>0)


def verify_library(leg, accepted):
    count = len(accepted)
    if count != leg["true_print_count_in_span"]:
        raise ValueError("FINAL_ACCEPTED_COUNT_MISMATCH:" + leg["ticker"])
    groups = iter(itertools.groupby(accepted, key=lambda row: math.floor(row["ts"])))
    current = next(groups, None)
    cumulative, checked = 0.0, 0
    for point in leg["path"]:
        while current is not None and current[0] <= math.floor(point["ts"]):
            for row in current[1]:
                cumulative += float(row["size"])
            current = next(groups, None)
        if cumulative != point["volume_cum"]:
            raise ValueError("PATH_VOLUME_MISMATCH:" + leg["ticker"] + ":" + str(point["ts"]))
        checked += 1
    return dict(accepted_count=count, final_count_matches=True,
                path_volume_points_checked=checked, path_volume_matches=True)


def minute_features(leg, accepted, books):
    by_minute = defaultdict(list)
    for row in accepted:
        by_minute[minute_end(row["ts"])].append(row)
    output = []
    book_index, current_book, previous_book = 0, None, None
    first = minute_end(leg["formation_end_epoch"])
    for end in range(int(first), int(math.ceil(leg["bell_epoch"])), 60):
        if end >= leg["bell_epoch"]:
            break  # no post-bell close, no partial-minute future borrowing
        while book_index < len(books) and books[book_index]["source_epoch"] < end:
            current_book = books[book_index]
            book_index += 1
        rows = by_minute.get(end, [])
        positive = [row for row in rows if row["size"] > 0]
        known = all(row.get("taker_side") in ("yes", "no") for row in positive)
        yes = sum(row["size"] for row in positive if row.get("taker_side") == "yes")
        no = sum(row["size"] for row in positive if row.get("taker_side") == "no")
        prices = [row["price"] for row in positive]
        stamps = sorted(row["ts"] for row in positive)
        gaps = [b-a for a,b in zip(stamps, stamps[1:])]
        def top(book, side):
            return book[side][0][0] if book else None
        bid, ask = top(current_book, "bids"), top(current_book, "asks")
        old_bid, old_ask = top(previous_book, "bids"), top(previous_book, "asks")
        output.append(dict(available_epoch=end, interval_start_epoch=max(end-60, leg["formation_end_epoch"]),
            interval_end_epoch=end, interval="[start,end)", partial_formation_minute=end-60<leg["formation_end_epoch"],
            accepted_print_count=len(rows), positive_size_trade_count=len(positive),
            contracts_total=sum(row["size"] for row in positive),
            taker_yes_contracts=yes if known else None, taker_no_contracts=no if known else None,
            taker_flow_contracts=yes-no if known else None,
            taker_completeness="COMPLETE_ACCEPTED_POSITIVE_PRINTS" if known else "STORE_SILENT: some accepted aggressors absent",
            known_taker_positive_print_count=sum(row.get("taker_side") in ("yes", "no") for row in positive),
            price_min_cents=min(prices) if prices else None, price_max_cents=max(prices) if prices else None,
            distinct_print_prices=len(set(prices)), intertrade_gap_std_seconds=statistics.pstdev(gaps) if len(gaps)>=2 else None,
            clustering_status="MEASURED" if len(gaps)>=2 else "STORE_SILENT: fewer than three positive prints",
            bid_close_cents=bid, ask_close_cents=ask, previous_bid_close_cents=old_bid, previous_ask_close_cents=old_ask,
            bid_quote_delta_cents=bid-old_bid if bid is not None and old_bid is not None else None,
            ask_quote_delta_cents=ask-old_ask if ask is not None and old_ask is not None else None,
            book_observed_epoch=current_book["source_epoch"] if current_book else None,
            book_status="RECORDED_SOURCE_ASOF" if current_book else "STORE_SILENT: no preceding source book"))
        previous_book = current_book
    return output


def clock_provenance(leg):
    bell = str(leg.get("bell_source", ""))
    return dict(formation_source=leg.get("formation_source"), bell_source=leg.get("bell_source"),
        bell_source_field=leg.get("bell_source_field"), span_method=leg.get("span_method"),
        formation_publication_epoch=None, bell_publication_epoch=None,
        formation_publication_status="NOT_STORED: derivation clock is not publication proof",
        bell_publication_status="RETROSPECTIVE_TRADE_DENSITY_INFERENCE" if "trade_density" in bell
            else "NOT_STORED: filed event clock is not publication proof",
        prediction_input_warning="No inferred publication timestamp or full-span cadence is a causal feature")


def extract_leg(connection, leg, cutter, env):
    if cutter.tune_named_event(leg["event_id"]):
        raise ValueError("EXAM_EVENT_REFUSED")
    formation, bell = leg["formation_end_epoch"], leg["bell_epoch"]
    removed = Counter()
    accepted = [dict(row) for row in cutter.accepted_print_rows(connection, leg["ticker"],
        joined=leg.get("include_other_roles", False), before=bell, after=formation, removed=removed)]
    if any(row["event"] != leg["event_id"] or row.get("src_role") == "TUNE_SAMPLE"
           or row["size"] is None or row["size"] < 0 for row in accepted):
        raise ValueError("SOURCE_IDENTITY_ROLE_OR_SIZE_ERROR")
    accepted.sort(key=lambda row: (math.floor(row["ts"]), row["rowid"]))
    verified = verify_library(leg, accepted)
    original, books, manifests = defaultdict(list), {}, []
    first_book = first_two_sided_book = first_book_in_span = last_book_before_formation = None
    first_book_was_two_sided=None
    preceding_book_raw=None
    # Explicit source-object references only; no guessed bucket enumeration.
    refs={row.get("obj") for row in leg.get("cadence", {}).get("source_objects", [])}
    refs.update(leg.get("cadence",{}).get("objects_without_cadence",[]))
    refs.update(row.get("obj") for row in accepted)
    objects = sorted(obj for obj in refs if obj and obj.startswith(("spaces:ticks/", "spaces:trades/")))
    for obj in objects:
        prefix = obj.split(":", 1)[1].split("/", 1)[0]
        def consume(raw, ordinal):
            nonlocal first_book, first_two_sided_book, first_book_in_span, last_book_before_formation
            nonlocal first_book_was_two_sided
            nonlocal preceding_book_raw
            if raw.get("ticker") != leg["ticker"]:
                raise ValueError("ORIGINAL_OBJECT_TICKER_MISMATCH")
            ts = source_epoch(raw["ts_et"])
            if ts >= bell:
                return
            if prefix == "trades":
                if ts < formation:
                    return
                price, size = finite(raw.get("price")), finite(raw.get("count"))
                if price is None or size is None:
                    raise ValueError("INVALID_ORIGINAL_TRADE")
                original[(ts, price, size)].append(dict(taker_side=raw.get("taker_side"),
                    source_row=ordinal, source_object=obj))
            else:
                # Keep last original row per recorded second, including the
                # latest preformation book needed for the causal first state.
                needs_top=(first_book is None or ts<first_book or first_two_sided_book is None or ts<first_two_sided_book)
                top=(dict(bids=[[finite(raw.get("bid_1")),finite(raw.get("bid_1_sz"))]],
                          asks=[[finite(raw.get("ask_1")),finite(raw.get("ask_1_sz"))]]) if needs_top else None)
                if first_book is None or ts<first_book:
                    first_book=ts
                    first_book_was_two_sided=two_sided_book(top)
                if ts>=formation:
                    first_book_in_span=ts if first_book_in_span is None else min(first_book_in_span,ts)
                else:
                    last_book_before_formation=ts if last_book_before_formation is None else max(last_book_before_formation,ts)
                if (first_two_sided_book is None or ts<first_two_sided_book) and two_sided_book(top):
                    first_two_sided_book=ts if first_two_sided_book is None else min(first_two_sided_book,ts)
                # Before formation retain only the latest seed, not an entire
                # earlier market lifetime in memory.
                key = ts if ts >= formation else "preformation"
                if key=="preformation":
                    if preceding_book_raw is None or ts>=preceding_book_raw[0]:
                        preceding_book_raw=(ts,raw,ordinal,obj)
                else:
                    books[key] = book_from_source(raw,ordinal,obj,ts)
        try:
            manifest=read_object(obj, env, consume)
        except (RuntimeError,OSError,ValueError,csv.Error) as error:
            manifests.append(dict(object=obj,columns=[],compressed_sha256=None,compressed_md5=None,
                model_eligible=False,consolidation_object_match="UNVERIFIED: source object read/parse failed",
                failure_type=type(error).__name__))
            continue
        binding=connection.execute("SELECT etag FROM ingest_log WHERE path=?",(obj,)).fetchone()
        etag=binding[0] if binding else None
        manifest["consolidation_etag"]=etag
        simple=(isinstance(etag,str) and len(etag.strip('"'))==32 and all(c in "0123456789abcdefABCDEF" for c in etag.strip('"')))
        matches=simple and manifest["compressed_md5"]==etag.strip('"').lower()
        manifest["consolidation_object_match"]=("VERIFIED_MD5_ETAG" if matches else
            "UNVERIFIED: original object differs from filed ETag" if simple else "UNVERIFIED: no filed simple MD5 ETag")
        manifest["model_eligible"]=matches
        manifests.append(manifest)
    if preceding_book_raw is not None:
        ts,raw,ordinal,obj=preceding_book_raw
        books["preformation"]=book_from_source(raw,ordinal,obj,ts)
    unverified={item["object"] for item in manifests if not item["model_eligible"]}
    sorted_books = sorted((book for book in books.values() if book["source_object"] not in unverified), key=lambda book:book["source_epoch"])
    if any(obj.startswith("spaces:ticks/") for obj in unverified):
        first_book=first_two_sided_book=first_book_in_span=last_book_before_formation=None
        first_book_was_two_sided=None
    preceding = [book for book in sorted_books if book["source_epoch"] < formation]
    sorted_books = preceding[-1:] + [book for book in sorted_books if book["source_epoch"] >= formation]
    observation_epochs=[book["source_epoch"] for book in sorted_books]
    enriched = attach_takers(accepted, original, any(obj.startswith("spaces:trades/") for obj in unverified))
    minutes = minute_features(leg, enriched, sorted_books)
    # Exact feature state compaction, not temporal sampling. Independent
    # observation epochs retain every refresh for causal freshness/cadence.
    kept=[];previous=None
    consumed=("bids","asks","bid_depth_5","ask_depth_5","depth_ratio","mid","last_trade","open_interest","open_interest_status","depth_status")
    for book in sorted_books:
        state=json.dumps({key:book[key] for key in consumed},sort_keys=True,separators=(",",":"))
        if state!=previous:
            kept.append(book);previous=state
    sorted_books=kept
    base = {key: leg[key] for key in ("event_id", "ticker", "leg_id", "category", "formation_end_epoch", "bell_epoch")}
    panel = dict(base, schema=SCHEMA, minute_features=minutes, books=sorted_books,
        book_observation_epochs=observation_epochs,
        book_compaction="Exact unchanged consumed BBO/top-size/depth-aggregate/OI state compacted; original observation epochs retained separately. Full five-level column presence/hash recorded, unused per-level prices not copied.",
        first_source_book_epoch=first_book, first_two_sided_book_epoch=first_two_sided_book,
        first_source_book_was_two_sided=first_book_was_two_sided,
        first_source_book_in_span_epoch=first_book_in_span,last_source_book_before_formation_epoch=last_book_before_formation,
        first_book_rule="First observed original book row; two-sided requires finite positive top prices with bid<ask and positive top sizes. First-source-already-two-sided marks left-censoring. Event-time observation, not exchange publication proof; no wake threshold imposed.",
        units=dict(prices="cents",book_sizes="contracts",flow="signed contracts",trade_count="integer events",timestamps="epoch seconds",gap_std="seconds"),
        clock_provenance=clock_provenance(leg), source_manifest=manifests,
        source_verification="VERIFIED" if not unverified else "UNVERIFIED_SOURCES_EXCLUDED_FROM_MODEL",
        excluded_unverified_objects=sorted(unverified),
        availability=dict(original_trade_object=any("spaces:trades/" in x for x in objects),
            original_book_object=any("spaces:ticks/" in x for x in objects),
            oi="SOURCE_FIELDS_ONLY; absent remains STORE_SILENT", ws_depth="UNVERIFIED_SEQUENCE_INTEGRITY; no false zero",
            odds="NOT_IN_THIS_EXTRACT"), checks=verified,
        dedupe_removed={str(key):value for key,value in sorted(removed.items())})
    witnesses = dict(base, columns=["ts", "price", "size", "rowid", "src"],
        positive_prints=[[row[key] for key in ("ts", "price", "size", "rowid", "src")]
                         for row in sorted(accepted,key=lambda row:(row["ts"],row["rowid"])) if row["size"]>0])
    return panel, witnesses


def selected_legs(args):
    count=0
    with gzip.open(args.library,"rt") as source:
        for line in source:
            leg=json.loads(line)
            if leg["category"] not in args.categories:
                continue
            if args.limit_legs is not None and count>=args.limit_legs:
                break
            count+=1
            yield leg


def prepare_spool(args,cutter,receipt):
    """Short locked DB phase. Object I/O runs later against this sealed spool."""
    output=args.output_dir.resolve()
    destination=output/"PREPARED_SOURCES.sqlite"
    receipt_path=output/"SOURCE_SPOOL_RECEIPT.json"
    if destination.exists() or receipt_path.exists():
        raise ValueError("REFUSE_EXISTING_SOURCE_SPOOL")
    partial=output/("PREPARED_SOURCES."+str(os.getpid())+".partial.sqlite")
    args.out=destination
    args.expected_sha256=receipt["source_snapshot"]["sha256"]
    counts=Counter()
    with cutter.store_cut_lock(args) as (lock_state,record):
        db=args.db.resolve(strict=True)
        before=(db.stat().st_size,db.stat().st_mtime_ns)
        filed=receipt["source_snapshot"]
        if before!=(filed["bytes"],filed["mtime_ns"]):
            raise ValueError("SOURCE_STAT_DIFFERS_FROM_PINNED_LIBRARY")
        start_sha=end_sha=None
        if args.limit_legs is None:
            record(status="HASHING_STORE_START")
            print("HASHING_STORE_START",flush=True)
            start_sha=sha256_file(db)
            if start_sha!=args.expected_sha256:
                raise ValueError("SOURCE_SHA_DIFFERS_FROM_PINNED_LIBRARY")
            record(store_sha256=start_sha,store_sha256_start=start_sha)
        record(status="SPOOLING_ACCEPTED_ROWS_AND_ETAGS")
        with closing(cutter.open_snapshot(db,consolidated=True)) as source,closing(sqlite3.connect(partial)) as target:
            target.executescript("CREATE TABLE prints(rowid INTEGER PRIMARY KEY,event TEXT,ticker TEXT,ts REAL,price REAL,size REAL,src TEXT,src_role TEXT,obj TEXT); CREATE INDEX p_tk ON prints(ticker,ts); CREATE TABLE ingest_log(path TEXT PRIMARY KEY,etag TEXT); CREATE TABLE source_meta(ticker TEXT PRIMARY KEY,checks_json TEXT,dedupe_json TEXT);")
            for leg in selected_legs(args):
                if cutter.tune_named_event(leg["event_id"]):
                    raise ValueError("EXAM_EVENT_REFUSED")
                removed=Counter()
                rows=[dict(row) for row in cutter.accepted_print_rows(source,leg["ticker"],joined=leg.get("include_other_roles",False),
                    before=leg["bell_epoch"],after=leg["formation_end_epoch"],removed=removed)]
                if any(row["event"]!=leg["event_id"] or row.get("src_role")=="TUNE_SAMPLE"
                       or row["size"] is None or row["size"]<0 for row in rows):
                    raise ValueError("SOURCE_IDENTITY_ROLE_OR_SIZE_ERROR")
                rows.sort(key=lambda row:(math.floor(row["ts"]),row["rowid"]))
                checks=verify_library(leg,rows)
                keys=("rowid","event","ticker","ts","price","size","src","src_role","obj")
                target.executemany("INSERT INTO prints VALUES(?,?,?,?,?,?,?,?,?)",[tuple(row[key] for key in keys) for row in rows])
                refs={row.get("obj") for row in rows}
                refs.update(row.get("obj") for row in leg.get("cadence",{}).get("source_objects",[]))
                refs.update(leg.get("cadence",{}).get("objects_without_cadence",[]))
                for obj in sorted(ref for ref in refs if ref):
                    found=source.execute("SELECT etag FROM ingest_log WHERE path=?",(obj,)).fetchone()
                    target.execute("INSERT OR IGNORE INTO ingest_log VALUES(?,?)",(obj,found[0] if found else None))
                target.execute("INSERT INTO source_meta VALUES(?,?,?)",(leg["ticker"],json.dumps(checks,sort_keys=True),json.dumps({str(k):v for k,v in sorted(removed.items())},sort_keys=True)))
                target.commit()
                counts["legs"]+=1;counts[leg["category"]]+=1;counts["accepted_prints"]+=len(rows)
                counts["path_volume_points_checked"]+=checks["path_volume_points_checked"]
                print("SPOOL_PROGRESS "+json.dumps(dict(counts,last_ticker=leg["ticker"])),flush=True)
        if before!=(db.stat().st_size,db.stat().st_mtime_ns) or any(Path(str(db)+suffix).exists() for suffix in ("-wal","-journal")):
            raise ValueError("SOURCE_CHANGED_OR_JOURNAL_PRESENT")
        if not counts["legs"]:
            raise ValueError("NO_LIBRARY_LEGS_EXTRACTED")
        if args.limit_legs is None:
            record(status="HASHING_STORE_END");print("HASHING_STORE_END",flush=True)
            end_sha=sha256_file(db)
            if end_sha!=start_sha:
                raise ValueError("SOURCE_CHANGED_SHA")
            record(store_sha256_end=end_sha)
        result=dict(status="SEALED_PRIVATE_SOURCE_SPOOL",categories=args.categories,limit_legs=args.limit_legs,
            counts=dict(counts),library_sha256=sha256_file(args.library),cutter_sha256=sha256_file(args.cutter),
            extractor_sha256=sha256_file(Path(__file__)),
            source_store=dict(path=str(db),bytes=before[0],mtime_ns=before[1],sha256_start=start_sha,sha256_end=end_sha,
                full_hash_recomputed=args.limit_legs is None,sha256_from_library=args.expected_sha256),
            lock={**lock_state,"held_through_receipt_publication":True},
            output=dict(path=str(destination),sha256=sha256_file(partial),bytes=partial.stat().st_size),
            rule="Exact already-deduplicated accepted rows/rowids and original object ETags; no raw book objects read while lock held. Private spool is not committed. Smoke is stat-bound only; population has two full locked hashes.")
        partial.replace(destination)
        receipt_path.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
        print("SPOOL_VERIFIED "+json.dumps(result,sort_keys=True),flush=True)


def save_checkpoint(directory,leg,panel,witnesses,binding):
    directory.mkdir(exist_ok=True)
    key=hashlib.sha256(leg["ticker"].encode()).hexdigest()
    paths={kind:directory/(key+"."+kind+".json.gz") for kind in ("feature","witness")}
    marker=directory/(key+".ready.json")
    entries={}
    for kind,row in (("feature",panel),("witness",witnesses)):
        partial=paths[kind].with_suffix(".partial."+str(os.getpid()))
        with partial.open("xb") as raw,gzip.GzipFile(filename="",mode="wb",fileobj=raw,mtime=0) as zipped:
            zipped.write(json.dumps(row,sort_keys=True,separators=(",",":"),allow_nan=False).encode())
        entries[kind]=dict(path=paths[kind].name,sha256=sha256_file(partial))
        partial.replace(paths[kind])
    partial=marker.with_suffix(".partial."+str(os.getpid()))
    partial.write_text(json.dumps(dict(ticker=leg["ticker"],binding=binding,files=entries),sort_keys=True))
    partial.replace(marker)


def load_checkpoint(directory,leg,binding):
    key=hashlib.sha256(leg["ticker"].encode()).hexdigest()
    marker=directory/(key+".ready.json")
    if not marker.exists():
        return None
    proof=json.loads(marker.read_text())
    if proof["ticker"]!=leg["ticker"] or proof["binding"]!=binding:
        raise ValueError("CHECKPOINT_BINDING_CHANGED")
    output=[]
    for kind in ("feature","witness"):
        path=directory/proof["files"][kind]["path"]
        if path.parent!=directory or sha256_file(path)!=proof["files"][kind]["sha256"]:
            raise ValueError("CHECKPOINT_HASH_OR_PATH_ERROR")
        with gzip.open(path,"rt") as source:
            output.append(json.load(source))
    return output


def run_supplemental(args):
    """Read archived Foundation OI + odds availability, never an active DB.

    Narrow Arrow batches and a private on-disk SQLite index bound memory.
    Source schema/clock/hash are preserved; no odds price is exported here.
    """
    import pyarrow as pa
    import pyarrow.compute as pc
    import pyarrow.parquet as pq
    output = args.output_dir.resolve()
    destination = output / "SUPPLEMENTAL_AVAILABILITY.jsonl.gz"
    receipt_path = output / "SUPPLEMENTAL_AVAILABILITY_RECEIPT.json"
    index_path = output / "supplemental_private_index.sqlite"
    if any(path.exists() for path in (destination,receipt_path,index_path)):
        raise ValueError("REFUSE_EXISTING_SUPPLEMENTAL_OUTPUT")
    specs, pairs = {}, {}
    with gzip.open(args.library,"rt") as source:
        for line in source:
            leg=json.loads(line)
            if leg["category"] not in args.categories:
                continue
            if args.limit_legs is not None and len(specs)>=args.limit_legs:
                break
            spec={key:leg[key] for key in ("event_id","ticker","category","formation_end_epoch","bell_epoch")}
            specs[leg["ticker"]]=spec
            pair=pairs.setdefault(leg["event_id"],dict(formation=leg["formation_end_epoch"],bell=leg["bell_epoch"]))
            pair["formation"]=max(pair["formation"],leg["formation_end_epoch"])
            pair["bell"]=min(pair["bell"],leg["bell_epoch"])
    source_manifest=[]
    with closing(sqlite3.connect(index_path)) as index:
        index.execute("CREATE TABLE oi(ticker TEXT, epoch REAL, raw REAL, carry REAL, delta REAL, PRIMARY KEY(ticker,epoch))")
        index.execute("CREATE TABLE odds(event TEXT, epoch REAL, PRIMARY KEY(event,epoch))")
        if args.foundation:
            if not args.foundation_sha256 or sha256_file(args.foundation)!=args.foundation_sha256:
                raise ValueError("FOUNDATION_SHA_MISMATCH_OR_UNBOUND")
            before=(args.foundation.stat().st_size,args.foundation.stat().st_mtime_ns)
            pf=pq.ParquetFile(args.foundation)
            columns=["ticker","minute_ts","open_interest_at_minute_end","open_interest_ffill","open_interest_delta_from_prior_minute"]
            keys=pa.array(list(specs))
            scanned=matched=0
            for batch in pf.iter_batches(batch_size=32768,columns=columns):
                scanned+=batch.num_rows
                selected=batch.filter(pc.is_in(batch.column(0),value_set=keys))
                rows=[]
                for row in selected.to_pylist():
                    leg=specs[row["ticker"]];epoch=row["minute_ts"]
                    if leg["formation_end_epoch"]<=epoch<leg["bell_epoch"]:
                        rows.append((row["ticker"],epoch,finite(row[columns[2]]),finite(row[columns[3]]),finite(row[columns[4]])))
                index.executemany("INSERT INTO oi VALUES(?,?,?,?,?)",rows)
                matched+=len(rows)
            index.commit()
            if before!=(args.foundation.stat().st_size,args.foundation.stat().st_mtime_ns):
                raise ValueError("FOUNDATION_CHANGED")
            source_manifest.append(dict(kind="FOUNDATION_OI",path=str(args.foundation),sha256=args.foundation_sha256,
                bytes=before[0],source_rows=scanned,matched_rows=matched,columns=columns,
                availability="minute_ts is closed-minute epoch; no earlier publication implied"))
        if args.odds_dir:
            if not args.odds_receipt:
                raise ValueError("ODDS_RECEIPT_REQUIRED")
            filed=json.loads(args.odds_receipt.read_text())
            bindings={Path(row["path"]).name:row for row in filed["archive_files"]}
            keys=pa.array(list(pairs))
            lower=pa.array([datetime.fromtimestamp(pair["formation"],ET).strftime("%Y-%m-%d %H:%M:%S") for pair in pairs.values()])
            upper=pa.array([datetime.fromtimestamp(pair["bell"],ET).strftime("%Y-%m-%d %H:%M:%S") for pair in pairs.values()])
            for name,binding in sorted(bindings.items()):
                path=args.odds_dir/name
                if sha256_file(path)!=binding["sha256"]:
                    raise ValueError("ODDS_ARCHIVE_SHA_MISMATCH:"+name)
                before=(path.stat().st_size,path.stat().st_mtime_ns)
                pf=pq.ParquetFile(path);scanned=matched=0
                for batch in pf.iter_batches(batch_size=32768,columns=["event_ticker","polled_at"]):
                    scanned+=batch.num_rows
                    ids=pc.index_in(batch.column(0),value_set=keys)
                    mask=pc.and_(pc.greater_equal(batch.column(1),pc.take(lower,ids)),pc.less(batch.column(1),pc.take(upper,ids)))
                    selected=batch.filter(pc.fill_null(mask,False))
                    unique={(row["event_ticker"],datetime.fromisoformat(row["polled_at"]).replace(tzinfo=ET).timestamp()) for row in selected.to_pylist()}
                    index.executemany("INSERT OR IGNORE INTO odds VALUES(?,?)",sorted(unique))
                    matched+=selected.num_rows
                index.commit()
                if before!=(path.stat().st_size,path.stat().st_mtime_ns):
                    raise ValueError("ODDS_ARCHIVE_CHANGED:"+name)
                source_manifest.append(dict(kind="ODDS_POLL_AVAILABILITY",path=str(path),sha256=binding["sha256"],
                    bytes=before[0],source_rows=scanned,matched_source_rows=matched,
                    columns=["event_ticker","polled_at"],clock="polled_at fixed UTC-04, writer clock; no odds values exported"))
                print("SUPPLEMENTAL_PROGRESS "+json.dumps(source_manifest[-1]),flush=True)
        counts=Counter()
        partial=destination.with_suffix(".gz.partial")
        with partial.open("xb") as raw,gzip.GzipFile(filename="",mode="wb",fileobj=raw,mtime=0) as zipped:
            for ticker,leg in specs.items():
                oi=[list(row) for row in index.execute("SELECT epoch,raw,carry,delta FROM oi WHERE ticker=? ORDER BY epoch",(ticker,))]
                odds=[row[0] for row in index.execute("SELECT epoch FROM odds WHERE event=? ORDER BY epoch",(leg["event_id"],))]
                row=dict(leg,schema="FEATURE_SUPPLEMENTAL_AVAILABILITY_V1",
                    oi_columns=["available_epoch","open_interest_at_minute_end","open_interest_ffill","open_interest_delta_from_prior_minute"],
                    oi=oi,oi_status="SOURCE_ROWS; NULL VALUES PRESERVED" if oi else "STORE_SILENT: no Foundation rows in span",
                    odds_poll_epochs=odds,odds_status="EXACT_EVENT_IN_SPAN_ARCHIVE_POLLS" if odds else ("NO_EXACT_EVENT_POLLS_IN_BOUND_ARCHIVES" if args.odds_dir else "NOT_EXTRACTED"),
                    odds_span=pairs[leg["event_id"]],ws_depth_status="UNVERIFIED_SEQUENCE_INTEGRITY; no false zero")
                zipped.write((json.dumps(row,sort_keys=True,separators=(",",":"),allow_nan=False)+"\n").encode())
                counts["legs"]+=1;counts["oi_rows"]+=len(oi);counts["odds_leg_poll_epochs"]+=len(odds)
                counts["legs_with_finite_oi"]+=any(any(value is not None for value in item[1:]) for item in oi)
                counts["legs_with_odds"]+=bool(odds)
        result=dict(status="VERIFIED",schema="FEATURE_SUPPLEMENTAL_AVAILABILITY_V1",counts=dict(counts),
            library_sha256=sha256_file(args.library),extractor_sha256=sha256_file(Path(__file__)),
            sources=source_manifest,limit_legs=args.limit_legs,
            output=dict(path=str(destination),sha256=sha256_file(partial),bytes=partial.stat().st_size),
            rule="Features only; source stores immutable/read-only; local private index only. Never use a first/last range as proof of intermediate snapshots. Null is not zero. WS not licensed until seeded gap-free epochs are verified.")
        partial.replace(destination)
        receipt_path.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
        print("SUPPLEMENTAL_VERIFIED "+json.dumps(result,sort_keys=True),flush=True)


def run(args):
    output = args.output_dir.resolve()
    if output != REMOTE_ROOT and REMOTE_ROOT not in output.parents:
        raise ValueError("OUTPUT_OUTSIDE_AUTHORIZED_FEATURE_DIRECTORY")
    if os.name != "posix" or os.getpriority(os.PRIO_PROCESS, 0) < 10:
        raise ValueError("REQUIRES_DROPLET_NICE_10")
    if args.limit_legs is not None and args.limit_legs <= 0:
        raise ValueError("LIMIT_LEGS_MUST_BE_POSITIVE")
    receipt = json.loads(args.library_receipt.read_text())
    if sha256_file(args.library) != receipt["output"]["sha256"]:
        raise ValueError("LIBRARY_SHA_MISMATCH")
    if sha256_file(args.cutter) != receipt["builder"]["sha256"]:
        raise ValueError("PINNED_CUTTER_SHA_MISMATCH")
    output.mkdir(parents=True, exist_ok=True)
    if args.supplemental_only:
        return run_supplemental(args)
    spec = importlib.util.spec_from_file_location("pinned_cutter", args.cutter)
    cutter = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cutter)
    if args.prepare_only:
        return prepare_spool(args,cutter,receipt)
    output.mkdir(parents=True, exist_ok=True)
    paths = {name: output/name for name in ("FEATURE_SOURCES.jsonl.gz", "POSITIVE_PRINT_WITNESSES.jsonl.gz", "FEATURE_EXTRACT_RECEIPT.json")}
    if any(path.exists() for path in paths.values()):
        raise ValueError("REFUSE_EXISTING_OUTPUT")
    args.out = paths["FEATURE_SOURCES.jsonl.gz"]  # cutter lock audit location
    args.expected_sha256 = receipt["source_snapshot"]["sha256"]
    counts, source_fields = Counter(), Counter()
    started = time.monotonic()
    env = SpacesClient(spaces_environment(args.repo_root))
    spool=None
    if args.source_spool:
        spool=json.loads((args.source_spool.parent/"SOURCE_SPOOL_RECEIPT.json").read_text())
        if spool["status"]!="SEALED_PRIVATE_SOURCE_SPOOL" or sha256_file(args.source_spool)!=spool["output"]["sha256"]:
            raise ValueError("SOURCE_SPOOL_NOT_SEALED_OR_HASH_MISMATCH")
        if spool["library_sha256"]!=sha256_file(args.library) or spool["cutter_sha256"]!=sha256_file(args.cutter):
            raise ValueError("SOURCE_SPOOL_LIBRARY_OR_CUTTER_MISMATCH")
        if not set(args.categories)<=set(spool["categories"]) or (args.limit_legs is None and spool["limit_legs"] is not None):
            raise ValueError("SOURCE_SPOOL_SCOPE_MISMATCH")
    lock_context=(nullcontext((dict(lock_held=False,status="SEALED_PRIVATE_SPOOL; original writer lock already released"),lambda **kw:None))
                  if spool else cutter.store_cut_lock(args))
    part_directory=output/"parts"
    binding=dict(library_sha256=sha256_file(args.library),extractor_sha256=sha256_file(Path(__file__)),
                 source_spool_sha256=spool["output"]["sha256"] if spool else None)
    partials={name:path.with_suffix(".gz.partial."+str(os.getpid())) for name,path in paths.items() if name.endswith(".gz")}
    with lock_context as (lock_state, record):
        db = (args.source_spool or args.db).resolve(strict=True)
        before = (db.stat().st_size, db.stat().st_mtime_ns)
        filed = receipt["source_snapshot"]
        if not spool and before != (filed["bytes"], filed["mtime_ns"]):
            raise ValueError("SOURCE_STAT_DIFFERS_FROM_PINNED_LIBRARY")
        store_sha_start = store_sha_end = None
        if args.limit_legs is None and not spool:
            record(status="HASHING_STORE_START")
            print("HASHING_STORE_START",flush=True)
            store_sha_start=sha256_file(db)
            if store_sha_start!=args.expected_sha256:
                raise ValueError("SOURCE_SHA_DIFFERS_FROM_PINNED_LIBRARY")
            record(store_sha256=store_sha_start,store_sha256_start=store_sha_start)
        record(status="EXTRACTING_FEATURE_SOURCES")
        with closing(cutter.open_snapshot(db, consolidated=True)) as connection, ExitStack() as stack:
            writers = {}
            for name in ("FEATURE_SOURCES.jsonl.gz", "POSITIVE_PRINT_WITNESSES.jsonl.gz"):
                raw = stack.enter_context(partials[name].open("xb"))
                writers[name] = stack.enter_context(gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0))
            with gzip.open(args.library,"rt") as source:
                for line in source:
                    leg = json.loads(line)
                    if leg["category"] not in args.categories:
                        continue
                    if args.limit_legs is not None and counts["legs"] >= args.limit_legs:
                        break
                    cached=load_checkpoint(part_directory,leg,binding) if args.resume else None
                    if cached:
                        panel,witnesses=cached
                        counts["resumed_legs"]+=1
                    else:
                        panel, witnesses = extract_leg(connection, leg, cutter, env)
                        if spool:
                            original=connection.execute("SELECT checks_json,dedupe_json FROM source_meta WHERE ticker=?",(leg["ticker"],)).fetchone()
                            if original is None or json.loads(original[0])!=panel["checks"]:
                                raise ValueError("PRIVATE_SPOOL_CHECKS_CHANGED")
                            panel["dedupe_removed"]=json.loads(original[1])
                        save_checkpoint(part_directory,leg,panel,witnesses,binding)
                    for name, row in (("FEATURE_SOURCES.jsonl.gz",panel),("POSITIVE_PRINT_WITNESSES.jsonl.gz",witnesses)):
                        writers[name].write((json.dumps(row,sort_keys=True,separators=(",",":"),allow_nan=False)+"\n").encode())
                    counts["legs"] += 1
                    counts[leg["category"]] += 1
                    counts["minute_rows"] += len(panel["minute_features"])
                    counts["book_rows"] += len(panel["books"])
                    counts["positive_prints"] += len(witnesses["positive_prints"])
                    counts["accepted_prints"] += panel["checks"]["accepted_count"]
                    counts["path_volume_points_checked"] += panel["checks"]["path_volume_points_checked"]
                    counts["unverified_source_objects_excluded"]+=len(panel["excluded_unverified_objects"])
                    for obj in panel["source_manifest"]:
                        source_fields.update(obj["columns"])
                    print("PROGRESS "+json.dumps(dict(counts,last_ticker=leg["ticker"],elapsed_seconds=time.monotonic()-started)),flush=True)
        if before != (db.stat().st_size,db.stat().st_mtime_ns) or any(Path(str(db)+suffix).exists() for suffix in ("-wal","-journal")):
            raise ValueError("SOURCE_CHANGED_OR_JOURNAL_PRESENT")
        if not counts["legs"]:
            raise ValueError("NO_LIBRARY_LEGS_EXTRACTED")
        if args.limit_legs is None and not spool:
            record(status="HASHING_STORE_END")
            print("HASHING_STORE_END",flush=True)
            store_sha_end=sha256_file(db)
            if store_sha_end!=store_sha_start:
                raise ValueError("SOURCE_CHANGED_SHA")
            record(store_sha256_end=store_sha_end)
        result = dict(schema=SCHEMA,status="VERIFIED" if not counts["unverified_source_objects_excluded"] else "VERIFIED_WITH_UNVERIFIED_SOURCES_EXCLUDED",categories=args.categories,limit_legs=args.limit_legs,
            counts=dict(counts),source_columns_seen=dict(source_fields),
            library_sha256=sha256_file(args.library),library_receipt_sha256=sha256_file(args.library_receipt),
            cutter_sha256=sha256_file(args.cutter),extractor_sha256=sha256_file(Path(__file__)),
            source_store=dict(path=str(db),bytes=before[0],mtime_ns=before[1],
                source_kind="SEALED_PRIVATE_SPOOL" if spool else "CONSOLIDATED_STORE",
                private_spool_sha256=spool["output"]["sha256"] if spool else None,
                original_store_sha256_from_library=args.expected_sha256,
                full_hash_recomputed=args.limit_legs is None and not spool,sha256_start=store_sha_start,sha256_end=store_sha_end,
                validation=("Private spool SHA verified; original two locked store hashes are in source_spool.source_store; original writer lock released before objects" if spool else
                    "Full population: two full store hashes under shared writer lock; smoke: pinned stat only. Both: no journals, every extracted path volume and final accepted count reproduced")),
            source_spool=spool,checkpoint_binding=binding,
            lock={**lock_state,"held_through_receipt_publication":not bool(spool)},
            rules=dict(dedupe=cutter.DEDUPE_POLICY,span="Exact filed library spans; no rederivation",
                minute="Completed half-open minute windows; first window clipped at formation; no at/after-bell close",
                flow="Positive-size contract sums by stored surviving aggressor; incomplete aggressors -> null, never inferred",
                prices="Positive-size accepted prints only for minute min/max/breadth/clustering and fill witnesses",
                count="Original library accepted integer count includes zero-size, separately from positive-size count",
                clocks="Spaces ET second is source-recorded clock; no receipt timestamp fabricated",
                books="Original BBO/top sizes/depth aggregates, last source row per second; exact unchanged feature state compacted, all observation epochs retained; latest preformation seed carried causally",
                missing="No missing OI/taker/depth/odds/wake publication is filled with a neutral or zero value"),outputs={})
        for name in ("FEATURE_SOURCES.jsonl.gz","POSITIVE_PRINT_WITNESSES.jsonl.gz"):
            partial=partials[name]
            result["outputs"][name]=dict(sha256=sha256_file(partial),bytes=partial.stat().st_size,path=str(paths[name]))
            partial.replace(paths[name])
        paths["FEATURE_EXTRACT_RECEIPT.json"].write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
        print("VERIFIED "+json.dumps(result,sort_keys=True),flush=True)


def parser():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ("db","cutter","library","library-receipt","repo-root","store-lock","output-dir"):
        p.add_argument("--"+name,type=Path,required=True)
    p.add_argument("--categories",nargs="+",choices=("ATP_MAIN","ATP_CHALL"),default=["ATP_MAIN","ATP_CHALL"])
    p.add_argument("--limit-legs",type=int,help="Explicit extraction smoke test; never represented as the population")
    p.add_argument("--prepare-only",action="store_true",help="Under shared lock/hash, seal exact accepted print rows and object ETags; no object reads")
    p.add_argument("--source-spool",type=Path,help="Read sealed PREPARED_SOURCES.sqlite instead of reopening live store; no writer lock held during object parsing")
    p.add_argument("--resume",action="store_true",help="Reuse per-leg checkpoints after hashes and exact script/library/spool binding checks")
    p.add_argument("--supplemental-only",action="store_true",help="Column-pruned immutable Foundation OI and archived odds polling times; no live DB opened")
    p.add_argument("--foundation",type=Path)
    p.add_argument("--foundation-sha256")
    p.add_argument("--odds-dir",type=Path)
    p.add_argument("--odds-receipt",type=Path,help="Pinned read-only audit receipt listing monthly archive hashes")
    return p


if __name__ == "__main__":
    run(parser().parse_args())
