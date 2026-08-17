#!/usr/bin/env node
"use strict";

process.argv.push("--variant", "v52o", "--stage", "cohort30", "--output", ".claude/window1_live_v4_replay/v52o_benchmarked_role_instrument_20260817");
require("./build_window1_v38_maker_only.js");
