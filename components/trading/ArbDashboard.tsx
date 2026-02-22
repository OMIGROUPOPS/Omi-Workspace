"use client";

import React from "react";
import { useArbData } from "./arb/hooks/useArbData";
import { useAlerts } from "./arb/hooks/useAlerts";
import { ArbDashboardHeader } from "./arb/ArbDashboardHeader";
import { MonitorTab } from "./arb/tabs/MonitorTab";
import { PnlHistoryTab } from "./arb/tabs/PnlHistoryTab";
import { DepthTab } from "./arb/tabs/DepthTab";
import { OperationsTab } from "./arb/tabs/OperationsTab";

export default function ArbDashboard() {
  const data = useArbData();
  const alerts = useAlerts(data.state);

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-gray-200">
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
      {data.topTab === "pnl_history" && <PnlHistoryTab data={data} />}
      {data.topTab === "depth" && <DepthTab data={data} />}
      {data.topTab === "operations" && <OperationsTab data={data} />}
    </div>
  );
}
