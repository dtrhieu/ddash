import React, { useEffect, useMemo, useState } from "react";
import DataGrid from "../components/DataGrid";
import type { ColDef } from "ag-grid-community";
import { listFields } from "../api";
import type { Field, Paginated } from "../api/types";

export default function FieldsPage() {
  const [rows, setRows] = useState<Field[]>([]);
  const [loading, setLoading] = useState(false);

  async function load() {
    setLoading(true);
    try {
      const res: Paginated<Field> = await listFields().catch(() => ({ count: 0, next: null, previous: null, results: [] } as any));
      setRows(res?.results ?? []);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  const cols = useMemo<ColDef<Field>[]>(() => [
    { field: "name", headerName: "Name", pinned: "left", width: 200 },
    {
      field: "created_at",
      headerName: "Created",
      width: 180,
      valueFormatter: (p) => (p.value ? new Date(p.value as string).toLocaleString() : ""),
    },
    { field: "id", headerName: "ID", width: 320 },
  ], []);

  return (
    <DataGrid<Field>
      title="Fields"
      rows={rows}
      columns={cols}
      loading={loading}
      onRefresh={load}
    />
  );
}
