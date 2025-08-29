import React, { useState, useMemo } from 'react';
import { AgGridReact } from 'ag-grid-react';
import { themeBalham } from 'ag-grid-community';
import { ColDef } from 'ag-grid-community';
import { CampaignWell } from '../types';

// Mock data for initial testing
const mockCampaignWells: CampaignWell[] = [
  {
    id: '1',
    campaign_id: 'camp1',
    well_id: 'well1',
    rig_id: 'rig1',
    planned_start: '2024-01-15',
    planned_end: '2024-02-15',
    dependencies: {},
    campaign: { id: 'camp1', name: 'Campaign Alpha', start_date: '2024-01-01', end_date: '2024-03-01', scenario_id: 'scen1' },
    well: { id: 'well1', name: 'Well-001', field: 'North Field', type: 'Exploration' },
    rig: { id: 'rig1', name: 'Rig-01', day_rate: 50000, status: 'Active' }
  },
  {
    id: '2',
    campaign_id: 'camp1',
    well_id: 'well2',
    rig_id: 'rig2',
    planned_start: '2024-02-01',
    planned_end: '2024-03-01',
    dependencies: {},
    campaign: { id: 'camp1', name: 'Campaign Alpha', start_date: '2024-01-01', end_date: '2024-03-01', scenario_id: 'scen1' },
    well: { id: 'well2', name: 'Well-002', field: 'North Field', type: 'Development' },
    rig: { id: 'rig2', name: 'Rig-02', day_rate: 55000, status: 'Active' }
  },
  {
    id: '3',
    campaign_id: 'camp2',
    well_id: 'well3',
    rig_id: 'rig1',
    planned_start: '2024-03-01',
    planned_end: '2024-04-01',
    dependencies: {},
    campaign: { id: 'camp2', name: 'Campaign Beta', start_date: '2024-03-01', end_date: '2024-05-01', scenario_id: 'scen1' },
    well: { id: 'well3', name: 'Well-003', field: 'South Field', type: 'Exploration' },
    rig: { id: 'rig1', name: 'Rig-01', day_rate: 50000, status: 'Active' }
  }
];

export default function Sheet() {
  const [rowData] = useState<CampaignWell[]>(mockCampaignWells);

  const columnDefs = useMemo<ColDef[]>(() => [
    {
      field: 'rig_name',
      headerName: 'Rig',
      width: 120,
      sortable: true,
      filter: true,
      pinned: 'left',
      valueGetter: (p) => p.data?.rig?.name ?? ''
    },
    {
      field: 'well_name',
      headerName: 'Well',
      width: 120,
      sortable: true,
      filter: true,
      pinned: 'left',
      valueGetter: (p) => p.data?.well?.name ?? ''
    },
    {
      field: 'well_field',
      headerName: 'Field',
      width: 120,
      sortable: true,
      filter: true,
      valueGetter: (p) => p.data?.well?.field ?? ''
    },
    {
      field: 'well_type',
      headerName: 'Type',
      width: 120,
      sortable: true,
      filter: true,
      valueGetter: (p) => p.data?.well?.type ?? ''
    },
    {
      field: 'planned_start',
      headerName: 'Planned Start',
      width: 130,
      sortable: true,
      filter: true,
      valueFormatter: (params) => {
        if (!params.value) return '';
        return new Date(params.value).toLocaleDateString();
      }
    },
    {
      field: 'planned_end',
      headerName: 'Planned End',
      width: 130,
      sortable: true,
      filter: true,
      valueFormatter: (params) => {
        if (!params.value) return '';
        return new Date(params.value).toLocaleDateString();
      }
    },
    {
      field: 'duration',
      headerName: 'Duration (days)',
      width: 130,
      sortable: true,
      filter: true,
      valueGetter: (params) => {
        const start = new Date(params.data.planned_start);
        const end = new Date(params.data.planned_end);
        const diffTime = Math.abs(end.getTime() - start.getTime());
        return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
      }
    },
    {
      field: 'rig_day_rate',
      headerName: 'Day Rate ($)',
      width: 120,
      sortable: true,
      filter: true,
      valueGetter: (p) => p.data?.rig?.day_rate ?? null,
      valueFormatter: (params) => {
        if (params.value == null) return '';
        return new Intl.NumberFormat('en-US', {
          style: 'currency',
          currency: 'USD',
          minimumFractionDigits: 0,
          maximumFractionDigits: 0,
        }).format(params.value);
      }
    },
    {
      field: 'cost',
      headerName: 'Total Cost ($)',
      width: 130,
      sortable: true,
      filter: true,
      valueGetter: (params) => {
        const start = new Date(params.data.planned_start);
        const end = new Date(params.data.planned_end);
        const diffTime = Math.abs(end.getTime() - start.getTime());
        const days = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        return days * (params.data.rig?.day_rate || 0);
      },
      valueFormatter: (params) => {
        if (!params.value) return '';
        return new Intl.NumberFormat('en-US', {
          style: 'currency',
          currency: 'USD',
          minimumFractionDigits: 0,
          maximumFractionDigits: 0,
        }).format(params.value);
      }
    },
    {
      field: 'campaign_name',
      headerName: 'Campaign',
      width: 150,
      sortable: true,
      filter: true,
      valueGetter: (p) => p.data?.campaign?.name ?? ''
    }
  ], []);

  const defaultColDef = useMemo<ColDef>(() => ({
    resizable: true,
    sortable: true,
    filter: true,
  }), []);

  return (
    <div className="sheet-container" style={{ height: '100vh', padding: '20px' }}>
      <h1>Drilling Campaign - Sheet View</h1>
      <div
        style={{
          height: 'calc(100vh - 120px)',
          width: '100%'
        }}
      >
        <AgGridReact
          theme={themeBalham}
          rowData={rowData}
          columnDefs={columnDefs}
          defaultColDef={defaultColDef}
          pagination={true}
          paginationPageSize={20}
          paginationPageSizeSelector={[10, 20, 50, 100]}
          animateRows={true}
        />
      </div>
    </div>
  );
}
