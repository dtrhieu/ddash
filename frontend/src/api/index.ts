export * from "./types";
export * from "./errors";
export { ApiClient, api } from "./client";

// Convenience endpoint functions using the default client
import { api as defaultClient } from "./client";
import type { Health, SchemaLite, Paginated, Field, Platform, Rig, Well, Project, Campaign } from "./types";

export const getHealth = () => defaultClient.get<Health>("/health");
export const getSchemaLite = () => defaultClient.get<SchemaLite>("/schema-lite");

export const listFields = (params?: URLSearchParams | Record<string, string>) =>
  defaultClient.get<Paginated<Field>>(`/fields/${toQuery(params)}`);
export const listPlatforms = (params?: URLSearchParams | Record<string, string>) =>
  defaultClient.get<Paginated<Platform>>(`/platforms/${toQuery(params)}`);
export const listRigs = (params?: URLSearchParams | Record<string, string>) =>
  defaultClient.get<Paginated<Rig>>(`/rigs/${toQuery(params)}`);
export const listWells = (params?: URLSearchParams | Record<string, string>) =>
  defaultClient.get<Paginated<Well>>(`/wells/${toQuery(params)}`);
export const listProjects = (params?: URLSearchParams | Record<string, string>) =>
  defaultClient.get<Paginated<Project>>(`/projects/${toQuery(params)}`);
export const listCampaigns = (params?: URLSearchParams | Record<string, string>) =>
  defaultClient.get<Paginated<Campaign>>(`/campaigns/${toQuery(params)}`);

function toQuery(params?: URLSearchParams | Record<string, string>) {
  if (!params) return "";
  if (params instanceof URLSearchParams) {
    const s = params.toString();
    return s ? `?${s}` : "";
  }
  const s = new URLSearchParams(params).toString();
  return s ? `?${s}` : "";
}
