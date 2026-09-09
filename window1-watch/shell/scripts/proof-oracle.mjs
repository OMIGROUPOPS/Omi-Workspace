import { chromium } from "playwright";
import { resolve } from "node:path";
const browser=await chromium.launch({headless:true,channel:"chrome"});
try {
  const page=await browser.newPage({viewport:{width:1600,height:2120},deviceScaleFactor:1});
  const errors=[];page.on("pageerror",e=>errors.push(e.message));
  await page.goto("http://localhost:8080/?event=KXATPMATCH-26JUL12ALTGAS&gate=480",{waitUntil:"networkidle"});
  await page.getByLabel("ALT sentence gap strip",{exact:true}).waitFor();
  await page.locator(".oracle-path").first().waitFor();
  console.log("GAPS",await page.getByLabel("Sentence GAP",{exact:true}).innerText());
  console.log("PATHS",await page.locator(".oracle-path path").evaluateAll(es=>es.map(e=>({d:e.getAttribute("d"),opacity:e.getAttribute("stroke-opacity")}))));
  const strip=page.getByLabel("ALT sentence gap strip",{exact:true});
  await strip.scrollIntoViewIfNeeded();
  await strip.locator("canvas").hover({position:{x:450,y:40}});
  console.log("HOVER",await strip.getByRole("tooltip").innerText());
  await page.mouse.move(0,0);
  await page.evaluate(()=>window.scrollTo(0,0));
  await page.screenshot({path:resolve("../proof/oracle-path-480.png"),fullPage:false});
  console.log("ERRORS",errors);if(errors.length)throw new Error(errors.join("\n"));
} finally {await browser.close();}
