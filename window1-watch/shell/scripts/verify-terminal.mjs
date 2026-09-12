import assert from 'node:assert/strict';
import {mkdirSync,writeFileSync,readFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {chromium} from 'playwright';
const base=process.argv[2]??'http://127.0.0.1:8083',phase=process.argv[3]??'lab';
const out=resolve(import.meta.dirname,'../../docs/face-v3');mkdirSync(out,{recursive:true});
const inputs=JSON.parse(readFileSync(resolve(out,'MOCKUP_RECEIPT.json'))).inputs;
const b=await chromium.launch({channel:'msedge',headless:true}),p=await b.newPage({viewport:{width:1700,height:1120}}),errors=[];
p.on('pageerror',e=>errors.push(e.message));const rows=[];
try{
 await p.goto(`${base}/?tab=lab&event=KXATPMATCH-26JUL12ALTGAS&gate=480`);
 await p.waitForFunction(()=>window.TUNE_DATA?.grade_status==='OK'&&window.TUNE_DATA?.oracle_status==='OK');
 for(const input of inputs){await p.locator('#load-game').selectOption(input.event);await p.waitForFunction(e=>window.TUNE_DATA?.face.provenance.event_id===e&&window.TUNE_DATA?.grade_status==='OK'&&window.TUNE_DATA?.oracle_status==='OK',input.event);await p.waitForFunction(()=>document.querySelectorAll('.oracle-path .recharts-line-curve').length===2);const row=await p.evaluate(()=>({event:window.TUNE_DATA.face.provenance.event_id,face_sha:window.TUNE_DATA.grade.provenance.face_sha256,grade:window.TUNE_DATA.grade.display.letter,trace:window.TUNE_DATA.face.provenance.trace_sha256}));assert.equal(row.face_sha,input.face_sha256);rows.push(row);assert.equal(await p.getByRole('dialog').count(),0);assert.equal(await p.locator('[aria-label$="sentence gap strip"]').count(),2);}
 await p.goto(`${base}/?tab=lab&event=KXATPMATCH-26JUL12ALTGAS&gate=480`);await p.waitForFunction(()=>window.TUNE_DATA?.grade_status==='OK'&&window.TUNE_DATA?.oracle_status==='OK');await p.locator('.oracle-path .recharts-line-curve').first().waitFor();
 assert.equal(await p.locator('#gate-jump').inputValue(),'480');assert.equal(await p.getByRole('navigation',{name:'Terminal tabs'}).getByRole('button').count(),3);
 await p.locator('[data-action-id]').first().focus();await p.getByRole('tooltip').waitFor();assert.match(await p.getByRole('tooltip').innerText(),/Why:/);await p.screenshot({path:resolve(out,'lab-bid-card-built.png'),fullPage:true});await p.keyboard.press('Escape');await p.mouse.move(0,0);
 await p.screenshot({path:resolve(out,'lab-built.png'),fullPage:true});
 await p.locator('main').click({position:{x:2,y:2}});await p.keyboard.press('/');assert.equal(await p.locator('#load-game').evaluate(e=>e===document.activeElement),true);await p.locator('main').click({position:{x:2,y:2}});await p.keyboard.press('g');assert.equal(await p.locator('#gate-jump').evaluate(e=>e===document.activeElement),true);
 if(phase!=='lab'){for(const tab of ['desk','scoreboard']){await p.getByRole('navigation',{name:'Terminal tabs'}).getByRole('button',{name:tab.toUpperCase(),exact:true}).click();await p.waitForTimeout(400);if(tab==='desk'){await p.getByText('No live paper ledger is connected.',{exact:true}).waitFor();assert.equal(await p.locator('[data-live-game]').count(),0)}else{await p.locator('[data-score-game]').first().waitFor();assert.equal(await p.locator('[data-score-game]').count(),5)}await p.screenshot({path:resolve(out,`${tab}-built.png`),fullPage:true});}}
 await p.getByRole('navigation',{name:'Terminal tabs'}).getByRole('button',{name:'LAB',exact:true}).click();
 const importEvent=inputs[0].event,importPath=resolve(out,'../../data',importEvent+'.face.json');
 await p.locator('input[type=file]').setInputFiles(importPath);await p.getByText(/LOCAL PREPARED FACE/).waitFor();assert.equal(await p.locator('#load-game').inputValue(),importEvent);await p.waitForFunction(e=>window.TUNE_DATA.face.provenance.event_id===e&&window.TUNE_DATA.grade_status==='OK',importEvent);
 const sealed=JSON.parse(readFileSync(importPath));sealed.provenance.source_class='SEALED';await p.locator('input[type=file]').setInputFiles({name:'rejected-source.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(sealed))});await p.getByRole('alert').filter({hasText:'excluded from LAB imports'}).waitFor();
 await p.locator('#load-game').selectOption('KXATPMATCH-26JUL12ALTGAS');await p.waitForFunction(()=>window.TUNE_DATA.face.provenance.event_id==='KXATPMATCH-26JUL12ALTGAS');
 await p.setViewportSize({width:390,height:844});await p.getByRole('navigation',{name:'Terminal tabs'}).getByRole('button',{name:'LAB',exact:true}).click();await p.screenshot({path:resolve(out,'lab-mobile-built.png'),fullPage:true});
 assert.deepEqual(errors,[]);const report={base,phase,games:rows,js_errors:errors,inspector:'fixed; no modal',keyboard:'game and gate focus verified',sources:'all five face hashes unchanged',imports:'prepared face selection/provenance aligned; sealed-source test rejected',desk:phase==='lab'?'not tested':'disconnected, zero fabricated games'};writeFileSync(resolve(out,`VERIFY_${phase.toUpperCase()}.json`),JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));
}finally{await b.close()}
