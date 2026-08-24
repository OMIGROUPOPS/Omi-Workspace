"use strict";

const fs = require("fs");
const path = require("path");

function required(name) {
  const index = process.argv.indexOf(`--${name}`);
  if (index < 0 || !process.argv[index + 1]) throw new Error(`missing --${name}`);
  return path.resolve(process.argv[index + 1]);
}

const parentPackage = required("parent-package");
const repairedPackage = required("repaired-package");
const output = required("output");
const eventId = "KXATPCHALLENGERMATCH-26JUL14LAJSVA";
const receiptId = "51ffb46a-c62c-6890-aa69-cd9970de51c6";

const parent = JSON.parse(fs.readFileSync(path.join(parentPackage, "LAYERED_DUAL_BELIEF_RECEIPT.json"), "utf8"));
const stage = parent.games?.[eventId]?.timeline?.find((row) => row.receipt === receiptId);
if (!stage) throw new Error("F_VS_120_LAJ_62_ENVELOPE_STAGE_MISSING");
const action = stage.actions?.find((row) => row.leg_id === "LAJ");
if (action?.envelope?.low_cents !== 62 || action?.envelope?.high_cents !== 62) throw new Error("F_VS_120_LAJ_62_ENVELOPE_NOT_REPRODUCED");
const belief = stage.beliefs?.LAJ;
if (!belief?.phase_conditioning?.rows?.length) throw new Error("F_VS_120_LAJ_CONDITIONING_ROWS_MISSING");
const repaired = JSON.parse(fs.readFileSync(path.join(repairedPackage, "LAJ_FLOOR_MOMENT_BELIEF_INPUTS.json"), "utf8"));

const artifact = {
  label: "F_VS_120_MEASUREMENT_ONLY_LAJ_62_ENVELOPE_CONDITIONING_ROWS",
  event_id: eventId,
  leg_id: "LAJ",
  policy_use: false,
  repair_input: false,
  requested_parent_envelope: {
    source_package: path.basename(parentPackage),
    timestamp_epoch: stage.timestamp_epoch,
    receipt: stage.receipt,
    envelope: action.envelope,
    belief_verbatim: belief,
    conditioning_rows_verbatim: belief.phase_conditioning.rows,
  },
  current_repair_floor_moment: repaired,
  finding: "The requested parent [62,62] conditioning rows are retained verbatim. The repaired own-low-return build no longer emits that envelope at LAJ's floor moment; it is DISAGREES with a null envelope there.",
};
fs.writeFileSync(output, `${JSON.stringify(artifact, null, 2)}\n`, "utf8");
