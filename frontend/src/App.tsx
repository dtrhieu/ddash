import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Sidebar } from "./components";
import Sheet from "./pages/Sheet";
import Gantt from "./pages/Gantt";

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
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
