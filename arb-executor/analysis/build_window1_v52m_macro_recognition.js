#!/usr/bin/env node
"use strict";

process.argv.push("--variant", "v52m", "--stage", "cohort30", "--output", ".claude/window1_live_v4_replay/v52m_macro_recognition_20260817");
require("./build_window1_v38_maker_only.js");
