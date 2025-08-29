// Core API types matching backend DRF resources (aligned with serializers)

// Backend uses UUIDs for most domain models. Represent as string in TS.
export type ID = string;

export type Timestamp = string; // ISO 8601
export type ISODate = string;   // YYYY-MM-DD

// Core
export type Field = {
  id: ID;
  name: string;
  created_at: Timestamp;
};

export type PlatformStatus = "operating" | "maintenance" | "shutdown";
export type Platform = {
  id: ID;
  field: ID; // FK to Field
  name: string;
  status: PlatformStatus;
  created_at: Timestamp;
};

export type RigKind = "jackup" | "mmwu" | "hwu" | "other";
export type RigStatus = "active" | "standby" | "maintenance";
export type Rig = {
  id: ID;
  name: string;
  rig_kind: RigKind;
  day_rate: string; // Decimal serialized as string
  status: RigStatus;
  created_at: Timestamp;
};

export type WellKind = "platform_well" | "exploration_open_location";
export type WellType = "exploration" | "development";
export type Well = {
  id: ID;
  name: string;
  field: ID;
  platform: ID | null; // null for exploration open location
  well_kind: WellKind;
  type: WellType;
  lat: string | null; // decimals come as strings
  lon: string | null;
  created_at: Timestamp;
};

export type MaintenanceWindow = {
  id: ID;
  platform: ID;
  start_date: ISODate;
  end_date: ISODate;
  reason: string;
  created_at: Timestamp;
};

// Scheduling
export type ScenarioStatus = "draft" | "approved" | "archived";
export type Scenario = {
  id: ID;
  name: string;
  status: ScenarioStatus;
  created_by: ID; // user id
  created_at: Timestamp;
};

export type ProjectType =
  | "drilling"
  | "workover"
  | "plug_and_abandon"
  | "fracturing"
  | "platform_service"
  | "uwild"
  | "rig_overhaul"
  | "other";
export type ProjectStatus = "planned" | "in_progress" | "complete" | "on_hold" | "canceled";
export type Project = {
  id: ID;
  name: string;
  project_type: ProjectType;
  field: ID | null;
  platform: ID | null;
  well: ID | null;
  rig: ID | null;
  status: ProjectStatus;
  planned_start: ISODate;
  planned_end: ISODate;
  actual_start: ISODate | null;
  actual_end: ISODate | null;
  dependencies: Record<string, unknown>;
  extras: Record<string, unknown>;
  created_at: Timestamp;
};

export type CampaignType = "rig_campaign" | "field_operations";
export type Campaign = {
  id: ID;
  scenario: ID;
  name: string;
  campaign_type: CampaignType;
  rig: ID | null;
  field: ID | null;
  created_at: Timestamp;
};

export type CampaignProject = {
  id: ID;
  campaign: ID;
  project: ID;
  created_at: Timestamp;
};

export type CalcRunStatus = "pending" | "running" | "success" | "failed";
export type CalcRun = {
  id: ID;
  scenario: ID;
  status: CalcRunStatus;
  params: Record<string, unknown>;
  results: Record<string, unknown>;
  created_by: ID;
  created_at: Timestamp;
  completed_at: Timestamp | null;
};

// Utilities
export type Paginated<T> = {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
};

export type Health = {
  status: "ok" | "degraded" | "error";
  timestamp: Timestamp;
};

export type SchemaLite = {
  endpoints: Array<{ method: string; path: string; name?: string }>;
};
