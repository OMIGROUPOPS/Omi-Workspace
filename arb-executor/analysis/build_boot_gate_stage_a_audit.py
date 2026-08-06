#!/usr/bin/env python3
"""Freeze the read-only Stage-A live_v4 restart-inheritance audit."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess


REMOTE = r'''
import asyncio, hashlib, json, os, pathlib, subprocess, sys, time
from datetime import datetime, timezone

ROOT = pathlib.Path("/root/Omi-Workspace")
EXEC = ROOT / "arb-executor"
sys.path.insert(0, str(EXEC))
os.chdir(EXEC)
import aiohttp
import live_v4 as live

STOP_EXIT_IDS = [
 "6bec4578-1734-400e-8ac7-5e33b427237f","9a6abeba-30a1-4055-9eec-5f6a578482b5","ecdbadcf-3adb-49f7-a056-935202db69f0","44d5d17a-82bb-47ee-a7bb-b33d1ae580df","e3ec9eef-8eaf-4ea6-8ad1-0b04c7ce339f","00c9192a-1765-4d14-b318-2a834a710a32","382c3f18-15fe-4cfe-9853-a631b0c2a58a","976efc10-3db3-451f-8c75-a1459eeb7d7b","e23b06a0-ad25-4b10-8710-bd825a53fefb","9e2b2a07-b7e8-41af-8e5b-f0473ae0bb8e","a97b7c4e-a582-45da-80ec-46ce8aeb8f90","f3f96bb0-2043-4e70-b25f-28bcac9d6cfb"
]

def run(*args, check=True):
    p = subprocess.run(args, text=True, capture_output=True)
    if check and p.returncode: raise RuntimeError("command_failed:%r:%s" % (args, p.stderr))
    return {"exit_code": p.returncode, "stdout": p.stdout, "stderr": p.stderr}

def sha(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()

def ident(path):
    p=pathlib.Path(path)
    return {"path":str(p),"exists":p.exists(),"bytes":p.stat().st_size if p.exists() else None,"sha256":sha(p) if p.is_file() else None,"mtime_epoch":p.stat().st_mtime if p.exists() else None}

def qty(row):
    for k in ("remaining_count_fp","remaining_count","count_fp","count"):
        if row.get(k) not in (None,""): return float(row[k])
    return 0.0

def price(row):
    for k in ("yes_price_dollars","price","yes_price"):
        if row.get(k) not in (None,""):
            x=float(row[k]); return int(round(x*100)) if x < 2 else int(round(x))
    return None

async def all_pages(session, ak, pk, rl, endpoint, collection):
    rows=[]; cursor=None; seen=set(); pages=[]
    while True:
        full=endpoint + (("&" if "?" in endpoint else "?")+"cursor="+cursor if cursor else "")
        data=await live.api_get(session,ak,pk,full,rl)
        if not isinstance(data,dict) or not isinstance(data.get(collection),list): raise RuntimeError("bad_page:"+collection)
        pages.append({"page":len(pages)+1,"rows":len(data[collection]),"cursor_in":cursor,"cursor_out_present":bool(data.get("cursor"))})
        rows.extend(data[collection]); nxt=data.get("cursor") or None
        if not nxt: break
        if nxt in seen or len(pages)>=100: raise RuntimeError("pagination_fail:"+collection)
        seen.add(nxt); cursor=nxt
    return rows,pages

async def main():
    now=datetime.now(timezone.utc).isoformat().replace("+00:00","Z")
    head=run("git","-C",str(ROOT),"rev-parse","HEAD")["stdout"].strip()
    branch=run("git","-C",str(ROOT),"rev-parse","--abbrev-ref","HEAD")["stdout"].strip()
    status=run("git","-C",str(ROOT),"status","--porcelain=v1","-uall")["stdout"].splitlines()
    live_path=EXEC/"live_v4.py"; config=EXEC/"config/deploy_v5_live.json"
    blob=run("git","-C",str(ROOT),"hash-object","arb-executor/live_v4.py")["stdout"].strip()
    head_blob=run("git","-C",str(ROOT),"rev-parse","HEAD:arb-executor/live_v4.py")["stdout"].strip()
    live_numstat=run("git","-C",str(ROOT),"diff","--numstat","--","arb-executor/live_v4.py")["stdout"].strip()
    cr=run("crontab","-l",check=False)["stdout"]
    cron_lines=cr.splitlines()
    process_text=run("ps","-eo","pid=,ppid=,lstart=,etime=,args=")["stdout"]
    relevant=[x for x in process_text.splitlines() if any(k in x.lower() for k in ("live_v4.py","premarket","recorder","capture_book","ws_depth","gun_ws","keepalive")) and "python3 -" not in x]
    tmux=run("tmux","list-sessions",check=False)
    disk=[]
    for target in ("/","/root/Omi-Workspace","/root/Omi-Workspace/arb-executor/analysis/premarket_ticks","/tmp"):
        st=os.statvfs(target); disk.append({"path":target,"bytes_total":st.f_blocks*st.f_frsize,"bytes_free":st.f_bavail*st.f_frsize,"bytes_used":(st.f_blocks-st.f_bfree)*st.f_frsize,"inodes_total":st.f_files,"inodes_free":st.f_favail})
    tape_root=EXEC/"analysis/premarket_ticks"
    tape_files=list(tape_root.glob("*.csv.gz")) if tape_root.exists() else []
    disk_usage={}
    for target in (EXEC/"state",EXEC/"data/durable/ws_depth_recorder",tape_root,pathlib.Path("/tmp/live_v4.log")):
        row=run("du","-sb",str(target),check=False); disk_usage[str(target)]=row["stdout"].split()[0] if row["exit_code"]==0 and row["stdout"].split() else None
    state_files=[]
    for p in sorted((EXEC/"state").glob("*")) if (EXEC/"state").exists() else []:
        if p.is_file(): state_files.append(ident(p))
    backup=pathlib.Path("/root/root.crontab.pre_schedule_liar_stop_20260728_e7004235.raw")
    ak,pk=live.load_credentials()
    if not ak: raise RuntimeError("credentials_unavailable")
    rl=live.RateLimiter()
    async with aiohttp.ClientSession() as session:
        positions,pp=await all_pages(session,ak,pk,rl,"/trade-api/v2/portfolio/positions?count_filter=position&settlement_status=unsettled","market_positions")
        orders,op=await all_pages(session,ak,pk,rl,"/trade-api/v2/portfolio/orders?status=resting","orders")
        balance=await live.api_get(session,ak,pk,"/trade-api/v2/portfolio/balance",rl)
        stopped_exit_orders=[]
        for oid in STOP_EXIT_IDS:
            try:
                data=await live.api_get(session,ak,pk,"/trade-api/v2/portfolio/orders/"+oid,rl)
                row=data.get("order",data) if isinstance(data,dict) else data
                found=isinstance(row,dict) and bool(row.get("order_id") or row.get("status") or row.get("ticker"))
                stopped_exit_orders.append({"order_id":oid,"status":row.get("status") if found else "NOT_RETURNED_BY_ORDER_LOOKUP","ticker":row.get("ticker") if found else None,"remaining_quantity":qty(row) if found else None,"fill_count_fp":row.get("fill_count_fp") if found else None})
            except Exception as exc: stopped_exit_orders.append({"order_id":oid,"status":"GET_FAILED","error":type(exc).__name__})
    normalized_orders=[]
    for o in orders:
        ticker=str(o.get("ticker") or ""); action=str(o.get("action") or "").lower()
        normalized_orders.append({"order_id":o.get("order_id"),"ticker":ticker,"action":action,"side":o.get("side"),"status":o.get("status"),"price_cents":price(o),"remaining_quantity":qty(o),"created_time":o.get("created_time"),"classification":"EXIT_SELL" if action=="sell" else "ENTRY_BUY" if action=="buy" else "OTHER"})
    normalized_positions=[]
    for p in positions:
        normalized_positions.append({"ticker":p.get("ticker"),"exchange_position_qty":float(p.get("position_fp") or 0),"market_exposure_dollars":p.get("market_exposure_dollars"),"total_traded_dollars":p.get("total_traded_dollars"),"realized_pnl_dollars":p.get("realized_pnl_dollars")})
    sells={}
    for o in normalized_orders:
        if o["classification"]=="EXIT_SELL": sells[o["ticker"]]=sells.get(o["ticker"],0)+o["remaining_quantity"]
    recon=[]
    for p in normalized_positions:
        held=p["exchange_position_qty"]; resting=sells.get(p["ticker"],0)
        recon.append({"ticker":p["ticker"],"held":held,"resting_sell":resting,"resting_minus_held":round(resting-held,8),"coverage":"EXACT" if abs(resting-held)<1e-9 else "UNDER" if resting<held else "OVER"})
    out={
      "schema_version":"boot-gate-stage-a-vps-audit-v1","captured_utc":now,"access":"READ_ONLY_GET_AND_FILESYSTEM_METADATA",
      "git":{"head":head,"branch":branch,"status_porcelain":status,"status_count":len(status),"status_summary":{"modified":sum(x[:2].strip() in ("M","MM") for x in status),"untracked":sum(x.startswith("??") for x in status),"deleted":sum("D" in x[:2] for x in status)},"live_v4":{**ident(live_path),"working_git_blob":blob,"head_git_blob":head_blob,"working_diff_numstat":live_numstat},"config":ident(config)},
      "processes":{"live_v4_count":sum("live_v4.py" in x for x in relevant),"recorder_like_count":sum(any(k in x.lower() for k in ("premarket","recorder","capture_book","ws_depth")) for x in relevant),"relevant":relevant,"tmux_exit_code":tmux["exit_code"],"tmux_sessions":tmux["stdout"].splitlines()},
      "cron":{"sha256":hashlib.sha256(cr.encode()).hexdigest(),"bytes":len(cr.encode()),"live_v4_active_lines":[x for x in cron_lines if "live_v4.py" in x and not x.lstrip().startswith("#")],"live_v4_marker_lines":[x for x in cron_lines if "live_v4.py" in x and x.lstrip().startswith("#")],"recorder_active_lines":[x for x in cron_lines if any(k in x.lower() for k in ("premarket","recorder","capture_book","shape")) and not x.lstrip().startswith("#")],"backup":ident(backup)},
      "disk":{"mounts":disk,"directory_bytes":disk_usage,"premarket_tape_files":len(tape_files),"premarket_tape_bytes":sum(p.stat().st_size for p in tape_files),"tmp_live_log":ident("/tmp/live_v4.log"),"tmp_heartbeat":ident("/tmp/heartbeat_live_v3.json")},
      "exchange":{"pagination":{"positions":pp,"orders":op},"balance":balance,"positions":normalized_positions,"resting_orders":normalized_orders,"stopped_exit_binding":{"operator_prompt_count":17,"controlling_fd623dd_receipt_count":12,"controlling_fd623dd_receipt_quantity":50,"queried_order_count":len(stopped_exit_orders),"resolution_counts":{s:sum(x["status"]==s for x in stopped_exit_orders) for s in sorted(set(x["status"] for x in stopped_exit_orders))},"orders":stopped_exit_orders},"counts":{"positions":len(normalized_positions),"resting_orders":len(normalized_orders),"entry_buys":sum(o["classification"]=="ENTRY_BUY" for o in normalized_orders),"exit_sells":sum(o["classification"]=="EXIT_SELL" for o in normalized_orders),"entry_buy_qty":sum(o["remaining_quantity"] for o in normalized_orders if o["classification"]=="ENTRY_BUY"),"exit_sell_qty":sum(o["remaining_quantity"] for o in normalized_orders if o["classification"]=="EXIT_SELL")},"position_exit_reconciliation":recon,"reconciliation_counts":{"exact":sum(x["coverage"]=="EXACT" for x in recon),"under":sum(x["coverage"]=="UNDER" for x in recon),"over":sum(x["coverage"]=="OVER" for x in recon)}},
      "engine_state_files":state_files,
      "mutations":{"filesystem":0,"git":0,"cron":0,"process":0,"orders":0,"positions":0,"balance":0,"service":0}
    }
    print(json.dumps(out,sort_keys=True,separators=(",",":")))
asyncio.run(main())
'''


def canonical(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--host", default="root@104.131.191.95")
    args = parser.parse_args()
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(["ssh", "-o", "BatchMode=yes", args.host, "python3", "-"], input=REMOTE, text=True, capture_output=True)
    if proc.returncode:
        raise SystemExit(proc.stderr or proc.stdout)
    audit = json.loads(proc.stdout)
    audit_bytes = canonical(audit)
    (output / "VPS_AND_EXCHANGE_READONLY_SNAPSHOT.json").write_bytes(audit_bytes)
    counts = audit["exchange"]["counts"]
    recon = audit["exchange"]["reconciliation_counts"]
    stage_a_safe = audit["processes"]["live_v4_count"] == 0 and counts["entry_buys"] == 0 and recon["over"] == 0
    restart_blockers = []
    if audit["git"]["status_count"]: restart_blockers.append("VPS_WORKTREE_DIRTY")
    if audit["git"]["live_v4"]["working_git_blob"] != audit["git"]["live_v4"]["head_git_blob"]: restart_blockers.append("LIVE_V4_WORKING_BYTES_DIFFER_FROM_HEAD_PREIMAGE")
    if audit["cron"]["sha256"] != "0e2af22e4ab536b4273e61d9251359eda71e369fb8591f22443c66aa88709926": restart_blockers.append("CRONTAB_DRIFT_FROM_CONTROLLED_STOP")
    if audit["exchange"]["stopped_exit_binding"]["operator_prompt_count"] != audit["exchange"]["stopped_exit_binding"]["controlling_fd623dd_receipt_count"]: restart_blockers.append("OPERATOR_17_EXIT_COUNT_CONFLICTS_WITH_CONTROLLING_12_EXIT_RECEIPT")
    status = "STAGE_A_COMPLETE_AWAITING_EXPLICIT_STAGE_B_WORD" if stage_a_safe else "STAGE_A_BLOCKED"
    receipt = {
        "schema_version": "boot-gate-stage-a-readiness-v1",
        "status": status,
        "stage_A": "COMPLETED_READ_ONLY",
        "stage_B": "NOT_AUTHORIZED_NOT_STARTED",
        "stage_C": "NOT_AUTHORIZED_NOT_STARTED",
        "inheritance": {
            "vps_head": audit["git"]["head"], "git_drift_rows": audit["git"]["status_count"], "git_drift_summary": audit["git"]["status_summary"],
            "live_v4_processes": audit["processes"]["live_v4_count"], "recorder_processes": audit["processes"]["recorder_like_count"],
            "resting_exit_sells": counts["exit_sells"], "resting_exit_quantity": counts["exit_sell_qty"],
            "resting_entry_buys": counts["entry_buys"], "unsettled_positions": counts["positions"],
            "position_exit_exact": recon["exact"], "position_exit_under": recon["under"], "position_exit_over": recon["over"],
        },
        "snapshot_sha256": digest(audit_bytes),
        "restart_readiness": "NOT_READY" if restart_blockers else "READY_ONLY_AFTER_SEPARATE_STAGE_AUTHORIZATION",
        "restart_blockers": restart_blockers,
        "mutations": audit["mutations"],
    }
    (output / "STAGE_A_READINESS_RECEIPT.json").write_bytes(canonical(receipt))
    report = f"""# Boot gate — Stage A read-only audit

Status: **{status}**. Stage B and Stage C were not authorized or started.

- VPS HEAD: `{audit['git']['head']}`; branch: `{audit['git']['branch']}`; Git drift rows: {audit['git']['status_count']}.
- Drift split: {audit['git']['status_summary']['modified']} modified, {audit['git']['status_summary']['untracked']} untracked, {audit['git']['status_summary']['deleted']} deleted.
- live_v4 processes: {audit['processes']['live_v4_count']}; recorder-like processes: {audit['processes']['recorder_like_count']}.
- Resting exchange orders: {counts['resting_orders']}; exit sells: {counts['exit_sells']} / {counts['exit_sell_qty']} contracts; entry buys: {counts['entry_buys']} / {counts['entry_buy_qty']} contracts.
- Unsettled positions: {counts['positions']}; exit coverage exact/under/over: {recon['exact']}/{recon['under']}/{recon['over']}.
- Installed crontab SHA-256: `{audit['cron']['sha256']}`; active live_v4 launch lines: {len(audit['cron']['live_v4_active_lines'])}.
- live_v4 HEAD blob / working blob / SHA-256 / bytes: `{audit['git']['live_v4']['head_git_blob']}` / `{audit['git']['live_v4']['working_git_blob']}` / `{audit['git']['live_v4']['sha256']}` / {audit['git']['live_v4']['bytes']}.
- Active configuration SHA-256: `{audit['git']['config']['sha256']}`.
- Controlling stop receipt: 12 exits / 50 contracts, not the prompt's 17. Current lookup: {audit['exchange']['stopped_exit_binding']['resolution_counts']}.
- Balance: {audit['exchange']['balance']}; root free bytes: {audit['disk']['mounts'][0]['bytes_free']}.
- Restart readiness: NOT_READY; blockers: {restart_blockers}.
- Audit mutations: 0 across filesystem, Git, cron, processes, orders, positions, balance, and services.

The complete drift list, processes, disk/inode state, paginated orders, paginated positions, balance response, and per-ticker exit reconciliation are frozen in `VPS_AND_EXCHANGE_READONLY_SNAPSHOT.json`.
"""
    (output / "STAGE_A_REPORT.md").write_text(report, encoding="utf-8", newline="\n")
    forbidden = {"schema_version":"boot-gate-stage-a-nonmutation-v1","stage_B_recorder_start":0,"stage_B_cron_changes":0,"stage_C_builds":0,"deployment":0,"restart":0,"order_mutations":0,"position_mutations":0,"source_or_config_mutations":0,"read_only_exchange_GETs":True}
    (output / "NONMUTATION_RECEIPT.json").write_bytes(canonical(forbidden))
    files = {}
    for file in sorted(output.iterdir()):
        if file.name == "ARTIFACT_HASH_MANIFEST.json": continue
        data = file.read_bytes(); files[file.name] = {"bytes":len(data),"sha256":digest(data)}
    (output / "ARTIFACT_HASH_MANIFEST.json").write_bytes(canonical({"schema_version":"boot-gate-stage-a-artifact-manifest-v1","files":files}))
    print(json.dumps({"status":status,"output":str(output),"snapshot_sha256":digest(audit_bytes),"counts":counts,"reconciliation":recon},indent=2))


if __name__ == "__main__":
    main()
