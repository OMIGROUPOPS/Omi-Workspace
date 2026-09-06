import { chromium } from "playwright";
import fs from "node:fs/promises";
import assert from "node:assert/strict";
const browser = await chromium.launch({ headless: true, channel: "chrome" });
const page = await browser.newPage({ viewport: { width: 1440, height: 1080 } });
const errors = [],
  report = {};
page.on("pageerror", (e) => errors.push(String(e)));
const events = ["KXATPMATCH-26JUL12ALTGAS", "KXATPCHALLENGERMATCH-26JUL14URSPAL"];
try {
  for (const [i, event] of events.entries()) {
    await page.goto(`http://127.0.0.1:8080/?event=${event}&gate=480`, { waitUntil: "networkidle" });
    await page.locator("[data-grade-letter]").waitFor();
    const g = await page.evaluate(() => ({
      grade: window.TUNE_DATA.grade,
      status: window.TUNE_DATA.grade_status,
      history: window.TUNE_DATA.history,
    }));
    assert.equal(g.status, "OK");
    assert.equal(g.grade.LETTER.letter, "F");
    assert.equal(await page.locator("[data-grade-letter]").innerText(), "F");
    assert.equal(await page.locator("[data-grade-section]").count(), 5);
    for (const s of g.grade.display.sections) {
      const line = page.locator(`[data-grade-section="${s.name}"]`);
      assert.ok((await line.innerText()).includes(s.line));
      assert.equal(await line.getAttribute("title"), s.hover_lines.join("\n"));
    }
    assert.equal(await page.locator("[data-grade-history-dot]:visible").count(), g.history.length);
    assert.ok(g.history.length >= 2, "rerun history retained");
    await page
      .locator('[aria-label="Grade card"]')
      .screenshot({ path: `../proof/${i ? "urspal" : "altgas"}-grade.png` });
    assert.equal(await page.locator(".recorded-floor-flag").count(), 2);
    report[event] = {
      letter: g.grade.LETTER.letter,
      governing: g.grade.LETTER.governing_section,
      q_share: g.grade.SENTENCE.share_q_authored_by_organ,
      x_share: g.grade.SENTENCE.share_x_authored_by_organ,
      captured: g.grade.OUTCOME.captured_cents,
      offered: g.grade.OUTCOME.best_capturable_cents,
      named_tokens: g.grade.SENTENCE.named_tokens_found,
      history_snapshots: g.history.length,
    };
  }
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(`http://127.0.0.1:8080/?event=${events[0]}&gate=480`, {
    waitUntil: "networkidle",
  });
  assert.ok(
    await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
    "no mobile page overflow",
  );
  await page.locator('[aria-label="Grade card"]').screenshot({ path: "../proof/grade-mobile.png" });
  await page.route("**/*.grade.json", async (route) => {
    const r = await route.fetch();
    const data = await r.json();
    data.provenance.trace_sha256 = "mismatch";
    await route.fulfill({ json: data });
  });
  await page.reload({ waitUntil: "networkidle" });
  assert.equal(await page.locator("[data-grade-letter]").innerText(), "—");
  assert.match(
    await page.locator('[aria-label="Grade card"]').innerText(),
    /grade does not match this face/,
  );
  await page.unroute("**/*.grade.json");
  await page.route("**/*.grade.json", (route) => route.fulfill({ status: 404, body: "not built" }));
  await page.reload({ waitUntil: "networkidle" });
  assert.match(
    await page.locator('[aria-label="Grade card"]').innerText(),
    /STORE SILENT — no grade built/,
  );
  assert.equal(await page.locator("[data-grade-letter]").innerText(), "—");
  assert.deepEqual(errors, []);
  report.checks = [
    "both loaded grades F",
    "five stored section lines and hover numbers",
    "repeat history retained",
    "floors still present",
    "mobile no horizontal overflow",
    "mismatched grade rejected",
    "missing grade STORE SILENT",
    "no page errors",
  ];
  await fs.writeFile("../proof/grade-card.json", JSON.stringify(report, null, 2) + "\n");
  console.log(JSON.stringify(report, null, 2));
} finally {
  await browser.close();
}
