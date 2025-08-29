import React, { useEffect, useMemo, useState } from "react";
import DataGrid from "../components/DataGrid";
import type { ColDef } from "ag-grid-community";
import { listRigs } from "../api";
import type { Rig, Paginated } from "../api/types";
import { enumLabel, formatDateTime, formatMoney } from "../utils/format";

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
    { field: "rig_kind", headerName: "Kind", width: 140, valueFormatter: (p) => enumLabel(p.value) },
    {
      field: "day_rate",
      headerName: "Day Rate",
      width: 160,
      valueFormatter: (p) => formatMoney(p.value as any),
    },
    { field: "status", headerName: "Status", width: 140, valueFormatter: (p) => enumLabel(p.value) },
    {
      field: "created_at",
      headerName: "Created",
      width: 180,
      valueFormatter: (p) => formatDateTime(p.value as any),
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
