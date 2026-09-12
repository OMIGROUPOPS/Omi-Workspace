import assert from "node:assert/strict";
import { mkdirSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";
import { chromium } from "playwright";

const base = process.argv[2] ?? "http://127.0.0.1:8082";
const output = resolve(process.argv[3] ?? ".vercel/demo-check");
mkdirSync(output, { recursive: true });
const browser = await chromium.launch({ channel: "msedge", headless: true });
const page = await browser.newPage({ viewport: { width: 1600, height: 1200 }, deviceScaleFactor: 1 });
const errors = [];
page.on("pageerror", error => errors.push(error.message));
const reports = [];
try {
  await page.goto(`${base}/?event=KXATPMATCH-26JUL12ALTGAS&gate=480`, { waitUntil: "networkidle" });
  await page.waitForFunction(() => window.TUNE_DATA?.grade_status === "OK" && window.TUNE_DATA?.oracle_status === "OK", undefined, { timeout: 60000 });
  const games = await page.locator("select option").evaluateAll(options => options.map(o => o.value).filter(Boolean));
  assert.equal(games.length, 5);
  for (const event of games) {
    await page.locator("select").selectOption(event);
    await page.waitForFunction(event => window.TUNE_DATA?.face.provenance.event_id === event && window.TUNE_DATA?.grade_status === "OK" && window.TUNE_DATA?.oracle_status === "OK", event, { timeout: 60000 });
    await page.waitForFunction(() => document.querySelectorAll('.oracle-path .recharts-line-curve').length === 2);
    reports.push(await page.evaluate(() => ({
      event: window.TUNE_DATA.face.provenance.event_id,
      grade_status: window.TUNE_DATA.grade_status,
      oracle_status: window.TUNE_DATA.oracle_status,
      letter: window.TUNE_DATA.grade.display.letter,
      floors: document.querySelector('[aria-label="FLOOR · RECORDED"]').textContent,
      oracle_paths: document.querySelectorAll('.oracle-path .recharts-line-curve').length,
      gap_strips: document.querySelectorAll('[aria-label$="sentence gap strip"]').length,
    })));
  }
  await page.goto(`${base}/?event=KXATPMATCH-26JUL12ALTGAS&gate=480`, { waitUntil: "networkidle" });
  await page.waitForFunction(() => window.TUNE_DATA?.grade_status === "OK" && window.TUNE_DATA?.oracle_status === "OK");
  assert.equal(await page.locator('.oracle-path .recharts-line-curve').count(), 2);
  assert.equal(await page.locator('[aria-label$="sentence gap strip"]').count(), 2);
  assert.ok(await page.locator('[data-action-id]').count() > 0);
  await page.locator('[data-action-id]').first().focus();
  await page.getByRole("tooltip").waitFor({ state: "visible" });
  const card = await page.getByRole("tooltip").innerText();
  assert.match(card, /Why:/);
  assert.match(card, /Believed:/);
  await page.screenshot({ path: resolve(output, "altgas-480-bid-card.png"), fullPage: true });
  await page.keyboard.press("Escape");
  await page.mouse.move(0, 0);
  await page.screenshot({ path: resolve(output, "altgas-480.png"), fullPage: true });
  const missing = await page.request.get(`${base}/data/missing.stages/test.json`);
  if (!new URL(base).hostname.match(/^(localhost|127\.0\.0\.1)$/)) {
    assert.equal(missing.status(), 404, "Excluded stage files should report 404, not HTML success");
  }
  assert.deepEqual(errors, []);
  const report = { base, games: reports, bid_card: card, page_errors: errors, excluded_stage_http: missing.status() };
  writeFileSync(resolve(output, "verification.json"), JSON.stringify(report, null, 2));
  console.log(JSON.stringify(report, null, 2));
} finally {
  await browser.close();
}
