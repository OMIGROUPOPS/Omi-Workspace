import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {chromium} from 'playwright';
const base=process.argv[2]??'http://127.0.0.1:8082',out=process.argv[3]??'C:/tmp/tune_fault_taxonomy_20260914';
fs.mkdirSync(out,{recursive:true});
const audit=JSON.parse(fs.readFileSync(new URL('../../data/tune-expansion/faults/index.json',import.meta.url)));
const browser=await chromium.launch({channel:'msedge',headless:true});
const page=await browser.newPage({viewport:{width:1600,height:1100}}),errors=[],rows=[];
page.on('pageerror',e=>errors.push(e.message));
try{
 const scoreResponse=await page.request.get(base+'/data/scoreboard-tune-100.json');assert.equal(scoreResponse.status(),200);const score=await scoreResponse.json();
 assert.equal(score.rows.length,100);assert.equal(score.summaries[0].captured_cents,audit.summary[0].credit.captured_cents);assert.equal(score.summaries[0].complete,audit.summary[0].credit.complete);
 const index=await (await page.request.get(base+'/data/index.json')).json();assert.equal(index.games.length,104);
 await page.goto(base+'/?tab=lab&event='+audit.games[0].event);
 for(const g of audit.games){
  if(rows.length)await page.getByRole('combobox',{name:'Load game',exact:true}).selectOption(g.event);
  await page.locator(`[data-fault-event="${g.event}"]`).waitFor({timeout:60000});
  assert((await page.locator(`[data-fault-event="${g.event}"] summary`).innerText()).includes(g.header));
  if(g.known_span){
   await page.waitForFunction(event=>window.TUNE_DATA?.face.provenance.event_id===event&&window.TUNE_DATA.grade_status==='OK'&&window.TUNE_DATA.oracle_status==='OK',g.event,{timeout:60000});
   const value=await page.evaluate(()=>({os:window.TUNE_DATA.face.provenance.os_sha256,trace:window.TUNE_DATA.face.provenance.trace_sha256}));assert.equal(value.os,g.provenance.os_sha256);assert.equal(value.trace,g.provenance.trace_sha256);
   if(g.credit.safety_excluded){const text=await page.locator('.reading-result').innerText();assert(text.includes('0 of '));assert(text.includes('Safety fill excluded'));}
  }else await page.getByRole('alert').filter({hasText:'No verified replay span'}).waitFor();
  rows.push({event:g.event,classes:g.classes,known_span:g.known_span,safety_excluded:g.credit.safety_excluded,status:'PASS'});
 }
 const example=audit.games.find(g=>g.event.endsWith('GANZIN'));
 await page.getByRole('combobox',{name:'Load game',exact:true}).selectOption(example.event);
 await page.waitForFunction(event=>window.TUNE_DATA?.face.provenance.event_id===event,example.event);
 await page.locator(`[data-fault-event="${example.event}"] summary`).click();
 await page.screenshot({path:path.join(out,'fault-GANZIN.png'),fullPage:true});
 await page.goto(base+'/?tab=scoreboard&collection=tune-expansion');
 await page.locator('[data-score-game]').first().waitFor();assert.equal(await page.locator('[data-score-game]').count(),100);
 const excluded=await page.request.get(base+'/data/not-shipped.stages/raw.json');
 if(!['127.0.0.1','localhost'].includes(new URL(base).hostname))assert.equal(excluded.status(),404);
 else assert(!excluded.headers()['content-type']?.includes('application/json'),'Missing stage must not return fabricated JSON; Vite preview may use HTML fallback');
 assert.deepEqual(errors,[]);
 const result={status:'PASS',base,games:rows.length,rows,scoreboard_capture:score.summaries[0].captured_cents,scoreboard_completed:score.summaries[0].complete,omitted_stage_status:excluded.status(),js_errors:errors};
 fs.writeFileSync(path.join(out,'VERIFY.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({status:result.status,base,games:rows.length,scoreboard_capture:result.scoreboard_capture,scoreboard_completed:result.scoreboard_completed,js_errors:errors}));
}finally{await browser.close();}
