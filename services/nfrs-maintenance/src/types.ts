// Type definitions for NFR data structures

export interface Control {
  control_id: string;
  measure: string;
  threshold?: string;
  tooling?: string;
  cadence?: string;
  environments?: string[];
  services?: string[];
  operation_id?: string;
  operation_ids?: string[];
  status?: string;
  rationale?: string;
  stories?: string[];
}

export interface Operation {
  service: string;
  operation_id: string;
  p50_target_ms?: number | string;
  p95_target_ms?: number | string;
  absolute_max_ms?: number | string;
  burst_tps_target?: number | string;
  sustained_tps_target?: number | string;
  max_request_payload_bytes?: number | string;
  status?: string;
  rationale?: string;
  stories?: string[];
}

export interface NFR {
  code: string;
  title?: string;
  requirement: string;
  explanation?: string;
  stories?: string[];
  services?: string[];
  teams?: string[];
  releases?: ReleaseInfo[];
  controls?: Control[];
  operations?: Operation[];
}

export interface NFRFile {
  version: string | number;
  generated?: string;
  nfrs: NFR[];
}

export interface Domain {
  name: string;
  path: string;
  prefix: string;
}

export interface ServiceDefinition {
  id: string;
  displayName: string;
}

export interface ServiceOperations {
  [serviceId: string]: {
    [operationId: string]: string;
  };
}

export interface ServicesConfig {
  services: { [key: string]: string };
  operations: ServiceOperations;
}

export interface ExplanationsFile {
  version: string | number;
  generated?: string;
  explanations: { [code: string]: string };
}

export interface ReleaseInfo {
  id: string;
  operations?: string[];
  overall_status?: string;
  team_status?: { [teamId: string]: string };
}

export interface TeamMeta {
  id: string;
  name: string;
  description?: string;
  services?: string[];
}

export interface ReleaseMeta {
  id: string;
  name: string;
  description?: string;
}

export interface NfrMetaFile {
  version: string | number;
  generated?: string;
  teams: TeamMeta[];
  releases: ReleaseMeta[];
}
