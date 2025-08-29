export * from "./types";
export * from "./errors";
export { ApiClient, api } from "./client";

// Convenience endpoint functions using the default client
import { api as defaultClient } from "./client";
import type {
  Health,
  SchemaLite,
  Paginated,
  Field,
  Platform,
  Rig,
  Well,
  MaintenanceWindow,
  Scenario,
  Project,
  Campaign,
  CampaignProject,
  CalcRun,
  ID,
} from "./types";

export const getHealth = () => defaultClient.get<Health>("/health");
export const getSchemaLite = () => defaultClient.get<SchemaLite>("/schema-lite");

// Query helper
function toQuery(params?: URLSearchParams | Record<string, string>) {
  if (!params) return "";
  if (params instanceof URLSearchParams) {
    const s = params.toString();
    return s ? `?${s}` : "";
  }
  const s = new URLSearchParams(params).toString();
  return s ? `?${s}` : "";
}

// Generic helpers for path building
const path = {
  fields: "/fields/",
  platforms: "/platforms/",
  rigs: "/rigs/",
  wells: "/wells/",
  maintenanceWindows: "/maintenance-windows/",
  scenarios: "/scenarios/",
  projects: "/projects/",
  campaigns: "/campaigns/",
  campaignProjects: "/campaign-projects/",
  calcRuns: "/calc-runs/",
} as const;

// Lists
export const listFields = (params?: URLSearchParams | Record<string, string>) =>
  defaultClient.get<Paginated<Field>>(`${path.fields}${toQuery(params)}`);
export const listPlatforms = (params?: URLSearchParams | Record<string, string>) =>
  defaultClient.get<Paginated<Platform>>(`${path.platforms}${toQuery(params)}`);
export const listRigs = (params?: URLSearchParams | Record<string, string>) =>
  defaultClient.get<Paginated<Rig>>(`${path.rigs}${toQuery(params)}`);
export const listWells = (params?: URLSearchParams | Record<string, string>) =>
  defaultClient.get<Paginated<Well>>(`${path.wells}${toQuery(params)}`);
export const listMaintenanceWindows = (params?: URLSearchParams | Record<string, string>) =>
  defaultClient.get<Paginated<MaintenanceWindow>>(`${path.maintenanceWindows}${toQuery(params)}`);
export const listScenarios = (params?: URLSearchParams | Record<string, string>) =>
  defaultClient.get<Paginated<Scenario>>(`${path.scenarios}${toQuery(params)}`);
export const listProjects = (params?: URLSearchParams | Record<string, string>) =>
  defaultClient.get<Paginated<Project>>(`${path.projects}${toQuery(params)}`);
export const listCampaigns = (params?: URLSearchParams | Record<string, string>) =>
  defaultClient.get<Paginated<Campaign>>(`${path.campaigns}${toQuery(params)}`);
export const listCampaignProjects = (params?: URLSearchParams | Record<string, string>) =>
  defaultClient.get<Paginated<CampaignProject>>(`${path.campaignProjects}${toQuery(params)}`);
export const listCalcRuns = (params?: URLSearchParams | Record<string, string>) =>
  defaultClient.get<Paginated<CalcRun>>(`${path.calcRuns}${toQuery(params)}`);

// Retrieve by id
export const getField = (id: ID) => defaultClient.get<Field>(`${path.fields}${id}/`);
export const getPlatform = (id: ID) => defaultClient.get<Platform>(`${path.platforms}${id}/`);
export const getRig = (id: ID) => defaultClient.get<Rig>(`${path.rigs}${id}/`);
export const getWell = (id: ID) => defaultClient.get<Well>(`${path.wells}${id}/`);
export const getMaintenanceWindow = (id: ID) => defaultClient.get<MaintenanceWindow>(`${path.maintenanceWindows}${id}/`);
export const getScenario = (id: ID) => defaultClient.get<Scenario>(`${path.scenarios}${id}/`);
export const getProject = (id: ID) => defaultClient.get<Project>(`${path.projects}${id}/`);
export const getCampaign = (id: ID) => defaultClient.get<Campaign>(`${path.campaigns}${id}/`);
export const getCampaignProject = (id: ID) => defaultClient.get<CampaignProject>(`${path.campaignProjects}${id}/`);
export const getCalcRun = (id: ID) => defaultClient.get<CalcRun>(`${path.calcRuns}${id}/`);

// Create
export const createField = (payload: Pick<Field, "name">) =>
  defaultClient.post<Field>(path.fields, payload);
export const createPlatform = (payload: Pick<Platform, "field" | "name" | "status">) =>
  defaultClient.post<Platform>(path.platforms, payload);
export const createRig = (payload: Pick<Rig, "name" | "rig_kind" | "day_rate" | "status">) =>
  defaultClient.post<Rig>(path.rigs, payload);
export const createWell = (
  payload: Pick<Well, "name" | "field" | "platform" | "well_kind" | "type" | "lat" | "lon">
) => defaultClient.post<Well>(path.wells, payload);
export const createMaintenanceWindow = (
  payload: Pick<MaintenanceWindow, "platform" | "start_date" | "end_date" | "reason">
) => defaultClient.post<MaintenanceWindow>(path.maintenanceWindows, payload);
export const createScenario = (
  payload: Pick<Scenario, "name" | "status" | "created_by">
) => defaultClient.post<Scenario>(path.scenarios, payload);
export const createProject = (
  payload: Pick<
    Project,
    | "name"
    | "project_type"
    | "field"
    | "platform"
    | "well"
    | "rig"
    | "status"
    | "planned_start"
    | "planned_end"
    | "actual_start"
    | "actual_end"
    | "dependencies"
    | "extras"
  >
) => defaultClient.post<Project>(path.projects, payload);
export const createCampaign = (
  payload: Pick<Campaign, "scenario" | "name" | "campaign_type" | "rig" | "field">
) => defaultClient.post<Campaign>(path.campaigns, payload);
export const createCampaignProject = (
  payload: Pick<CampaignProject, "campaign" | "project">
) => defaultClient.post<CampaignProject>(path.campaignProjects, payload);
export const createCalcRun = (
  payload: Pick<CalcRun, "scenario" | "status" | "params" | "results">
) => defaultClient.post<CalcRun>(path.calcRuns, payload);

// Update (PUT)
export const updateField = (id: ID, payload: Pick<Field, "name">) =>
  defaultClient.put<Field>(`${path.fields}${id}/`, payload);
export const updatePlatform = (id: ID, payload: Pick<Platform, "field" | "name" | "status">) =>
  defaultClient.put<Platform>(`${path.platforms}${id}/`, payload);
export const updateRig = (id: ID, payload: Pick<Rig, "name" | "rig_kind" | "day_rate" | "status">) =>
  defaultClient.put<Rig>(`${path.rigs}${id}/`, payload);
export const updateWell = (
  id: ID,
  payload: Pick<Well, "name" | "field" | "platform" | "well_kind" | "type" | "lat" | "lon">
) => defaultClient.put<Well>(`${path.wells}${id}/`, payload);
export const updateMaintenanceWindow = (
  id: ID,
  payload: Pick<MaintenanceWindow, "platform" | "start_date" | "end_date" | "reason">
) => defaultClient.put<MaintenanceWindow>(`${path.maintenanceWindows}${id}/`, payload);
export const updateScenario = (id: ID, payload: Pick<Scenario, "name" | "status" | "created_by">) =>
  defaultClient.put<Scenario>(`${path.scenarios}${id}/`, payload);
export const updateProject = (
  id: ID,
  payload: Pick<
    Project,
    | "name"
    | "project_type"
    | "field"
    | "platform"
    | "well"
    | "rig"
    | "status"
    | "planned_start"
    | "planned_end"
    | "actual_start"
    | "actual_end"
    | "dependencies"
    | "extras"
  >
) => defaultClient.put<Project>(`${path.projects}${id}/`, payload);
export const updateCampaign = (
  id: ID,
  payload: Pick<Campaign, "scenario" | "name" | "campaign_type" | "rig" | "field">
) => defaultClient.put<Campaign>(`${path.campaigns}${id}/`, payload);
export const updateCampaignProject = (
  id: ID,
  payload: Pick<CampaignProject, "campaign" | "project">
) => defaultClient.put<CampaignProject>(`${path.campaignProjects}${id}/`, payload);
export const updateCalcRun = (
  id: ID,
  payload: Pick<CalcRun, "scenario" | "status" | "params" | "results" | "completed_at">
) => defaultClient.put<CalcRun>(`${path.calcRuns}${id}/`, payload);

// Partial update (PATCH)
export const patchField = (id: ID, payload: Partial<Pick<Field, "name">>) =>
  defaultClient.patch<Field>(`${path.fields}${id}/`, payload);
export const patchPlatform = (id: ID, payload: Partial<Pick<Platform, "field" | "name" | "status">>) =>
  defaultClient.patch<Platform>(`${path.platforms}${id}/`, payload);
export const patchRig = (id: ID, payload: Partial<Pick<Rig, "name" | "rig_kind" | "day_rate" | "status">>) =>
  defaultClient.patch<Rig>(`${path.rigs}${id}/`, payload);
export const patchWell = (
  id: ID,
  payload: Partial<Pick<Well, "name" | "field" | "platform" | "well_kind" | "type" | "lat" | "lon">>
) => defaultClient.patch<Well>(`${path.wells}${id}/`, payload);
export const patchMaintenanceWindow = (
  id: ID,
  payload: Partial<Pick<MaintenanceWindow, "platform" | "start_date" | "end_date" | "reason">>
) => defaultClient.patch<MaintenanceWindow>(`${path.maintenanceWindows}${id}/`, payload);
export const patchScenario = (
  id: ID,
  payload: Partial<Pick<Scenario, "name" | "status" | "created_by">>
) => defaultClient.patch<Scenario>(`${path.scenarios}${id}/`, payload);
export const patchProject = (
  id: ID,
  payload: Partial<
    Pick<
      Project,
      | "name"
      | "project_type"
      | "field"
      | "platform"
      | "well"
      | "rig"
      | "status"
      | "planned_start"
      | "planned_end"
      | "actual_start"
      | "actual_end"
      | "dependencies"
      | "extras"
    >
  >
) => defaultClient.patch<Project>(`${path.projects}${id}/`, payload);
export const patchCampaign = (
  id: ID,
  payload: Partial<Pick<Campaign, "scenario" | "name" | "campaign_type" | "rig" | "field">>
) => defaultClient.patch<Campaign>(`${path.campaigns}${id}/`, payload);
export const patchCampaignProject = (
  id: ID,
  payload: Partial<Pick<CampaignProject, "campaign" | "project">>
) => defaultClient.patch<CampaignProject>(`${path.campaignProjects}${id}/`, payload);
export const patchCalcRun = (
  id: ID,
  payload: Partial<Pick<CalcRun, "scenario" | "status" | "params" | "results" | "completed_at">>
) => defaultClient.patch<CalcRun>(`${path.calcRuns}${id}/`, payload);

// Delete
export const deleteField = (id: ID) => defaultClient.delete<void>(`${path.fields}${id}/`);
export const deletePlatform = (id: ID) => defaultClient.delete<void>(`${path.platforms}${id}/`);
export const deleteRig = (id: ID) => defaultClient.delete<void>(`${path.rigs}${id}/`);
export const deleteWell = (id: ID) => defaultClient.delete<void>(`${path.wells}${id}/`);
export const deleteMaintenanceWindow = (id: ID) => defaultClient.delete<void>(`${path.maintenanceWindows}${id}/`);
export const deleteScenario = (id: ID) => defaultClient.delete<void>(`${path.scenarios}${id}/`);
export const deleteProject = (id: ID) => defaultClient.delete<void>(`${path.projects}${id}/`);
export const deleteCampaign = (id: ID) => defaultClient.delete<void>(`${path.campaigns}${id}/`);
export const deleteCampaignProject = (id: ID) => defaultClient.delete<void>(`${path.campaignProjects}${id}/`);
export const deleteCalcRun = (id: ID) => defaultClient.delete<void>(`${path.calcRuns}${id}/`);
