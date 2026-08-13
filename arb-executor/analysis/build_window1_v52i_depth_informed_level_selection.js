#!/usr/bin/env node
"use strict";
process.argv.push("--variant", "v52i", "--stage", "cohort30");
require("./build_window1_v38_maker_only.js");
