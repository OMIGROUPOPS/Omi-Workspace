#!/usr/bin/env node
"use strict";

// Deterministic entrypoint only. The causal onset implementation lives in
// window1_v52l_causal_stability_onset.js and is not modified here.
process.argv.push("--variant", "v52l", "--stage", "cohort30");
require("./build_window1_v38_maker_only.js");
