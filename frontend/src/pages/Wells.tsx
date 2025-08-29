import React, { useEffect, useMemo, useState } from "react";
import DataGrid from "../components/DataGrid";
import type { ColDef } from "ag-grid-community";
import { listWells } from "../api";
import type { Well, Paginated } from "../api/types";

export default function WellsPage() {
  const [rows, setRows] = useState<Well[]>([]);
  const [loading, setLoading] = useState(false);

  async function load() {
    setLoading(true);
    try {
      const res: Paginated<Well> = await listWells().catch(() => ({ count: 0, next: null, previous: null, results: [] } as any));
      setRows(res?.results ?? []);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  const cols = useMemo<ColDef<Well>[]>(() => [
    { field: "name", headerName: "Well", pinned: "left", width: 200 },
    { field: "field", headerName: "Field ID", width: 240 },
    { field: "platform", headerName: "Platform ID", width: 240 },
    { field: "well_kind", headerName: "Kind", width: 160 },
    { field: "type", headerName: "Type", width: 140 },
    { field: "lat", headerName: "Lat", width: 120 },
    { field: "lon", headerName: "Lon", width: 120 },
    {
      field: "created_at",
      headerName: "Created",
      width: 180,
      valueFormatter: (p) => (p.value ? new Date(p.value as string).toLocaleString() : ""),
    },
    { field: "id", headerName: "ID", width: 320 },
  ], []);

  return (
    <DataGrid<Well>
      title="Wells"
      rows={rows}
      columns={cols}
      loading={loading}
      onRefresh={load}
    />
  );
}
