import React, { useEffect, useMemo, useState } from "react";
import DataGrid from "../components/DataGrid";
import type { ColDef } from "ag-grid-community";
import { listRigs } from "../api";
import type { Rig, Paginated } from "../api/types";

export default function RigsPage() {
  const [rows, setRows] = useState<Rig[]>([]);
  const [loading, setLoading] = useState(false);

  async function load() {
    setLoading(true);
    try {
      const res: Paginated<Rig> = await listRigs().catch(() => ({ count: 0, next: null, previous: null, results: [] } as any));
      setRows(res?.results ?? []);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  const cols = useMemo<ColDef<Rig>[]>(() => [
    { field: "name", headerName: "Rig", pinned: "left", width: 200 },
    { field: "rig_kind", headerName: "Kind", width: 140 },
    {
      field: "day_rate",
      headerName: "Day Rate",
      width: 160,
      valueFormatter: (p) => {
        const v = p.value as string | number | null | undefined;
        if (v == null) return "";
        const n = typeof v === "string" ? parseFloat(v) : v;
        if (Number.isNaN(n)) return String(v);
        return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", minimumFractionDigits: 0 }).format(n);
      },
    },
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
    <DataGrid<Rig>
      title="Rigs"
      rows={rows}
      columns={cols}
      loading={loading}
      onRefresh={load}
    />
  );
}
