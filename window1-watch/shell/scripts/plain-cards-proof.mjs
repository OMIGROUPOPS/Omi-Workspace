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
  const actions = await page.evaluate(() => window.TUNE_DATA.face.render.bid_actions);
  const reprices = actions.filter((a) => a.leg === "ALT" && a.raw.action === "REPRICE_REST");
  const fill = actions.find((a) => a.fill);
  const checkCard = async (scope, a) => {
    assert.deepEqual(await scope.locator("[data-card-line]").allInnerTexts(), a.card_lines);
    assert.equal(await scope.locator("details[open]").count(), 0);
    assert.ok(!(await scope.innerText()).includes("BASE_PRICING_AUTHORITY_EXECUTED_BY_LANE"));
    const rows = await scope
      .locator("[data-card-line]")
      .evaluateAll((nodes) =>
        nodes.map((n) => ({
          height: n.getBoundingClientRect().height,
          lineHeight: parseFloat(getComputedStyle(n).lineHeight),
        })),
      );
    assert.ok(rows.every((r) => r.height === r.lineHeight));
  };
  const hover = async (a) => {
    await page.locator(`[data-action-id="${a.id}"]`).hover();
    const tip = page.getByRole("tooltip");
    await tip.waitFor();
    await checkCard(tip, a);
    return tip;
  };
  let tip = await hover(reprices[0]);
  await tip.locator("summary").click();
  assert.ok((await tip.innerText()).includes(reprices[0].raw.reason));
  assert.ok((await tip.innerText()).includes("PRIOR_ONLY"));
  await tip.locator("summary").click();
  await checkCard(tip, reprices[0]);
  await page.evaluate(() => document.fonts.ready);
  await tip.screenshot({ path: "../proof/alt-reprice-plain-card.png" });
  await page.mouse.move(0, 0);
  await page.getByRole("tooltip").waitFor({ state: "hidden" });
  await checkCard(page.locator(".fill-label-card"), fill);
  assert.equal(
    await page.locator(".recorded-floor-flag").first().getAttribute("title"),
    "Recorded floor 58¢ printed here · 3362m to bell · from the truth table (not an OS input)",
  );
  assert.equal(
    await page.getByText("▪ bid action · ● fill · ⚑ recorded floor", { exact: true }).count(),
    2,
  );
  const pool = page.getByLabel("Pool accuracy", { exact: true });
  assert.ok((await pool.innerText()).includes("POOL ACCURACY · bench only"));
  assert.equal(await pool.locator(".pool-accuracy-value").innerText(), "13.86%");
  const checkpoints = await page.evaluate(() => window.TUNE_DATA.face.render.checkpoints);
  for (const c of checkpoints.filter(
    (c) => c.bench?.validity.ess != null && c.bench.validity.ess < 10,
  )) {
    await page
      .getByRole("button", { name: `Checkpoint ${c.minutesToBell} minutes to bell`, exact: true })
      .click();
    assert.equal(await pool.locator(".pool-accuracy-value").innerText(), "—");
    assert.equal(
      await pool.locator(".pool-accuracy-value").getAttribute("title"),
      c.bench.pool_accuracy.hover_note,
    );
  }
  await page.getByRole("button", { name: "Checkpoint 5 minutes to bell", exact: true }).click();
  for (const a of reprices) {
    tip = await hover(a);
    await tip.locator("summary").click();
    assert.ok((await tip.innerText()).includes(a.raw.reason));
    await page.mouse.move(0, 0);
    await page.getByRole("tooltip").waitFor({ state: "hidden" });
  }
  await hover(fill);
  await page.mouse.move(0, 0);
  await page.getByRole("tooltip").waitFor({ state: "hidden" });
  const markers = await page.locator(".bid-action-marker").allInnerTexts();
  assert.ok(markers.every((m) => m === "▪" || m === "●"));
  assert.equal(markers.filter((m) => m === "●").length, 1);
  await page.setViewportSize({ width: 390, height: 844 });
  tip = await hover(reprices[0]);
  report.mobile = await page.evaluate(() => ({
    screen: innerWidth,
    document: document.documentElement.scrollWidth,
  }));
  assert.ok(report.mobile.document <= report.mobile.screen);
  await page.mouse.move(0, 0);
  await page.getByRole("tooltip").waitFor({ state: "hidden" });
  assert.deepEqual(errors, []);
  report.cards = reprices
    .concat(fill)
    .map((a) => ({ t: a.t, lines: a.card_lines, raw_reason: a.raw.reason }));
  report.pool_low_ess = checkpoints
    .filter((c) => c.bench?.validity.ess != null && c.bench.validity.ess < 10)
    .map((c) => ({ gate: c.minutesToBell, ess: c.bench.validity.ess, ...c.bench.pool_accuracy }));
  report.checks = {
    four_physical_lines: true,
    raw_details_closed_by_default: true,
    raw_fields_retained: true,
    squares_and_fill_dot_only: true,
    floor_hover: true,
    pool_label: true,
    page_errors: errors,
  };
  await fs.writeFile("../proof/plain-cards.json", JSON.stringify(report, null, 2) + "\n");
  console.log(JSON.stringify(report, null, 2));
} finally {
  await browser.close();
}
