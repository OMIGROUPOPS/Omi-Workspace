#!/usr/bin/env node
"use strict";
process.argv.push("--variant", "v52q", "--stage", "cohort30", "--output", ".claude/window1_live_v4_replay/v52q_anchor_correction_20260818");
require("./build_window1_v38_maker_only.js");
