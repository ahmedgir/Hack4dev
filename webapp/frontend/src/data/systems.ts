import catalog from "./catalog.json";

export type ScientificStatus =
  | "promising_preliminary_transit"
  | "insufficient_for_transit_claim"
  | "transit_like_but_parameters_inconsistent"
  | "not_analysed";

export type SessionRecord = {
  id: string;
  date: string;
  totalFrames: number;
  acceptedFrames: number;
  referenceFrameIndex?: number;
  measuredDepthPercent?: number;
  measuredDurationHours?: number;
  midpointOffsetMinutes?: number;
  residualScatterPercent?: number;
  preTransitPoints?: number;
  inTransitPoints?: number;
  postTransitPoints?: number;
  coverageComplete?: boolean;
  fitValid?: boolean;
  status: ScientificStatus;
  summaryPath: string;
  lightCurvePath: string;
  fieldImagePath?: string;
  timelineFramesPath?: string;
};

export type SystemRecord = {
  slug: string;
  starName: string;
  planetName: string;
  alias?: string;
  discoverySurvey: string;
  periodDays: number;
  publishedDepthPercent: number;
  durationHours: number;
  raDeg: number;
  decDeg: number;
  gaiaMagnitude: number;
  shortDescription: string;
  catalogImagePath: string;
  imageKind: "artist_concept" | "verified_field" | "representative_concept";
  imageLabel: string;
  sourceUrl: string;
  processingProgress?: {
    date: string;
    auditedFrames: number;
    totalFrames: number;
    fileAuditComplete: boolean;
    coordinateSolution: "verified" | "unavailable";
    photometryComplete: boolean;
    reason: string;
  };
  sessions: SessionRecord[];
};

export const systems = catalog as SystemRecord[];
export const featuredSystem = systems[0];
export const getSystem = (slug: string) => systems.find((system) => system.slug === slug);

export function getSystemStatus(system: SystemRecord): ScientificStatus {
  if (!system.sessions.length) return "not_analysed";
  if (system.sessions.some((session) => session.status === "promising_preliminary_transit")) {
    return "promising_preliminary_transit";
  }
  if (system.sessions.some((session) => session.status === "transit_like_but_parameters_inconsistent")) {
    return "transit_like_but_parameters_inconsistent";
  }
  return "insufficient_for_transit_claim";
}

export const statusLabels: Record<ScientificStatus, string> = {
  promising_preliminary_transit: "Promising preliminary recovery",
  insufficient_for_transit_claim: "Insufficient for a transit claim",
  transit_like_but_parameters_inconsistent: "Transit-like, but inconsistent",
  not_analysed: "Reviewed — no verified solution",
};
