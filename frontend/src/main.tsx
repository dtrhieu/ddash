import React from "react";
import { createRoot } from "react-dom/client";

function App() {
  return <div style={{ fontFamily: "system-ui, sans-serif", padding: 16 }}>
    <h1>Drilling Campaign Tracker</h1>
    <p>Frontend scaffold will arrive in M6.</p>
  </div>;
}

const el = document.getElementById("root");
if (el) {
  createRoot(el).render(<App />);
}
