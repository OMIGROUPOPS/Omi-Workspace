import assert from 'node:assert/strict';
import { mkdirSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { chromium } from 'playwright';
const base=process.argv[2]??'http://127.0.0.1:8084';
const out=resolve(process.argv[3]??'../docs/face-v3/option-a');
mkdirSync(out,{recursive:true});
const browser=await chromium.launch({channel:'msedge',headless:true});
const page=await browser.newPage({viewport:{width:1600,height:1000},deviceScaleFactor:1});
const errors=[];page.on('pageerror',e=>errors.push(e.message));
const loaded=()=>page.waitForFunction(()=>window.TUNE_DATA?.grade_status==='OK'&&window.TUNE_DATA?.oracle_status==='OK'&&document.querySelectorAll('[data-tape-path]').length===2);
const report={base,games:[],views:[],errors};
try {
  await page.goto(`${base}/?tab=lab&event=KXATPMATCH-26JUL12ALTGAS&gate=480`);await loaded();
  const events=await page.locator('#load-game option').evaluateAll(es=>es.map(e=>e.value));
  assert.equal(events.length,5);
  for(const event of events){
    await page.locator('#load-game').selectOption(event);
    await page.waitForFunction(e=>window.TUNE_DATA?.face.provenance.event_id===e,event);await loaded();
    assert.equal(await page.locator('[data-perfect-sentence]').count(),2);
    assert.equal(await page.locator('[data-recorded-floor]').count(),2);
    assert.equal(await page.locator('table:visible').count(),0);
    assert.equal(await page.locator('#reading-details').count(),0);
    assert.doesNotMatch(await page.locator('main').innerText(),/ESS|FIRST-TICK-ONLY|RESOLVED|STORE SILENT/);
    report.games.push(await page.evaluate(()=>({event:window.TUNE_DATA.face.provenance.event_id,grade:window.TUNE_DATA.grade.display.letter,face_sha:window.TUNE_DATA.grade.provenance.face_sha256,sentences:[...document.querySelectorAll('.reading-sentence h2')].map(e=>e.textContent)})));
  }
  await page.goto(`${base}/?tab=lab&event=KXATPMATCH-26JUL12ALTGAS&gate=480`);await loaded();
  assert.match(await page.locator('.reading-sentence').first().innerText(),/61¢ by 6:10/);
  assert.match(await page.locator('.reading-sentence').last().innerText(),/38¢ by 4:02/);
  for(const [name,width,height] of [['desktop',1600,1000],['phone',390,844]]){
    await page.setViewportSize({width,height});await page.waitForTimeout(250);
    const geometry=await page.evaluate(()=>({overflow:document.documentElement.scrollWidth>innerWidth,chartHeight:[...document.querySelectorAll('.reading-plot')].reduce((n,e)=>n+e.clientHeight,0),pageHeight:document.documentElement.scrollHeight,minChartWidth:Math.min(...[...document.querySelectorAll('.reading-plot')].map(e=>e.clientWidth))}));
    assert.equal(geometry.overflow,false);assert.ok(geometry.minChartWidth>300);assert.ok(geometry.chartHeight/geometry.pageHeight>=.70,JSON.stringify(geometry));
    await page.screenshot({path:resolve(out,`lab-a-${name}.png`),fullPage:true});report.views.push({name,...geometry});
  }
  await page.setViewportSize({width:1600,height:1000});
  await page.locator('[data-action-kind="REPRICE"]').first().focus();await page.getByRole('tooltip').waitFor();
  assert.match(await page.getByRole('tooltip').innerText(),/Why:/);assert.doesNotMatch(await page.getByRole('tooltip').innerText(),/ESS|FIRST-TICK-ONLY|RESOLVED|STORE SILENT/);
  await page.screenshot({path:resolve(out,'lab-a-bid-card.png'),fullPage:true});await page.keyboard.press('Escape');
  const before=await page.locator('#gate-jump').inputValue();
  await page.getByRole('button',{name:'Next receipt',exact:true}).click();assert.notEqual(await page.locator('#gate-jump').inputValue(),before);
  await page.getByRole('button',{name:'Previous receipt',exact:true}).click();assert.equal(await page.locator('#gate-jump').inputValue(),before);
  await page.getByRole('button',{name:'Details +',exact:true}).click();
  await page.locator('[aria-label="Full receipt inspector"]').waitFor();
  assert.ok(await page.locator('[data-grade-history-dot]').count()>0);
  await page.getByText('Book lines, pool bands and sentence gap',{exact:true}).click();
  assert.equal(await page.locator('[aria-label$="sentence gap strip"]').count(),2);
  await page.getByRole('button',{name:'Close details',exact:true}).click();
  await page.getByRole('button',{name:'DESK',exact:true}).click();await page.getByText('No live paper ledger is connected.',{exact:true}).waitFor();
  await page.getByRole('button',{name:'SCOREBOARD',exact:true}).click();await page.locator('[data-score-game]').first().waitFor();assert.equal(await page.locator('[data-score-game]').count(),5);
  assert.deepEqual(errors,[]);
  writeFileSync(resolve(out,'verification.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
}finally{await browser.close()}
