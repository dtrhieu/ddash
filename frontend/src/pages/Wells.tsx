import React, { useEffect, useMemo, useState } from "react";
import DataGrid from "../components/DataGrid";
import type { ColDef } from "ag-grid-community";
import { listWells, listFields, listPlatforms } from "../api";
import type { Well, Field, Platform, Paginated } from "../api/types";
import { enumLabel, formatDateTime } from "../utils/format";

export default function WellsPage() {
  const [rows, setRows] = useState<Well[]>([]);
  const [loading, setLoading] = useState(false);
  const [fieldMap, setFieldMap] = useState<Record<string, Field>>({});
  const [platformMap, setPlatformMap] = useState<Record<string, Platform>>({});

  function toMap<T extends { id: string }>(items: T[]) {
    return Object.fromEntries(items.map((i) => [i.id, i]));
  }

  async function load() {
    setLoading(true);
    try {
      const [wells, fields, plats]: [Paginated<Well>, Paginated<Field>, Paginated<Platform>] = await Promise.all([
        listWells().catch(() => ({ count: 0, next: null, previous: null, results: [] } as any)),
        listFields().catch(() => ({ count: 0, next: null, previous: null, results: [] } as any)),
        listPlatforms().catch(() => ({ count: 0, next: null, previous: null, results: [] } as any)),
      ]);
      setRows(wells?.results ?? []);
      setFieldMap(toMap(fields?.results ?? []));
      setPlatformMap(toMap(plats?.results ?? []));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  const cols = useMemo<ColDef<Well>[]>(() => [
    { field: "name", headerName: "Well", pinned: "left", width: 200 },
    {
      field: "field",
      headerName: "Field",
      width: 180,
      valueGetter: (p) => (p.data?.field ? fieldMap[p.data.field]?.name ?? p.data.field : ""),
    },
    {
      field: "platform",
      headerName: "Platform",
      width: 180,
      valueGetter: (p) => (p.data?.platform ? platformMap[p.data.platform]?.name ?? p.data.platform : ""),
    },
    { field: "well_kind", headerName: "Kind", width: 160, valueFormatter: (p) => enumLabel(p.value) },
    { field: "type", headerName: "Type", width: 140, valueFormatter: (p) => enumLabel(p.value) },
    { field: "lat", headerName: "Lat", width: 120 },
    { field: "lon", headerName: "Lon", width: 120 },
    { field: "created_at", headerName: "Created", width: 180, valueFormatter: (p) => formatDateTime(p.value as any) },
    { field: "id", headerName: "ID", width: 320 },
  ], [fieldMap, platformMap]);

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
