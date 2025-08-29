import React, { useEffect, useMemo, useState } from "react";
import DataGrid from "../components/DataGrid";
import type { ColDef } from "ag-grid-community";
import { listPlatforms } from "../api";
import type { Platform, Paginated } from "../api/types";

export default function PlatformsPage() {
  const [rows, setRows] = useState<Platform[]>([]);
  const [loading, setLoading] = useState(false);

  async function load() {
    setLoading(true);
    try {
      const res: Paginated<Platform> = await listPlatforms().catch(() => ({ count: 0, next: null, previous: null, results: [] } as any));
      setRows(res?.results ?? []);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  const cols = useMemo<ColDef<Platform>[]>(() => [
    { field: "name", headerName: "Platform", pinned: "left", width: 200 },
    { field: "field", headerName: "Field ID", width: 240 },
    { field: "status", headerName: "Status", width: 140 },
    {
      field: "created_at",
      headerName: "Created",
      width: 180,
      valueFormatter: (p) => (p.value ? new Date(p.value as string).toLocaleString() : ""),
    },
    { field: "id", headerName: "ID", width: 320 },
  ], []);

  return (
    <DataGrid<Platform>
      title="Platforms"
      rows={rows}
      columns={cols}
      loading={loading}
      onRefresh={load}
    />
  );
}
