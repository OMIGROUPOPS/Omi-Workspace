import { chromium } from "playwright";
import fs from "node:fs/promises";
import assert from "node:assert/strict";
const browser = await chromium.launch({ headless: true, channel: "chrome" });
const page = await browser.newPage({ viewport: { width: 1440, height: 1080 } });
const errors = [],
  report = {};
page.on("pageerror", (e) => errors.push(String(e)));
const url = "http://127.0.0.1:8080/?event=KXATPMATCH-26JUL12ALTGAS&gate=480";
try {
  await page.goto(url, { waitUntil: "networkidle" });
  await page.getByLabel("Checkpoint scene").getByText("Checkpoint 480m", { exact: true }).waitFor();
  const stored = await page.evaluate(() => window.TUNE_DATA.face.render.bid_actions);
  report.alt_reprices = stored.filter((a) => a.leg === "ALT" && a.raw.action === "REPRICE_REST");
  assert.deepEqual(
    report.alt_reprices.map((a) => [a.old_cents, a.new_cents]),
    [
      [55, 49],
      [49, 55],
      [55, 49],
      [49, 45],
    ],
  );
  assert.equal(await page.locator('.recorded-floor-line line[stroke-opacity="0.5"]').count(), 2);
  assert.equal(await page.locator(".recorded-floor-line line[stroke-dasharray]").count(), 0);
  assert.equal(await page.locator(".recorded-floor-flag").count(), 2);
  assert.equal(
    await page.getByText("recorded floor 58¢ · 3362m to bell", { exact: true }).count(),
    1,
  );
  assert.ok(
    (await page.getByLabel("FLOOR · RECORDED", { exact: true }).innerText()).includes(
      "best capturable 96¢ · 4¢ under par",
    ),
  );
  report.fill = stored.find((a) => a.fill).fill;
  const card = page.locator(".fill-label-card");
  assert.ok((await card.innerText()).includes(report.fill.summary));
  assert.ok((await card.innerText()).includes("4¢ above floor 38¢"));
  await card.locator("summary").click();
  assert.ok((await card.innerText()).includes(report.fill.placing_sentence.plain_sentence));
  await card.locator("summary").click();
  const first = page.locator(`[data-action-id="${report.alt_reprices[0].id}"]`);
  await first.hover();
  assert.equal(
    await page.getByRole("tooltip").innerText(),
    report.alt_reprices[0].hover_lines.join("\n\n"),
  );
  await page.mouse.move(0, 0);
  await page.getByRole("tooltip").waitFor({ state: "hidden" });
  await page.evaluate(() => {
    window.scrollTo(0, 0);
    return document.fonts.ready;
  });
  await page.screenshot({ path: "../proof/altgas-bid-actions-480.png", fullPage: true });
  // Later receipts must not leak into gate 480, then become individually hoverable at gate 5.
  assert.equal(await page.locator(`[data-action-id="${report.alt_reprices[2].id}"]`).count(), 0);
  await page.getByRole("button", { name: "Checkpoint 5 minutes to bell", exact: true }).click();
  for (const a of report.alt_reprices) {
    await page.locator(`[data-action-id="${a.id}"]`).hover();
    const tip = await page.getByRole("tooltip").innerText();
    for (const line of a.hover_lines) assert.ok(tip.includes(line));
    assert.ok(tip.includes(a.raw.reason));
    await page.mouse.move(0, 0);
  }
  // Same-clock PLACE and fill each keep an independent hit target; receipt-order reveal.
  const order = await page.evaluate(() => {
    const g = window.TUNE_DATA;
    return g.face.render.bid_actions
      .filter((a) => a.leg === "GAS")
      .map((a) => ({
        id: a.id,
        frame: g.frames.findIndex((f) => f.receipt_index === a.receipt_index),
      }));
  });
  await page.getByLabel("Replay receipt and tape frames").fill(String(order[0].frame));
  assert.equal(await page.locator('[data-action-kind="FILL"]').count(), 0);
  await page.getByLabel("Replay receipt and tape frames").fill(String(order[1].frame));
  for (const o of order) {
    await page.locator(`[data-action-id="${o.id}"]`).hover();
    assert.ok(await page.getByRole("tooltip").isVisible());
    await page.mouse.move(0, 0);
  }
  await page.goto(url, { waitUntil: "networkidle" });
  await page.locator(".fill-label-card").waitFor();
  await page.setViewportSize({ width: 390, height: 844 });
  report.mobile = await page.evaluate(() => ({
    screen: innerWidth,
    document: document.documentElement.scrollWidth,
  }));
  assert.ok(report.mobile.document <= report.mobile.screen);
  await page.setViewportSize({ width: 1440, height: 1080 });
  await page
    .getByLabel("Load game", { exact: true })
    .selectOption("KXATPCHALLENGERMATCH-26JUL14URSPAL");
  await page.waitForFunction(() => window.TUNE_DATA.face.provenance.event_id.endsWith("URSPAL"));
  await page.getByRole("button", { name: "Checkpoint 240 minutes to bell", exact: true }).click();
  await page.getByRole("button", { name: "Play", exact: true }).click();
  report.frame_timing = await page.evaluate(async () => {
    const times = [];
    let last = performance.now();
    for (let i = 0; i < 360; i++) {
      await new Promise(requestAnimationFrame);
      const now = performance.now();
      times.push(now - last);
      last = now;
    }
    times.sort((a, b) => a - b);
    return {
      samples: times.length,
      median_ms: times[Math.floor(times.length / 2)],
      max_ms: times.at(-1),
      over_16_67_ms: times.filter((t) => t > 16.67).length,
    };
  });
  await page.getByRole("button", { name: "Pause", exact: true }).click();
  await page
    .getByLabel("Replay receipt and tape frames")
    .fill(await page.getByLabel("Replay receipt and tape frames").getAttribute("max"));
  assert.equal(await page.locator(".fill-label-card").count(), 2);
  report.urspal_fills = await page.locator(".fill-label-card").allInnerTexts();
  assert.deepEqual(errors, []);
  report.browser = {
    page_errors: errors,
    all_four_reprice_hovers: true,
    receipt_order_reveal: true,
    solid_half_alpha_floors: true,
  };
  await fs.writeFile("../proof/bid-actions.json", JSON.stringify(report, null, 2) + "\n");
  console.log(
    JSON.stringify(
      {
        reprices: report.alt_reprices.map((a) => ({
          t: a.t,
          old: a.old_cents,
          new: a.new_cents,
          reason: a.raw.reason,
        })),
        fill: report.fill.summary,
        floor: report.fill.floor_line,
        mobile: report.mobile,
        frame_timing: report.frame_timing,
        browser: report.browser,
      },
      null,
      2,
    ),
  );
} finally {
  await browser.close();
}
