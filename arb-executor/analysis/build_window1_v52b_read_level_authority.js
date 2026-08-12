#!/usr/bin/env node
"use strict";
process.argv.splice(2, 0, "--variant", "v52b", "--stage", "cohort30");
require("./build_window1_v38_maker_only.js");
