import React, { useEffect, useMemo, useState } from "react";
import DataGrid from "../components/DataGrid";
import type { ColDef } from "ag-grid-community";
import { listPlatforms, listFields } from "../api";
import type { Platform, Field, Paginated } from "../api/types";
import { enumLabel, formatDateTime } from "../utils/format";

export default function PlatformsPage() {
  const [rows, setRows] = useState<Platform[]>([]);
  const [loading, setLoading] = useState(false);
  const [fieldMap, setFieldMap] = useState<Record<string, Field>>({});

  function toMap<T extends { id: string }>(items: T[]) {
    return Object.fromEntries(items.map((i) => [i.id, i]));
  }

  async function load() {
    setLoading(true);
    try {
      const [plats, fields]: [Paginated<Platform>, Paginated<Field>] = await Promise.all([
        listPlatforms().catch(() => ({ count: 0, next: null, previous: null, results: [] } as any)),
        listFields().catch(() => ({ count: 0, next: null, previous: null, results: [] } as any)),
      ]);
      setRows(plats?.results ?? []);
      setFieldMap(toMap(fields?.results ?? []));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  const cols = useMemo<ColDef<Platform>[]>(() => [
    { field: "name", headerName: "Platform", pinned: "left", width: 200 },
    {
      field: "field",
      headerName: "Field",
      width: 200,
      valueGetter: (p) => (p.data?.field ? fieldMap[p.data.field]?.name ?? p.data.field : ""),
    },
    { field: "status", headerName: "Status", width: 140, valueFormatter: (p) => enumLabel(p.value) },
    {
      field: "created_at",
      headerName: "Created",
      width: 180,
      valueFormatter: (p) => formatDateTime(p.value as any),
    },
    { field: "id", headerName: "ID", width: 320 },
  ], [fieldMap]);

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
