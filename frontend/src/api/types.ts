// Core API types matching backend DRF resources (minimal fields)

export type ID = number;

export type Field = {
  id: ID;
  name: string;
};

export type Platform = {
  id: ID;
  name: string;
  field: ID; // FK to Field
};

export type Rig = {
  id: ID;
  name: string;
};

export type Well = {
  id: ID;
  name: string;
  platform: ID; // FK to Platform
};

export type Project = {
  id: ID;
  name: string;
  rig: ID | null;
  platform: ID | null;
  well: ID | null;
  planned_start: string; // ISO date
  planned_end: string;   // ISO date
  duration_days?: number | null;
  cost_usd?: number | null;
};

export type Campaign = {
  id: ID;
  name: string;
  scenario: ID | null;
};

export type Paginated<T> = {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
};

export type Health = {
  status: "ok" | "degraded" | "error";
  timestamp: string;
};

export type SchemaLite = {
  endpoints: Array<{ method: string; path: string; name?: string }>;
};
