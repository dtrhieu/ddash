import React from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import { ModuleRegistry, AllCommunityModule } from 'ag-grid-community';
import "./index.css";

// Register AG Grid Community modules once at app bootstrap
ModuleRegistry.registerModules([AllCommunityModule]);

const el = document.getElementById("root");
if (el) {
  createRoot(el).render(<App />);
}
