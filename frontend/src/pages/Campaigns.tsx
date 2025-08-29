import React, { useEffect, useMemo, useState } from "react";
import DataGrid from "../components/DataGrid";
import type { ColDef } from "ag-grid-community";
import { listCampaigns, listScenarios, listRigs, listFields } from "../api";
import type { Campaign, Scenario, Rig, Field, Paginated } from "../api/types";
import { enumLabel, formatDateTime } from "../utils/format";

export default function CampaignsPage() {
  const [rows, setRows] = useState<Campaign[]>([]);
  const [loading, setLoading] = useState(false);
  const [scenarioMap, setScenarioMap] = useState<Record<string, Scenario>>({});
  const [rigMap, setRigMap] = useState<Record<string, Rig>>({});
  const [fieldMap, setFieldMap] = useState<Record<string, Field>>({});

  function toMap<T extends { id: string }>(items: T[]) {
    return Object.fromEntries(items.map((i) => [i.id, i]));
  }

  async function load() {
    setLoading(true);
    try {
      const [camps, scens, rigs, fields]: [
        Paginated<Campaign>,
        Paginated<Scenario>,
        Paginated<Rig>,
        Paginated<Field>
      ] = await Promise.all([
        listCampaigns().catch(() => ({ count: 0, next: null, previous: null, results: [] } as any)),
        listScenarios().catch(() => ({ count: 0, next: null, previous: null, results: [] } as any)),
        listRigs().catch(() => ({ count: 0, next: null, previous: null, results: [] } as any)),
        listFields().catch(() => ({ count: 0, next: null, previous: null, results: [] } as any)),
      ]);
      setRows(camps?.results ?? []);
      setScenarioMap(toMap(scens?.results ?? []));
      setRigMap(toMap(rigs?.results ?? []));
      setFieldMap(toMap(fields?.results ?? []));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  const cols = useMemo<ColDef<Campaign>[]>(() => [
    { field: "name", headerName: "Campaign", pinned: "left", width: 240 },
    { field: "campaign_type", headerName: "Type", width: 160, valueFormatter: (p) => enumLabel(p.value as any) },
    { field: "scenario", headerName: "Scenario", width: 220, valueGetter: (p) => (p.data?.scenario ? scenarioMap[p.data.scenario]?.name ?? p.data.scenario : "") },
    { field: "rig", headerName: "Rig", width: 200, valueGetter: (p) => (p.data?.rig ? rigMap[p.data.rig]?.name ?? p.data.rig : "") },
    { field: "field", headerName: "Field", width: 200, valueGetter: (p) => (p.data?.field ? fieldMap[p.data.field]?.name ?? p.data.field : "") },
    { field: "created_at", headerName: "Created", width: 180, valueFormatter: (p) => formatDateTime(p.value as any) },
    { field: "id", headerName: "ID", width: 320 },
  ], [scenarioMap, rigMap, fieldMap]);

  return (
    <DataGrid<Campaign>
      title="Campaigns"
      rows={rows}
      columns={cols}
      loading={loading}
      onRefresh={load}
    />
  );
}
