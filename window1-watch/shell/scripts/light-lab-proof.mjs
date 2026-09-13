import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {writeFileSync} from 'node:fs';
import {resolve} from 'node:path';
const base=process.argv[2]??'http://127.0.0.1:8084';
const suffix=base.startsWith('http://127.')?'local':'hosted';
const browser=await chromium.launch({headless:true,channel:'chrome'});
const report={base,status:'PASS',games:[],errors:[],screenshots:[]};
try {
  const page=await browser.newPage({viewport:{width:1440,height:1100}});
  page.setDefaultTimeout(30000);
  page.on('pageerror',e=>report.errors.push(e.message));
  const index=await (await page.request.get(`${base}/data/index.json`)).json();
  const alt=index.games.find(g=>g.event.endsWith('ALTGAS')).event;
  async function load(event) {
    await page.goto(`${base}/?tab=lab&event=${event}&gate=480`);
    await page.locator('[data-decision-engine]').waitFor();
    await page.waitForFunction(event=>window.TUNE_DATA?.face.provenance.event_id===event,event);
    assert.equal(await page.locator('[data-recorded-floor]').count(),2);
    assert.equal(await page.locator('[data-perfect-sentence]').count(),2);
    assert.equal(await page.locator('[data-call-path]').count(),2);
    const x=await page.evaluate(()=>({event:window.TUNE_DATA.face.provenance.event_id,
      pressure:window.TUNE_DATA.pressure_status,grade:window.TUNE_DATA.grade?.display.letter,
      floors:Object.values(window.TUNE_DATA.face.truth.legs).map(r=>r.floor_cents),
      overflow:document.documentElement.scrollWidth>innerWidth,stageText:document.querySelector('.reading-stage').innerText}));
    assert.equal(x.pressure,'OK');assert.equal(x.overflow,false);
    assert.doesNotMatch(x.stageText,/\b(?:ESS|FIRST-TICK-ONLY|RESOLVED|STORE SILENT)\b/);
    report.games.push({...x,stageText:undefined});return x;
  }
  for(const g of index.games)await load(g.event);
  await load(alt);
  await page.waitForFunction(()=>document.querySelector('#gate-jump').value==='-480');
  report.at480=await page.locator('.reading-stage').innerText();
  assert.match(report.at480,/2 of 4¢ captured/);assert.match(report.at480,/3,938\.55 contracts/);
  assert.match(report.at480,/21,611/);assert.match(report.at480,/284 matching games/);
  const desktop=resolve(`../proof/light-lab-${suffix}-480.png`);
  await page.screenshot({path:desktop,fullPage:true});report.screenshots.push(desktop);
  await page.setViewportSize({width:390,height:844});
  // A frame ensures ResizeObserver has resized both SVGs before capture.
  await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
  const rects=await page.locator('.reading-game-header>*').evaluateAll(nodes=>nodes.map(n=>{const r=n.getBoundingClientRect();return{x:r.x,y:r.y,right:r.right,bottom:r.bottom}}));
  for(let i=0;i<rects.length;i++)for(let j=i+1;j<rects.length;j++)assert.ok(!(rects[i].x<rects[j].right&&rects[i].right>rects[j].x&&rects[i].y<rects[j].bottom&&rects[i].bottom>rects[j].y),'Header items overlap');
  const phone=resolve(`../proof/light-lab-${suffix}-phone.png`);
  await page.screenshot({path:phone,fullPage:true});report.screenshots.push(phone);
  await page.setViewportSize({width:1440,height:1100});
  await page.locator('[data-timeline-event="GAS-fill"]').click();
  await page.waitForFunction(()=>document.querySelector('.reading-stage').textContent.includes('8,853.34 contracts'));
  report.bothFilled=await page.locator('.reading-stage').innerText();
  assert.match(report.bothFilled,/T - 2hr 49 min/);assert.match(report.bothFilled,/325 matching games/);assert.match(report.bothFilled,/366 matching games/);
  assert.equal(await page.locator('.decision-engine>header small').innerText(),'T - 2hr 49 min');
  assert.match(report.bothFilled,/0\.382×/);assert.match(report.bothFilled,/not rated/);
  assert.match(report.bothFilled,/60¢ → 60¢/);assert.match(report.bothFilled,/38¢ → 38¢/);
  assert.equal(await page.locator('.engine-secured').filter({hasText:'Filled'}).count(),2);
  const filled=resolve(`../proof/light-lab-${suffix}-filled.png`);
  await page.screenshot({path:filled,fullPage:true});report.screenshots.push(filled);
  const fillId=await page.evaluate(()=>window.TUNE_DATA.face.render.bid_actions.find(a=>a.leg==='ALT'&&a.fill).id);
  await page.locator(`[data-action-id="${fillId}"]`).click();
  const card=page.locator('.reading-action-tip');await card.waitFor();report.fillCard=await card.innerText();
  assert.match(report.fillCard,/Bid-setting call: 60¢/);assert.match(report.fillCard,/this price stood 6\.09m/);
  assert.equal(await card.locator('.card-lines p').count(),4);
  await page.screenshot({path:resolve(`../proof/light-lab-${suffix}-card.png`),fullPage:true});
  await card.getByRole('button',{name:'Close',exact:true}).click();
  await page.getByRole('button',{name:'Details +',exact:true}).click();
  assert.equal(await page.locator('#reading-details').isVisible(),true);
  await page.getByRole('button',{name:'Close details',exact:true}).click();
  await page.getByRole('button',{name:'DESK',exact:true}).click();
  assert.equal(await page.locator('.reading-terminal').count(),0);
  assert.match(await page.locator('main').innerText(),/PAPER/);
  await page.getByRole('button',{name:'SCOREBOARD',exact:true}).click();
  await page.getByRole('button',{name:'LAB',exact:true}).click();
  assert.deepEqual(report.errors,[]);
  writeFileSync(resolve(`../proof/LIGHT_LAB_${suffix.toUpperCase()}_PROOF.json`),JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify(report,null,2));
} finally {await browser.close();}
