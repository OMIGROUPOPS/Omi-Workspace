import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {chromium} from 'playwright';
const base=process.argv[2]??'http://127.0.0.1:8083',out=process.argv[3]??'C:/tmp/unsupported_rests_20260914/timeline-proof';
const event=process.argv[4]??'KXATPCHALLENGERMATCH-26JUL12HERALM';
fs.mkdirSync(out,{recursive:true});
const browser=await chromium.launch({channel:'msedge',headless:true}),page=await browser.newPage({viewport:{width:1600,height:1100}});
const requests=[],errors=[];page.on('request',r=>{if(r.url().includes('.timeline/'))requests.push(r.url())});page.on('pageerror',e=>errors.push(e.message));
try{
 await page.goto(`${base}/?tab=lab&event=${event}&gate=5`);
 await page.waitForFunction(e=>window.TUNE_DATA?.face.provenance.event_id===e&&window.TUNE_DATA.grade_status==='OK',event,{timeout:120000});
 const initial=await page.evaluate(()=>({chunks:window.TUNE_DATA.face.timeline.chunks.length,receipts:window.TUNE_DATA.face.os.length,loaded:window.TUNE_DATA.face.os.filter(r=>!r.timeline_pending).length,markers:window.TUNE_DATA.face.render.bid_actions.length}));
 assert(initial.chunks>1);assert(initial.loaded<initial.receipts);assert(requests.length<initial.chunks);
 const slider=page.locator('input[type=range]').first();await slider.focus();await slider.press('Home');
 await page.locator('.reading-plot').first().waitFor({timeout:120000});
 await slider.focus();await slider.press('End');
 await page.waitForFunction(()=>!document.querySelector('[role=status]')?.textContent?.includes('Loading and verifying'),null,{timeout:120000});
 await page.locator('.reading-plot').first().waitFor({timeout:120000});
 const after=await page.evaluate(()=>({loaded:window.TUNE_DATA.face.os.filter(r=>!r.timeline_pending).length,receipts:window.TUNE_DATA.face.os.length,markers:window.TUNE_DATA.face.render.bid_actions.length}));
 assert(after.loaded<after.receipts);assert.equal(after.markers,initial.markers);assert(requests.length<initial.chunks);assert.deepEqual(errors,[]);
 await page.screenshot({path:path.join(out,event+'-timeline.png'),fullPage:true});
 const result={status:'PASS',event,base,initial,after,chunk_requests:requests,js_errors:errors};fs.writeFileSync(path.join(out,event+'-VERIFY.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
}finally{await browser.close();}
