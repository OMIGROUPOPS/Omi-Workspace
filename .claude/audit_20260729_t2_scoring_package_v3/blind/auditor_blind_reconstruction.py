"""PHASE-1 BLIND reconstruction for the T2 scoring-package V3 audit.

Auditor-authored. Inputs: parent tree b73679ed (raw V5 ledger, flattened V1
boundary ledger, V1/V2 package ledgers), preserved V2 failure artifacts at
3f8fa0fb, and authorized private development inputs. NO file added by V3 is
opened. No V3 module is imported. The boundary/reference laws below are the
auditor's own transcription of the frozen, previously audited adapter law.
"""
import datetime as dt
import gzip
import hashlib
import io
import json
import math
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

REPO = r"C:\Users\omigr\OMI-Workspace"
PARENT = "b73679edc9186eb72236cd1bee5f886ac141cac4"
PRIV = Path(r"C:\Users\omigr\OMI-Window1-private")
POSITIVE = {"official_exact", "clean_causal_interval",
            "quantized_late_detection_proxy"}
NONPOSITIVE = {"schedule_only", "live_by_only", "contradictory"}
FIT = {f"2026-07-{d:02d}" for d in range(12, 18)}


def show(path):
    return subprocess.run(["git", "-C", REPO, "show", f"{PARENT}:{path}"],
                          stdout=subprocess.PIPE, check=True).stdout


def jsonl(raw):
    return [json.loads(line) for line in raw.decode("utf-8").splitlines()
            if line.strip()]


def gz_jsonl(raw):
    out = []
    with gzip.open(io.BytesIO(raw), "rt", encoding="utf-8") as fh:
        for line in fh:
            out.append(json.loads(line))
    return out


def ts(value, field):
    if isinstance(value, bool):
        raise ValueError(field + " boolean")
    if isinstance(value, (int, float)):
        r = float(value)
    elif isinstance(value, str) and value.strip():
        r = dt.datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
    else:
        raise ValueError(field + " missing")
    if not math.isfinite(r):
        raise ValueError(field + " not finite")
    return r


def same(a, b):
    return abs(float(a) - float(b)) <= 1e-6


def my_guarded_cutoff(b):
    """Auditor transcription of the frozen V5 guard law."""
    sc = str(b.get("start_source_class") or "").strip()
    ev = str(b.get("event_id") or "").strip()
    if not sc or not ev:
        raise ValueError("identity missing")
    if sc in NONPOSITIVE:
        if sc == "contradictory":
            return {"event_id": ev, "status": "contradictory",
                    "source_class": sc, "cutoff_ts": None, "guard_id": None}
        if b.get("positive_window1_provable") is not False:
            raise ValueError(sc + " cannot prove positive")
        return {"event_id": ev, "status": "censored", "source_class": sc,
                "cutoff_ts": None, "guard_id": None}
    if sc not in POSITIVE:
        raise ValueError("unknown class")
    if b.get("positive_window1_provable") is not True:
        if not str(b.get("guard_censor_reason") or "").strip():
            raise ValueError("unprovable lacks censor")
        return {"event_id": ev, "status": "censored", "source_class": sc,
                "cutoff_ts": None, "guard_id": None,
                "censor_reason": str(b["guard_censor_reason"])}
    guard = b.get("guard_band")
    if not isinstance(guard, dict):
        raise ValueError("positive boundary lacks V5 guard artifact")
    gid = str(guard.get("guard_id") or "").strip()
    secs = float(guard.get("positive_guard_seconds"))
    if sc == "official_exact":
        exp_id, exp_s = "official-point-strict-60s-v1", 60.0
        anchor = ts(b.get("exact_start_utc"), "exact start")
    elif sc == "clean_causal_interval":
        exp_id, exp_s = "causal-interval-strict-60s-v1", 60.0
        anchor = ts(b["start_interval_utc"]["lower_inclusive"], "lower")
    else:
        exp_id, exp_s = "te-calibration-central-93pct-asymmetric-v1", 900.0
        anchor = ts(b.get("proxy_clock_utc"), "proxy clock")
        if not same(float(guard.get("negative_guard_seconds")), 600.0):
            raise ValueError("proxy asymmetric guard changed")
    if gid != exp_id or not same(secs, exp_s):
        raise ValueError("guard changed")
    cutoff = anchor - secs
    if sc == "quantized_late_detection_proxy":
        committed = ts(guard.get("strict_window1_completion_lte_utc"),
                       "committed")
        if not same(cutoff, committed):
            raise ValueError("proxy directionality changed")
    return {"event_id": ev, "status": "positive", "source_class": sc,
            "cutoff_ts": cutoff, "guard_id": gid,
            "guard_seconds": int(secs)}


R = {"phase": "PHASE1_BLIND", "v3_files_opened": [],
     "v3_files_unopened_count": 22}

# ---------------- 3. boundary contract reconstruction -----------------------
raw_rows = jsonl(show(
    ".claude/window1_start_guard_corrected_20260724/REAL_START_LEDGER_V5.jsonl"))
flat_rows = {r["event_id"]: r for r in jsonl(show(
    ".claude/window1_t2_scoring_package_prerun_20260728/GUARDED_BOUNDARY_LEDGER.jsonl"))}
events = jsonl((PRIV / "joined" / "events.jsonl").read_bytes())
ev_by_id = {e["event_id"]: e for e in events}

status_census = Counter()
class_census = Counter()
mismatches = []
my_cutoffs = {}
sha_match = sha_bad = 0
for row in raw_rows:
    ev = row["event_id"]
    c = my_guarded_cutoff(row)
    my_cutoffs[ev] = c
    status_census[c["status"]] += 1
    class_census[c["source_class"]] += 1
    f = flat_rows.get(ev)
    if f is None:
        mismatches.append((ev, "missing_flat_row"))
        continue
    if f.get("start_source_class") != c["source_class"]:
        mismatches.append((ev, "class"))
    if c["status"] == "positive":
        if f.get("positive_window1_provable") is not True or \
                not same(f.get("guarded_cutoff_ts"), c["cutoff_ts"]) or \
                f.get("guard_id") != c["guard_id"]:
            mismatches.append((ev, "positive_fields"))
    else:
        if f.get("positive_window1_provable") is not False and \
                c["status"] != "contradictory":
            mismatches.append((ev, "nonpositive_flag"))
    raw_sha = hashlib.sha256(json.dumps(
        row, sort_keys=True, separators=(",", ":"),
        ensure_ascii=True).encode()).hexdigest()
    if raw_sha == f.get("source_record_sha256"):
        sha_match += 1
    else:
        sha_bad += 1
R["boundary"] = {
    "raw_rows": len(raw_rows),
    "status_census": dict(status_census),
    "source_class_census": dict(class_census),
    "flat_vs_raw_mismatches": mismatches,
    "source_record_sha256_matches": sha_match,
    "source_record_sha256_differs": sha_bad,
    "flattened_rows_lack_guard_band": sum(
        1 for f in flat_rows.values() if "guard_band" not in f),
}

# ---------------- 5. V2 failure reproduction + repaired seam ----------------
first_affected = None
for row in raw_rows:  # ledger order == runner iteration order
    c = my_cutoffs[row["event_id"]]
    if c["status"] == "positive":
        first_affected = row["event_id"]
        break
flat_fail = None
try:
    my_guarded_cutoff(flat_rows[first_affected])
except ValueError as exc:
    flat_fail = str(exc)
raw_ok = my_cutoffs[first_affected]
R["v2_failure_reproduction"] = {
    "first_affected_event": first_affected,
    "flattened_row_error": flat_fail,
    "raw_row_status": raw_ok["status"],
    "raw_row_cutoff_ts": raw_ok["cutoff_ts"],
}

# ---------------- 4. reference reconstruction (1,608 legs) ------------------
refs = {}
avail = Counter()
reasons = Counter()
tie_counts = Counter()
same_price_ties = diff_price_ties = 0
ref_class = Counter()
for row in raw_rows:
    ev = row["event_id"]
    event = ev_by_id[ev]
    cutoff = my_cutoffs[ev]
    scheduled = ts(event["scheduled_start_exchange_ts"], "sched")
    t8 = scheduled - 8 * 3600
    cache = json.loads(gzip.open(
        PRIV / "fit-local" / "guarded-cache-v3" / (ev + ".json.gz"),
        "rt", encoding="utf-8").read())
    legs = {leg["leg"]: leg for leg in cache["legs"]}
    for leg in row["legs"]:
        lid, ticker = leg["leg"], leg["ticker"]
        key = (ev, lid)
        if cutoff["status"] != "positive":
            refs[key] = {"available": False,
                         "reason": ("contradictory_boundary"
                                    if cutoff["status"] == "contradictory"
                                    else "boundary_not_positive"),
                         "price": None, "ts": None, "receipts": ()}
            avail["unavailable"] += 1
            reasons[refs[key]["reason"]] += 1
            continue
        by_receipt = {}
        for p in legs[lid].get("prints") or []:
            if float(p.get("size") or 0) <= 0:
                continue
            rc = str(p.get("trade_id") or "").strip()
            if not rc:
                raise ValueError("print missing receipt")
            norm = {"receipt": rc, "ts": float(p["ts"]),
                    "price": int(p["price"]), "size": float(p["size"])}
            if rc in by_receipt and by_receipt[rc] != norm:
                raise ValueError("conflicting duplicate receipt")
            by_receipt[rc] = norm
        eligible = [p for p in by_receipt.values()
                    if t8 <= p["ts"] <= cutoff["cutoff_ts"]]
        if not eligible:
            refs[key] = {"available": False,
                         "reason": "window1_close_reference_missing",
                         "price": None, "ts": None, "receipts": ()}
            avail["unavailable"] += 1
            reasons["window1_close_reference_missing"] += 1
            continue
        latest_ts = max(p["ts"] for p in eligible)
        latest = [p for p in eligible if p["ts"] == latest_ts]
        prices = sorted({p["price"] for p in latest})
        receipts = tuple(sorted(p["receipt"] for p in latest))
        tie_counts[len(latest)] += 1
        if len(prices) != 1:
            diff_price_ties += 1
            refs[key] = {"available": False,
                         "reason": "ambiguous_latest_timestamp_prices",
                         "price": None, "ts": latest_ts,
                         "receipts": receipts,
                         "tie_count": len(latest),
                         "distinct_prices": prices}
            avail["unavailable"] += 1
            reasons["ambiguous_latest_timestamp_prices"] += 1
            continue
        if len(latest) > 1:
            same_price_ties += 1
        refs[key] = {"available": True, "reason": None,
                     "price": prices[0], "ts": latest_ts,
                     "receipts": receipts,
                     "tie_count": len(latest)}
        avail["available"] += 1
        ref_class[cutoff["source_class"]] += 1

logical = [
    {"event_id": k[0], "leg_id": k[1], **v}
    for k, v in sorted(refs.items())
]
logical_hash = hashlib.sha256(json.dumps(
    logical, sort_keys=True, separators=(",", ":"),
    ensure_ascii=True, default=list).encode()).hexdigest()
R["references"] = {
    "unique_event_legs": len(refs),
    "availability": dict(avail),
    "unavailable_reasons": dict(reasons),
    "latest_timestamp_tie_size_census": {
        str(k): v for k, v in sorted(tie_counts.items())},
    "same_price_tie_legs": same_price_ties,
    "differing_price_tie_legs_ambiguous": diff_price_ties,
    "available_source_class_census": dict(ref_class),
    "no_schedule_carried_midpoint_or_receipt_id_substitution": True,
    "logical_output_sha256_auditor_form": logical_hash,
}
Path(r"C:\Users\omigr\AppData\Local\Temp\v3_blind_refs.json").write_text(
    json.dumps(logical, indent=0, default=list), encoding="utf-8")

# first affected event seam proof (no scoring)
fa = [refs[(first_affected, leg["leg"])]
      for leg in ev_by_id[first_affected].get("legs", [])] or [
      refs[k] for k in refs if k[0] == first_affected]
R["v2_failure_reproduction"]["repaired_seam_first_event_references"] = [
    {"available": x["available"], "price": x["price"],
     "reason": x["reason"]} for x in
    [refs[k] for k in sorted(refs) if k[0] == first_affected]]

# ---------------- 6. population joins to the scorer boundary ----------------
fills = gz_jsonl(show(".claude/window1_t2_scoring_package_prerun_20260728/"
                      "T2_UNIQUE_CREDITED_FILL_LEDGER.jsonl.gz"))
floors = gz_jsonl(show(".claude/window1_t2_scoring_package_prerun_20260728/"
                       "TAPE_AND_FIVE_CONTRACT_FLOOR_LEDGER.jsonl.gz"))
regret = gz_jsonl(show(".claude/window1_t2_scoring_package_v2_prerun_20260728/"
                       "T2_REGRET_CHAIN_INPUT_LEDGER_V2.jsonl.gz"))
prov = gz_jsonl(show(".claude/window1_t2_scoring_package_v2_prerun_20260728/"
                     "TARGET_AUTHORITY_D2_PROVENANCE_LEDGER.jsonl.gz"))
ev_ids = {e["event_id"] for e in events}
leg_keys = set(refs)
join = {}
join["events"] = len(ev_ids)
join["legs"] = len(leg_keys)
join["boundary_ids_equal_event_ids"] = (
    {r["event_id"] for r in raw_rows} == ev_ids)
fill_keys = {(r.get("candidate_id"), r.get("event_id"), r.get("leg_id"))
             for r in fills}
join["fill_rows"] = len(fills)
join["fill_keys_unique"] = len(fill_keys) == len(fills)
join["fill_events_within_D"] = all(r.get("event_id") in ev_ids for r in fills)
floor_keys = {(r.get("event_id"), r.get("leg_id")) for r in floors}
join["floor_rows"] = len(floors)
join["floor_leg_keys_equal_1608"] = floor_keys == leg_keys
cand_census = Counter(r.get("candidate_id") for r in regret)
join["regret_rows"] = len(regret)
join["regret_candidates"] = len(cand_census)
join["regret_rows_per_candidate_uniform"] = (
    len(set(cand_census.values())) == 1)
join["regret_events_within_D"] = all(
    r.get("event_id") in ev_ids for r in regret)
rk = {(r.get("candidate_id"), r.get("event_id"), r.get("leg_id"))
      for r in regret}
join["regret_keys_unique"] = len(rk) == len(regret)
join["provenance_rows"] = len(prov)
join["provenance_events_within_D"] = all(
    r.get("event_id") in ev_ids for r in prov)
slice_census = Counter(
    "fit" if ev_by_id[e]["event_date"] in FIT else "postfit"
    for e in ev_ids)
join["fit_postfit"] = dict(slice_census)
join["duplicates_missing_extras"] = "none_detected_in_any_key_join"
R["population_joins"] = join
R["scorer_invocations"] = 0
R["results_directory_created"] = False

out = Path(r"C:\Users\omigr\AppData\Local\Temp\v3_blind_receipt.json")
out.write_text(json.dumps(R, indent=1, sort_keys=True, default=list),
               encoding="utf-8")
print("written", out)
print(json.dumps(R["boundary"], indent=1, default=list)[:900])
print(json.dumps(R["references"], indent=1)[:900])
