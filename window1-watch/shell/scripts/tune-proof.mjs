import { chromium } from "playwright";
import fs from "node:fs/promises";
import path from "node:path";
import assert from "node:assert/strict";
const proof = path.resolve("../proof");
await fs.mkdir(proof, { recursive: true });
const browser = await chromium.launch({ headless: true, channel: "chrome" });
const page = await browser.newPage({
  viewport: { width: 1440, height: 1000 },
  deviceScaleFactor: 1,
});
const errors = [],
  stageRequests = [];
page.on("pageerror", (e) => errors.push(String(e)));
page.on("request", (r) => {
  if (r.url().includes(".stages/")) stageRequests.push(r.url());
});
const report = {};
try {
  for (const [name, event] of [
    ["ALTGAS", "KXATPMATCH-26JUL12ALTGAS"],
    ["URSPAL", "KXATPCHALLENGERMATCH-26JUL14URSPAL"],
  ]) {
    await page.goto(`http://127.0.0.1:8080/?event=${event}&gate=480`, { waitUntil: "networkidle" });
    await page
      .getByRole("button", { name: "Checkpoint 480 minutes to bell", exact: true })
      .waitFor();
    await page.getByRole("button", { name: "Checkpoint 480 minutes to bell", exact: true }).click();
    await page
      .getByLabel("Checkpoint scene")
      .getByText("Checkpoint 480m", { exact: true })
      .waitFor();
    await page.evaluate(() => document.fonts.ready);
    const loaded = await page.evaluate(() => ({
      event: window.TUNE_DATA.face.provenance.event_id,
      provenance: window.TUNE_DATA.face.provenance,
      verification: window.TUNE_DATA.face.render.verification,
      gate: window.TUNE_DATA.face.render.checkpoints.find((c) => c.minutesToBell === 480),
      frames: window.TUNE_DATA.frames.length,
    }));
    assert.equal(loaded.event, event);
    assert.equal(stageRequests.length, 0, "No inspector stage should be eagerly fetched");
    if (name === "URSPAL") {
      assert.equal(
        await page.getByRole("button", { name: "Play", exact: true }).isDisabled(),
        true,
      );
      assert.match(await page.getByLabel("Tune test HUD").innerText(), /STORE SILENT/);
      assert.equal(loaded.gate.playable, false);
      assert.equal(loaded.gate.bench, null);
    }
    await page.screenshot({
      path: path.join(proof, `${name.toLowerCase()}-480.png`),
      fullPage: true,
    });
    report[name] = loaded;
    if (name === "ALTGAS") {
      const place = loaded.verification.ALT.first_rest;
      assert.equal(place.lane, "INSUFFICIENT_AUTHORITY_NO_WRITER");
      await page.getByRole("button", { name: /ALT PLACE_REST 55/ }).click();
      const drawer = page.getByRole("dialog", { name: "Full receipt inspector" });
      await drawer.getByText("Decision index — as stored", { exact: true }).waitFor();
      assert.match(await drawer.innerText(), /INSUFFICIENT_AUTHORITY_NO_WRITER/);
      assert.match(
        await drawer.innerText(),
        /ENGINE_VOTES_LICENSED_DEPTH_PRIOR_WITH_NO_OWN_EVIDENCE_YET/,
      );
      await page.screenshot({ path: path.join(proof, "alt-place-inspector.png"), fullPage: true });
      report.inspector = {
        lane: place.lane,
        authority_source: place.authority_source,
        lazy_requests: stageRequests.splice(0),
      };
      await page.getByRole("button", { name: "Close inspector", exact: true }).click();
    }
  }
  await page.getByLabel("Load game", { exact: true }).selectOption("KXATPMATCH-26JUL12ALTGAS");
  await page.waitForFunction(
    () =>
      window.TUNE_DATA.face.provenance.event_id === "KXATPMATCH-26JUL12ALTGAS" &&
      location.search.includes("KXATPMATCH-26JUL12ALTGAS"),
  );
  await page.getByLabel("Checkpoint scene").getByText("Checkpoint 480m", { exact: true }).waitFor();
  const scene = page.getByLabel("Checkpoint scene");
  const originalIndex = Number(await scene.getAttribute("data-receipt-index"));
  await page.getByRole("button", { name: "Next", exact: true }).click();
  assert.equal(Number(await scene.getAttribute("data-receipt-index")), originalIndex + 1);
  await page.getByRole("button", { name: "Prev", exact: true }).click();
  assert.equal(Number(await scene.getAttribute("data-receipt-index")), originalIndex);
  await page.getByRole("button", { name: "Checkpoint 480 minutes to bell", exact: true }).click();
  await page.getByRole("button", { name: "Next checkpoint", exact: true }).click();
  await scene.getByText("Checkpoint 360m", { exact: true }).waitFor();
  report.controls = {
    picker_updates_url: true,
    next_receipt: true,
    previous_receipt: true,
    next_checkpoint: "480 → 360",
  };
  const simultaneous = await page.evaluate(() => {
    const g = window.TUNE_DATA;
    const rest = g.face.os.find((r) => r.legs.GAS?.rest);
    const fill = g.face.os.find((r) => r.legs.GAS?.fill);
    return {
      rest_index: rest.index,
      fill_index: fill.index,
      rest_time: rest.t,
      fill_time: fill.t,
      rest_frame: g.frames.findIndex((f) => f.receipt_index === rest.index),
      fill_frame: g.frames.findIndex((f) => f.receipt_index === fill.index),
    };
  });
  assert.equal(simultaneous.rest_time, simultaneous.fill_time);
  assert.notEqual(simultaneous.rest_frame, simultaneous.fill_frame);
  await page.getByLabel("Replay receipt and tape frames").fill(String(simultaneous.rest_frame));
  assert.equal(Number(await scene.getAttribute("data-receipt-index")), simultaneous.rest_index);
  assert.match(await page.getByLabel("Tune test HUD").innerText(), /GAS 42¢/);
  assert.equal(await page.getByRole("button", { name: "GAS fill 42¢", exact: true }).count(), 0);
  await page.getByLabel("Replay receipt and tape frames").fill(String(simultaneous.fill_frame));
  assert.equal(await page.getByRole("button", { name: "GAS fill 42¢", exact: true }).count(), 1);
  assert.match(await page.getByLabel("Tune test HUD").innerText(), /GAS none/);
  report.same_timestamp_receipts = simultaneous;
  report.clip = await page
    .locator(".tune-history .recharts-line")
    .first()
    .evaluate((el) => getComputedStyle(el).clipPath);
  assert.notEqual(report.clip, "none", "The static paths must be clipped to the source clock");
  await page
    .getByLabel("Replay receipt and tape frames")
    .fill(await page.getByLabel("Replay receipt and tape frames").getAttribute("max"));
  assert.ok(
    (await page.locator('[data-rest-miss="true"] .rest-history').count()) > 0,
    "ALT unfilled rest fades at bell",
  );
  assert.ok((await page.locator(".fill-burst").count()) > 0, "Recorded fill markers appear");
  await page
    .getByLabel("Load game", { exact: true })
    .selectOption("KXATPCHALLENGERMATCH-26JUL14URSPAL");
  await page.waitForFunction(
    () => window.TUNE_DATA.face.provenance.event_id === "KXATPCHALLENGERMATCH-26JUL14URSPAL",
  );
  await page.getByRole("button", { name: "Checkpoint 240 minutes to bell", exact: true }).click();
  await page.getByRole("button", { name: "Play", exact: true }).click();
  report.playbackFrameTiming = await page.evaluate(async () => {
    const times = [];
    let previous = performance.now();
    for (let i = 0; i < 360; i++) {
      await new Promise(requestAnimationFrame);
      const current = performance.now();
      times.push(current - previous);
      previous = current;
    }
    return {
      samples: times.length,
      median_ms: times.sort((a, b) => a - b)[180],
      max_ms: Math.max(...times),
      over_16_67_ms: times.filter((t) => t > 16.67).length,
      note: "Headless Chrome, development server, during receipt playback; not a hardware-independent 60fps guarantee",
    };
  });
  await page.getByRole("button", { name: "Pause", exact: true }).click();
  await page.setViewportSize({ width: 390, height: 844 });
  await page.getByRole("button", { name: "Checkpoint 480 minutes to bell", exact: true }).click();
  report.mobile = await page.evaluate(() => ({
    viewport: innerWidth,
    document_width: document.documentElement.scrollWidth,
  }));
  assert.ok(
    report.mobile.document_width <= report.mobile.viewport,
    "Mobile page must not overflow horizontally",
  );
  assert.deepEqual(errors, []);
  report.page_errors = errors;
  await fs.writeFile(
    path.join(proof, "browser-verification.json"),
    JSON.stringify(report, null, 2),
  );
  console.log(JSON.stringify(report, null, 2));
} finally {
  await browser.close();
}
