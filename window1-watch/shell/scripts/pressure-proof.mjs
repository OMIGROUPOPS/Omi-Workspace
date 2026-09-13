import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {resolve} from 'node:path';
import {writeFileSync} from 'node:fs';
const browser=await chromium.launch({headless:true,channel:'chrome'});
try {
  const page=await browser.newPage({viewport:{width:1440,height:1000}}), errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  const base=process.argv[2]??'http://127.0.0.1:8084';
  await page.goto(`${base}/?tab=lab&event=KXATPMATCH-26JUL12ALTGAS&gate=480`);
  await page.locator('[data-pressure-chain]').waitFor();
  await page.waitForFunction(()=>window.TUNE_DATA && document.querySelector('#gate-jump')?.value === '-480');
  const initial=await page.locator('[data-pressure-chain]').innerText();
  assert.match(initial,/Contracts|contracts/);
  assert.match(initial,/no data here/);
  assert.match(initial,/Last recorded receipt/);
  await page.screenshot({path:resolve('../proof/lab-pressure-480.png'),fullPage:false});
  await page.locator('#gate-jump').evaluate(el=>{
    Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(el,'-169.28');
    el.dispatchEvent(new Event('input',{bubbles:true}));
    el.dispatchEvent(new Event('change',{bubbles:true}));
  });
  await page.waitForFunction(()=>document.querySelector('[data-pressure-chain]')?.textContent.includes('8,853.34 contracts'));
  const filled=await page.locator('[data-pressure-chain]').innerText();
  assert.match(filled,/8,853\.34 contracts/);assert.match(filled,/5,887\.28 contracts/);
  assert.match(filled,/31,580 \/ 41,387/);assert.match(filled,/29,053 \/ 44,242/);
  assert.match(filled,/pool of 325 games/);assert.match(filled,/pool of 366 games/);
  assert.deepEqual(errors,[]);
  const result={status:'PASS',at_480:initial,at_fill:filled,page_errors:errors};
  writeFileSync(resolve('../proof/LAB_PRESSURE_RENDERED.json'),JSON.stringify(result,null,2)+'\n');
  console.log(JSON.stringify(result,null,2));
} finally {await browser.close();}
