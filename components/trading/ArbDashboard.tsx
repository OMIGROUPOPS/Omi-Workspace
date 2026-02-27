"use client";

import React from "react";
import { useArbData } from "./arb/hooks/useArbData";
import { useAlerts } from "./arb/hooks/useAlerts";
import { ArbDashboardHeader } from "./arb/ArbDashboardHeader";
import { MonitorTab } from "./arb/tabs/MonitorTab";
import { LiveGamesTab } from "./arb/tabs/LiveGamesTab";
import { PnlHistoryTab } from "./arb/tabs/PnlHistoryTab";
import { DepthTab } from "./arb/tabs/DepthTab";
import { OperationsTab } from "./arb/tabs/OperationsTab";

export default function ArbDashboard() {
  const data = useArbData();
  const alerts = useAlerts(data.state);

  return (
    <div className="min-h-screen bg-black text-gray-300 relative">
      {/* Scanline overlay — very subtle repeating gradient for CRT feel */}
      <div
        className="pointer-events-none fixed inset-0 z-50"
        style={{
          backgroundImage: "repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,0.03) 2px, rgba(0,0,0,0.03) 4px)",
          backgroundSize: "100% 4px",
        }}
      />
      <ArbDashboardHeader
        hasData={!!data.hasData}
        isStale={data.isStale}
        fetchError={data.fetchError}
        paused={data.paused}
        setPaused={data.setPaused}
        topTab={data.topTab}
        setTopTab={data.setTopTab}
        system={data.state?.system}
        alerts={alerts}
        fetchData={data.fetchData}
      />

      {data.topTab === "monitor" && <MonitorTab data={data} />}
      {data.topTab === "live" && <LiveGamesTab data={data} />}
      {data.topTab === "pnl_history" && <PnlHistoryTab data={data} />}
      {data.topTab === "depth" && <DepthTab data={data} />}
      {data.topTab === "operations" && <OperationsTab data={data} />}
    </div>
  );
}
