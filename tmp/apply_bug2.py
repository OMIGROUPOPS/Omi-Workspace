#!/usr/bin/env python3
"""Apply Bug 2 fix: cell re-classification at fill time."""

with open('/root/Omi-Workspace/arb-executor/live_v3.py', 'r') as f:
    content = f.read()

# PATH 1: Insert cell re-lookup after entry_filled log, before exit cancel block
old_path1 = """                    }, ticker=tk)

                    # Cancel ALL existing exit sells before posting new ones"""

new_path1 = """                    }, ticker=tk)

                    # Re-classify cell based on fill_price (may differ from anchor)
                    old_cell = pos.cell_name
                    old_exit_cents = pos.cell_cfg.get("exit_cents", 0) if pos.cell_cfg else 0
                    fill_cell, fill_cell_cfg = self.cell_lookup(pos.category, pos.direction, fill_price)
                    if fill_cell != old_cell:
                        if fill_cell_cfg is None:
                            fill_cell_cfg = {"exit_cents": 15, "strategy": pos.cell_cfg.get("strategy", "noDCA")}
                            self._log("cell_drift_to_inactive", {
                                "old_cell": old_cell, "new_cell": fill_cell,
                                "anchor_price": pos.entry_price, "fill_price": fill_price,
                                "drift_cents": pos.entry_price - fill_price,
                                "old_exit_cents": old_exit_cents, "new_exit_cents": 15,
                                "direction": pos.direction,
                            }, ticker=tk)
                        else:
                            self._log("cell_reclassified", {
                                "old_cell": old_cell, "new_cell": fill_cell,
                                "anchor_price": pos.entry_price, "fill_price": fill_price,
                                "drift_cents": pos.entry_price - fill_price,
                                "old_exit_cents": old_exit_cents,
                                "new_exit_cents": fill_cell_cfg["exit_cents"],
                                "direction": pos.direction,
                            }, ticker=tk)
                        pos.cell_name = fill_cell
                        pos.cell_cfg = fill_cell_cfg

                    # Cancel ALL existing exit sells before posting new ones"""

assert old_path1 in content, "Path 1 anchor not found!"
content = content.replace(old_path1, new_path1, 1)

# PATH 2: Insert cell re-lookup in cadence_repost_fill_detected, before the log event
old_path2 = """                        pos.entry_filled_ts = time.time()
                        self._log("cadence_repost_fill_detected", {
                            "filled_qty": old_filled, "price": pos.entry_price,
                        }, ticker=tk)
                        continue"""

new_path2 = """                        pos.entry_filled_ts = time.time()
                        # Re-classify cell based on fill price
                        old_cell = pos.cell_name
                        old_exit_cents = pos.cell_cfg.get("exit_cents", 0) if pos.cell_cfg else 0
                        fill_cell, fill_cell_cfg = self.cell_lookup(pos.category, pos.direction, pos.entry_price)
                        if fill_cell != old_cell:
                            if fill_cell_cfg is None:
                                fill_cell_cfg = {"exit_cents": 15, "strategy": pos.cell_cfg.get("strategy", "noDCA")}
                                self._log("cell_drift_to_inactive", {
                                    "old_cell": old_cell, "new_cell": fill_cell,
                                    "anchor_price": pos.entry_price, "fill_price": pos.entry_price,
                                    "drift_cents": 0,
                                    "old_exit_cents": old_exit_cents, "new_exit_cents": 15,
                                    "direction": pos.direction,
                                }, ticker=tk)
                            else:
                                self._log("cell_reclassified", {
                                    "old_cell": old_cell, "new_cell": fill_cell,
                                    "anchor_price": pos.entry_price, "fill_price": pos.entry_price,
                                    "drift_cents": 0,
                                    "old_exit_cents": old_exit_cents,
                                    "new_exit_cents": fill_cell_cfg["exit_cents"],
                                    "direction": pos.direction,
                                }, ticker=tk)
                            pos.cell_name = fill_cell
                            pos.cell_cfg = fill_cell_cfg
                        self._log("cadence_repost_fill_detected", {
                            "filled_qty": old_filled, "price": pos.entry_price,
                        }, ticker=tk)
                        continue"""

assert old_path2 in content, "Path 2 anchor not found!"
content = content.replace(old_path2, new_path2, 1)

with open('/root/Omi-Workspace/arb-executor/live_v3.py', 'w') as f:
    f.write(content)

print("Bug 2 patches applied successfully.")
