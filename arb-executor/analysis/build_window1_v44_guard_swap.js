#!/usr/bin/env node
"use strict";

if (!process.argv.includes("--variant")) process.argv.push("--variant", "v44");
require("./build_window1_v38_maker_only.js");
