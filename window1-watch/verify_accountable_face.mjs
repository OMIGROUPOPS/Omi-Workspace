import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
import {unpackFace} from './face_encoding.mjs';
const here=path.dirname(fileURLToPath(import.meta.url)),[event,custody,auditFile]=process.argv.slice(2);
const face=unpackFace(JSON.parse(fs.readFileSync(path.join(here,'data',`${event}.face.json`))));
const auditBytes=zlib.gunzipSync(fs.readFileSync(path.join(here,'.'+face.accountability.detail_url+'.gz')));
assert.equal(crypto.createHash('sha256').update(auditBytes).digest('hex'),face.accountability.sha256_uncompressed);
const rows=JSON.parse(auditBytes).rows, proof=JSON.parse(fs.readFileSync(path.join(custody,'ACCOUNTABLE_BIDS_RECEIPT.json')));
assert.equal(face.provenance.os_sha256,proof.provenance.os_sha256);
assert.equal(face.provenance.trace_sha256,proof.provenance.trace_sha256);
const firstLeg=face.legs[0],place=face.render.bid_actions.find(a=>a.leg===firstLeg&&a.kind==='PLACE');
const renewal=rows.find(r=>r.kind==='BID_RENEWAL'&&r.phase==='TICK'&&r.assumption_id===place.bid_accountability.assumption.assumption_id);
const move=face.render.bid_actions.find(a=>a.leg===firstLeg&&a.kind==='REPRICE');
const receipt={...proof,face_acceptance:{first_leg:firstLeg,first_assumption:place.bid_accountability.assumption,
 first_tick_renewal:renewal,first_reprice:{receipt:move.receipt,minutes_to_bell:move.minutes_to_bell,
 old_cents:move.old_cents,new_cents:move.new_cents,...move.bid_accountability},
 bid_markers:face.render.bid_actions.length,supersession_markers:face.render.supersessions.length,
 marker_missing_accountability:face.render.bid_actions.filter(a=>!a.bid_accountability?.assumption||!a.bid_accountability?.renewal).length,
 compressed_face_bytes:fs.statSync(path.join(here,'data',`${event}.face.json.gz`)).size,
 accountability_sha256_uncompressed:face.accountability.sha256_uncompressed,
 later_outcome_label:'Explicitly later observation, not knowledge at marker',
 grade:'No renewal markers in order/age inputs; existing grade remains based on unchanged decisions and fills'}};
receipt.report_only_finalization={builder_sha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(here,'../arb-executor/analysis/build_window1_v54_dual_belief.js'))).digest('hex'),
 changes_after_replay:'main also retains the new receipt rows in its report projection so a full multi-game custody manifest counts them; expose existing literalClaimAudit for this audit. replayEvent, digestReplay and the OS unchanged after acceptance.',
 source_scope_audit_sha256:crypto.createHash('sha256').update(fs.readFileSync(auditFile)).digest('hex')};
assert.equal(receipt.face_acceptance.marker_missing_accountability,0);
const dir=path.join(here,'data/accountable-bids');fs.mkdirSync(dir,{recursive:true});
fs.writeFileSync(path.join(dir,'ACCOUNTABLE_BIDS_RECEIPT.json'),JSON.stringify(receipt,null,2)+'\n');
fs.copyFileSync(auditFile,path.join(dir,'ACCOUNTABLE_BIDS_STAGE_A.json'));
console.log(JSON.stringify(receipt.face_acceptance,null,2));
