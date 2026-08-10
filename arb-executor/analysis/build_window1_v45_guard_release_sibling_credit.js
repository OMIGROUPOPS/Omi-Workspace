#!/usr/bin/env node
"use strict";

if (!process.argv.includes("--variant")) process.argv.push("--variant", "v45");
require("./build_window1_v38_maker_only.js");
