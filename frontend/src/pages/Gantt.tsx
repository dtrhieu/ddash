import React from "react";
import GanttChart, { GanttTask } from "../components/GanttChart";

const demoTasks: GanttTask[] = [
  {
    id: "Task 1",
    name: "Kickoff",
    start: new Date(Date.now() - 2 * 24 * 3600 * 1000),
    end: new Date(Date.now() + 2 * 24 * 3600 * 1000),
    progress: 30,
  },
  {
    id: "Task 2",
    name: "Drilling",
    start: new Date(Date.now() + 3 * 24 * 3600 * 1000),
    end: new Date(Date.now() + 10 * 24 * 3600 * 1000),
    dependencies: "Task 1",
    progress: 10,
  },
];

export default function Gantt() {
  return (
    <div style={{ padding: 16 }}>
      <h2>Gantt View</h2>
      <p style={{ color: "#666", marginTop: 0 }}>
        M7.2.1: React wrapper around frappe-gantt with demo data
      </p>
      <GanttChart
        tasks={demoTasks}
        viewMode="Week"
        height={360}
        onClickTask={(t) => console.log("click", t)}
        onDateChange={(t, s, e) => console.log("date change", t, s, e)}
        onProgressChange={(t, p) => console.log("progress", t, p)}
      />
    </div>
  );
}
