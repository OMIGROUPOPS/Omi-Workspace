#!/usr/bin/env node
"use strict";

// The V38 harness owns the frozen union-reach and strict-print rulers.  V39
// selects a separate policy and output identity; V38 remains its default mode.
if (!process.argv.includes("--variant")) process.argv.push("--variant", "v39");
require("./build_window1_v38_maker_only.js");
