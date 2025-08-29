import React, { useEffect, useMemo, useState } from "react";
import DataGrid from "../components/DataGrid";
import type { ColDef } from "ag-grid-community";
import { listCalcRuns, listScenarios } from "../api";
import type { CalcRun, Scenario, Paginated } from "../api/types";
import { enumLabel, formatDateTime } from "../utils/format";

export default function CalcRunsPage() {
  const [rows, setRows] = useState<CalcRun[]>([]);
  const [loading, setLoading] = useState(false);
  const [scenarioMap, setScenarioMap] = useState<Record<string, Scenario>>({});

  function toMap<T extends { id: string }>(items: T[]) {
    return Object.fromEntries(items.map((i) => [i.id, i]));
  }

  async function load() {
    setLoading(true);
    try {
      const [runs, scens]: [Paginated<CalcRun>, Paginated<Scenario>] = await Promise.all([
        listCalcRuns().catch(() => ({ count: 0, next: null, previous: null, results: [] } as any)),
        listScenarios().catch(() => ({ count: 0, next: null, previous: null, results: [] } as any)),
      ]);
      setRows(runs?.results ?? []);
      setScenarioMap(toMap(scens?.results ?? []));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  const cols = useMemo<ColDef<CalcRun>[]>(() => [
    { field: "scenario", headerName: "Scenario", width: 220, valueGetter: (p) => (p.data?.scenario ? scenarioMap[p.data.scenario]?.name ?? p.data.scenario : "") },
    { field: "status", headerName: "Status", width: 140, valueFormatter: (p) => enumLabel(p.value as any) },
    { field: "created_by", headerName: "Created By (User ID)", width: 220 },
    { field: "created_at", headerName: "Created", width: 180, valueFormatter: (p) => formatDateTime(p.value as any) },
    { field: "completed_at", headerName: "Completed", width: 180, valueFormatter: (p) => formatDateTime(p.value as any) },
    { field: "id", headerName: "ID", width: 320 },
  ], [scenarioMap]);

  return (
    <DataGrid<CalcRun>
      title="Calculation Runs"
      rows={rows}
      columns={cols}
      loading={loading}
      onRefresh={load}
    />
  );
}
