import React, { useEffect, useMemo, useState } from "react";
import DataGrid from "../components/DataGrid";
import type { ColDef } from "ag-grid-community";
import { listMaintenanceWindows, listPlatforms } from "../api";
import type { MaintenanceWindow, Platform, Paginated } from "../api/types";
import { formatDate, formatDateTime } from "../utils/format";

export default function MaintenanceWindowsPage() {
  const [rows, setRows] = useState<MaintenanceWindow[]>([]);
  const [loading, setLoading] = useState(false);
  const [platformMap, setPlatformMap] = useState<Record<string, Platform>>({});

  function toMap<T extends { id: string }>(items: T[]) {
    return Object.fromEntries(items.map((i) => [i.id, i]));
  }

  async function load() {
    setLoading(true);
    try {
      const [mws, plats]: [Paginated<MaintenanceWindow>, Paginated<Platform>] = await Promise.all([
        listMaintenanceWindows().catch(() => ({ count: 0, next: null, previous: null, results: [] } as any)),
        listPlatforms().catch(() => ({ count: 0, next: null, previous: null, results: [] } as any)),
      ]);
      setRows(mws?.results ?? []);
      setPlatformMap(toMap(plats?.results ?? []));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  const cols = useMemo<ColDef<MaintenanceWindow>[]>(() => [
    { field: "platform", headerName: "Platform", width: 220, valueGetter: (p) => (p.data?.platform ? platformMap[p.data.platform]?.name ?? p.data.platform : "") },
    { field: "start_date", headerName: "Start", width: 140, valueFormatter: (p) => formatDate(p.value as any) },
    { field: "end_date", headerName: "End", width: 140, valueFormatter: (p) => formatDate(p.value as any) },
    { field: "reason", headerName: "Reason", width: 320 },
    { field: "created_at", headerName: "Created", width: 180, valueFormatter: (p) => formatDateTime(p.value as any) },
    { field: "id", headerName: "ID", width: 320 },
  ], [platformMap]);

  return (
    <DataGrid<MaintenanceWindow>
      title="Maintenance Windows"
      rows={rows}
      columns={cols}
      loading={loading}
      onRefresh={load}
    />
  );
}
