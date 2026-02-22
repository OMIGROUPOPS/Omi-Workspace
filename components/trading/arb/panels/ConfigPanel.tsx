"use client";

import React from "react";

interface Props {
  specs: any;
}

export function ConfigPanel({ specs }: Props) {
  const config = specs?.config || {};
  const deployment = specs?.deployment || {};

  const configItems = [
    { label: "Spread Min", value: `${config.spread_min_cents ?? "-"}c` },
    { label: "Min Contracts", value: config.min_contracts ?? "-" },
    { label: "Max Contracts", value: config.max_contracts ?? "-" },
    { label: "Max Cost", value: `${config.max_cost_cents ?? "-"}c` },
    { label: "GTC Enabled", value: config.enable_gtc ? "Yes" : "No" },
    { label: "Max Positions", value: config.max_concurrent_positions ?? "-" },
    { label: "Cooldown", value: `${config.cooldown_seconds ?? "-"}s` },
    { label: "Slippage", value: `${config.expected_slippage_cents ?? "-"}c` },
    { label: "K Buffer", value: `${config.price_buffer_cents ?? "-"}c` },
    { label: "PM Buffer", value: `${config.pm_price_buffer_cents ?? "-"}c` },
    { label: "Min CEQ Hold", value: `${config.min_ceq_hold ?? "-"}%` },
    { label: "Depth Cap", value: config.depth_cap ?? "-" },
  ];

  return (
    <div className="rounded-lg border border-gray-800 bg-[#111] p-3">
      <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-3">
        Configuration
      </h3>

      {/* Deployment info */}
      <div className="mb-4 p-2 rounded bg-gray-800/50">
        <div className="grid grid-cols-3 gap-2 text-xs">
          <div>
            <span className="text-gray-500">Mode</span>
            <p className={`font-bold ${deployment.execution_mode === "LIVE" ? "text-emerald-400" : "text-yellow-400"}`}>
              {deployment.execution_mode || "-"}
            </p>
          </div>
          <div>
            <span className="text-gray-500">Server</span>
            <p className="text-white">{deployment.server || "-"}</p>
          </div>
          <div>
            <span className="text-gray-500">Python</span>
            <p className="text-white font-mono">{deployment.python_version || "-"}</p>
          </div>
          <div className="col-span-3">
            <span className="text-gray-500">Git</span>
            <p className="text-white font-mono text-[10px]">
              <span className="text-emerald-400">{deployment.git_branch || "-"}</span>
              {" @ "}
              <span className="text-blue-400">{deployment.git_commit_short || "-"}</span>
              {" "}
              <span className="text-gray-500">{deployment.git_commit_msg || ""}</span>
            </p>
          </div>
        </div>
      </div>

      {/* Config grid */}
      <div className="grid grid-cols-4 gap-2">
        {configItems.map((item) => (
          <div key={item.label} className="text-xs">
            <span className="text-gray-500">{item.label}</span>
            <p className="text-white font-mono">{item.value}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
