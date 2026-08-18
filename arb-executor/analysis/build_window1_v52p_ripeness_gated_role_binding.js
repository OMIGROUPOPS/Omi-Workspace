#!/usr/bin/env node
"use strict";
process.argv.push("--variant", "v52p", "--stage", "cohort30", "--output", ".claude/window1_live_v4_replay/v52p_ripeness_gated_role_binding_20260817");
require("./build_window1_v38_maker_only.js");
