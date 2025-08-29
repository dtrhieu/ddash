import React, { useEffect, useMemo, useState } from 'react';
import DataGrid from '../components/DataGrid';
import { ColDef } from 'ag-grid-community';
import { listProjects, listFields, listPlatforms, listRigs, listWells } from '../api';
import type { Project, Field, Platform, Rig, Well, Paginated } from '../api/types';

export default function Sheet() {
  const [rows, setRows] = useState<Project[]>([]);
  const [loading, setLoading] = useState(false);
  const [fieldMap, setFieldMap] = useState<Record<string, Field>>({});
  const [platformMap, setPlatformMap] = useState<Record<string, Platform>>({});
  const [wellMap, setWellMap] = useState<Record<string, Well>>({});
  const [rigMap, setRigMap] = useState<Record<string, Rig>>({});

  function toMap<T extends { id: string }>(items: T[]) {
    return Object.fromEntries(items.map((i) => [i.id, i]));
  }

  async function load() {
    setLoading(true);
    try {
      const [proj, rigs, fields, plats, wells] = await Promise.all([
        listProjects().catch(() => ({ count: 0, next: null, previous: null, results: [] } as Paginated<Project>)),
        listRigs().catch(() => ({ count: 0, next: null, previous: null, results: [] } as Paginated<Rig>)),
        listFields().catch(() => ({ count: 0, next: null, previous: null, results: [] } as Paginated<Field>)),
        listPlatforms().catch(() => ({ count: 0, next: null, previous: null, results: [] } as Paginated<Platform>)),
        listWells().catch(() => ({ count: 0, next: null, previous: null, results: [] } as Paginated<Well>)),
      ]);
      setRows(proj.results ?? []);
      setRigMap(toMap(rigs.results ?? []));
      setFieldMap(toMap(fields.results ?? []));
      setPlatformMap(toMap(plats.results ?? []));
      setWellMap(toMap(wells.results ?? []));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  const cols = useMemo<ColDef<Project>[]>(() => [
    { field: 'name', headerName: 'Project', pinned: 'left', width: 220 },
    { field: 'project_type', headerName: 'Type', width: 140 },
    {
      field: 'field',
      headerName: 'Field',
      width: 160,
      valueGetter: (p) => (p.data?.field ? fieldMap[p.data.field]?.name ?? p.data.field : ''),
    },
    {
      field: 'platform',
      headerName: 'Platform',
      width: 180,
      valueGetter: (p) => (p.data?.platform ? platformMap[p.data.platform]?.name ?? p.data.platform : ''),
    },
    {
      field: 'well',
      headerName: 'Well',
      width: 180,
      valueGetter: (p) => (p.data?.well ? wellMap[p.data.well]?.name ?? p.data.well : ''),
    },
    {
      field: 'rig',
      headerName: 'Rig',
      width: 160,
      valueGetter: (p) => (p.data?.rig ? rigMap[p.data.rig]?.name ?? p.data.rig : ''),
    },
    { field: 'status', headerName: 'Status', width: 140 },
    {
      field: 'planned_start',
      headerName: 'Planned Start',
      width: 140,
      valueFormatter: (p) => (p.value ? new Date(String(p.value)).toLocaleDateString() : ''),
    },
    {
      field: 'planned_end',
      headerName: 'Planned End',
      width: 140,
      valueFormatter: (p) => (p.value ? new Date(String(p.value)).toLocaleDateString() : ''),
    },
    {
      field: 'duration_days',
      headerName: 'Duration (days)',
      width: 140,
      valueGetter: (p) => {
        const s = p.data?.planned_start ? new Date(p.data.planned_start as unknown as string) : null;
        const e = p.data?.planned_end ? new Date(p.data.planned_end as unknown as string) : null;
        if (!s || !e) return null;
        const diff = Math.ceil((e.getTime() - s.getTime()) / (1000 * 60 * 60 * 24));
        return diff;
      },
    },
    {
      field: 'rig_day_rate',
      headerName: 'Rig Day Rate',
      width: 140,
      valueGetter: (p) => {
        const rig = p.data?.rig ? rigMap[p.data.rig] : undefined;
        return rig?.day_rate ?? null;
      },
      valueFormatter: (p) => {
        const v = p.value as string | number | null | undefined;
        if (v == null) return '';
        const n = typeof v === 'string' ? parseFloat(v) : v;
        if (Number.isNaN(n)) return String(v);
        return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: 0 }).format(n);
      },
    },
    {
      field: 'cost',
      headerName: 'Est. Cost',
      width: 140,
      valueGetter: (p) => {
        const s = p.data?.planned_start ? new Date(p.data.planned_start as unknown as string) : null;
        const e = p.data?.planned_end ? new Date(p.data.planned_end as unknown as string) : null;
        if (!s || !e) return null;
        const days = Math.ceil((e.getTime() - s.getTime()) / (1000 * 60 * 60 * 24));
        const rateStr = p.data?.rig ? rigMap[p.data.rig]?.day_rate : undefined;
        const rate = rateStr != null ? parseFloat(String(rateStr)) : 0;
        if (!rate || days < 0) return null;
        return days * rate;
      },
      valueFormatter: (p) => {
        const v = p.value as number | null | undefined;
        if (!v) return '';
        return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: 0 }).format(v);
      },
    },
    { field: 'actual_start', headerName: 'Actual Start', width: 140, valueFormatter: (p) => (p.value ? new Date(String(p.value)).toLocaleDateString() : '') },
    { field: 'actual_end', headerName: 'Actual End', width: 140, valueFormatter: (p) => (p.value ? new Date(String(p.value)).toLocaleDateString() : '') },
    { field: 'id', headerName: 'ID', width: 320 },
  ], [fieldMap, platformMap, wellMap, rigMap]);

  return (
    <DataGrid<Project>
      title="Projects"
      rows={rows}
      columns={cols}
      loading={loading}
      onRefresh={load}
    />
  );
}
