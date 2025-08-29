// Export all types from this directory
// export * from './api'; // Will be added in M6.2

// Type definitions for Drilling Campaign Tracker

export interface Rig {
  id: string;
  name: string;
  day_rate: number;
  status: 'Active' | 'Standby' | 'Maintenance';
}

export interface Well {
  id: string;
  name: string;
  field: string;
  type: 'Exploration' | 'Development';
}

export interface Campaign {
  id: string;
  name: string;
  start_date: string;
  end_date: string;
  scenario_id: string;
}

export interface Scenario {
  id: string;
  name: string;
  status: 'Draft' | 'Approved' | 'Archived';
  created_by: string;
  created_at: string;
}

export interface CampaignWell {
  id: string;
  campaign_id: string;
  well_id: string;
  rig_id: string;
  planned_start: string;
  planned_end: string;
  actual_start?: string;
  actual_end?: string;
  dependencies: Record<string, unknown>;
  // Joined data for display
  campaign?: Campaign;
  well?: Well;
  rig?: Rig;
}

export interface CalcRun {
  id: string;
  scenario_id: string;
  status: 'Pending' | 'Running' | 'Success' | 'Failed';
  params: Record<string, unknown>;
  results: Record<string, unknown>;
  created_by: string;
  created_at: string;
  completed_at?: string;
}

export interface AuditLog {
  id: number;
  user_id: string;
  entity: string;
  entity_id: string;
  action: 'Create' | 'Update' | 'Delete';
  before: Record<string, unknown>;
  after: Record<string, unknown>;
  at: string;
}

// AG Grid specific types
export interface GridColumn {
  field: string;
  headerName: string;
  width?: number;
  sortable?: boolean;
  filter?: boolean;
  editable?: boolean;
  cellRenderer?: string;
  valueFormatter?: (params: { value: unknown }) => string;
}
