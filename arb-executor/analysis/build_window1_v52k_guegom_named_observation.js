#!/usr/bin/env node
"use strict";
process.argv.push("--variant", "v52k", "--stage", "cohort30", "--named-only", "true");
require("./build_window1_v38_maker_only.js");
