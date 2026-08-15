import catalogData from "./forensicCatalog.json";

export interface SubsystemDefinition {
  id: string;
  number: string;
  name: string;
  badge: string;
  metrics: string;
  desc: string;
  descTr: string;
}

export interface PillarDefinition {
  id: string;
  number: number;
  name: string;
  shortName: string;
  badge: string;
  color: string;
  icon: string;
  subsystems: SubsystemDefinition[];
}

export interface ForensicCatalog {
  version: string;
  pillars: PillarDefinition[];
}

export const FORENSIC_CATALOG: ForensicCatalog = catalogData as ForensicCatalog;

export function getAllSubsystems(): SubsystemDefinition[] {
  return FORENSIC_CATALOG.pillars.flatMap((p) => p.subsystems);
}

export function getSubsystemById(id: string): SubsystemDefinition | undefined {
  return getAllSubsystems().find((s) => s.id === id);
}

export function getPillarById(id: string): PillarDefinition | undefined {
  return FORENSIC_CATALOG.pillars.find((p) => p.id === id);
}
