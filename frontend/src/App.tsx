import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Sidebar } from "./components";
import Sheet from "./pages/Sheet";
import Gantt from "./pages/Gantt";
import Fields from "./pages/Fields";
import Platforms from "./pages/Platforms";
import Rigs from "./pages/Rigs";
import Wells from "./pages/Wells";
import Scenarios from "./pages/Scenarios";
import Campaigns from "./pages/Campaigns";
import MaintenanceWindows from "./pages/MaintenanceWindows";
import CalcRuns from "./pages/CalcRuns";

export default function App() {
  return (
    <BrowserRouter>
      <div className="flex h-screen">
        <Sidebar />
        <main className="flex-1 overflow-auto">
          <Routes>
            <Route path="/" element={<Navigate to="/sheet" replace />} />
            <Route path="/sheet" element={<Sheet />} />
            <Route path="/gantt" element={<Gantt />} />
            <Route path="/fields" element={<Fields />} />
            <Route path="/platforms" element={<Platforms />} />
            <Route path="/rigs" element={<Rigs />} />
            <Route path="/wells" element={<Wells />} />
            <Route path="/scenarios" element={<Scenarios />} />
            <Route path="/campaigns" element={<Campaigns />} />
            <Route path="/maintenance-windows" element={<MaintenanceWindows />} />
            <Route path="/calc-runs" element={<CalcRuns />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
