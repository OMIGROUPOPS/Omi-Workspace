import { chromium } from "playwright";
import fs from "node:fs/promises";
import assert from "node:assert/strict";
const browser = await chromium.launch({ headless: true, channel: "chrome" });
const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } }),
  errors = [],
  report = {};
page.on("pageerror", (e) => errors.push(String(e)));
try {
  for (const [name, event] of [
    ["altgas", "KXATPMATCH-26JUL12ALTGAS"],
    ["urspal", "KXATPCHALLENGERMATCH-26JUL14URSPAL"],
  ]) {
    await page.goto(`http://127.0.0.1:8080/?event=${event}&gate=480`, { waitUntil: "networkidle" });
    const hud = page.getByLabel("FLOOR · RECORDED", { exact: true });
    await hud.getByText("RULER — NOT AN OS INPUT", { exact: true }).waitFor();
    const truth = await page.evaluate(() => window.TUNE_DATA.face.truth);
    assert.equal(truth.table_commit, "c0056976c446afcb4d9603796a2e06c068ee94d6");
    for (const leg of Object.values(truth.legs))
      assert.ok((await hud.innerText()).includes(leg.line));
    assert.ok((await hud.innerText()).includes(truth.pair.compact_line));
    assert.ok((await hud.innerText()).includes(truth.pair.discount_line));
    assert.equal(await page.locator(".recorded-floor-line").count(), 2);
    assert.equal(await page.locator(".recorded-floor-flag").count(), 2);
    await page.evaluate(() => document.fonts.ready);
    await page.screenshot({ path: `../proof/${name}-recorded-floor.png`, fullPage: true });
    report[name] = truth;
  }
  await page.getByRole("button", { name: "Checkpoint 240 minutes to bell", exact: true }).click();
  assert.equal(await page.locator(".recorded-floor-flag").count(), 2);
  assert.equal(await page.locator('.recorded-floor-flag[data-boundary="BEFORE_AXIS"]').count(), 1);
  await page.setViewportSize({ width: 390, height: 844 });
  const width = await page.evaluate(() => ({
    screen: innerWidth,
    document: document.documentElement.scrollWidth,
  }));
  assert.ok(width.document <= width.screen);
  assert.deepEqual(errors, []);
  report.browser = { page_errors: errors, mobile: width, hud_and_two_floor_markers: true };
  await fs.writeFile("../proof/recorded-floors.json", JSON.stringify(report, null, 2) + "\n");
  console.log(JSON.stringify(report, null, 2));
} finally {
  await browser.close();
}
