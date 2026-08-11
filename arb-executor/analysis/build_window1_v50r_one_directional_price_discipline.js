#!/usr/bin/env node
"use strict";

if (!process.argv.includes("--variant")) process.argv.push("--variant", "v50");
if (!process.argv.includes("--v50-law")) process.argv.push("--v50-law", "one-directional");
if (!process.argv.includes("--output")) process.argv.push("--output", ".claude/window1_live_v4_replay/v50r_one_directional_price_discipline_20260811");
require("./build_window1_v38_maker_only.js");
