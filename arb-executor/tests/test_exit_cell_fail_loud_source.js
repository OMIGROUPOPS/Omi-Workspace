"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");

const file = path.resolve(__dirname, "../live_v4.py");
const source = fs.readFileSync(file, "utf8");
const start = source.indexOf("    def exit_rule_for(self, category, price_cents):");
const end = source.indexOf("\n    def get_category", start);
assert(start >= 0 && end > start);
const method = source.slice(start, end);
assert(!method.includes('return (15, "exit")'));
assert(method.includes('self._log("CRITICAL_exit_cell_missing", receipt)'));
assert(method.includes('self._log("exit_cell_nearest_borrowed"'));
assert(method.includes("MIN_ABSOLUTE_DISTANCE_THEN_LOWER_CELL"));
assert(method.includes("raise RuntimeError"));
assert(source.includes("DEAD_SPREAD_THRESHOLD = 20"));
assert(source.includes("if spread <= 2"));

process.stdout.write("exit missing-cell fail-loud source tests: PASS (8 assertions)\n");
