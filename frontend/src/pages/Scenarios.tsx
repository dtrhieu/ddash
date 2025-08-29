import React, { useEffect, useMemo, useState } from "react";
import DataGrid from "../components/DataGrid";
import type { ColDef } from "ag-grid-community";
import { listScenarios } from "../api";
import type { Scenario, Paginated } from "../api/types";
import { enumLabel, formatDateTime } from "../utils/format";

export default function ScenariosPage() {
  const [rows, setRows] = useState<Scenario[]>([]);
  const [loading, setLoading] = useState(false);

  async function load() {
    setLoading(true);
    try {
      const res: Paginated<Scenario> = await listScenarios().catch(
        () => ({ count: 0, next: null, previous: null, results: [] } as any)
      );
      setRows(res?.results ?? []);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  const cols = useMemo<ColDef<Scenario>[]>(() => [
    { field: "name", headerName: "Scenario", pinned: "left", width: 220 },
    { field: "status", headerName: "Status", width: 140, valueFormatter: (p) => enumLabel(p.value as any) },
    { field: "created_by", headerName: "Created By (User ID)", width: 220 },
    { field: "created_at", headerName: "Created", width: 180, valueFormatter: (p) => formatDateTime(p.value as any) },
    { field: "id", headerName: "ID", width: 320 },
  ], []);

  return (
    <DataGrid<Scenario>
      title="Scenarios"
      rows={rows}
      columns={cols}
      loading={loading}
      onRefresh={load}
    />
  );
}
