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
  residualScatterPercent?: number;
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
  discoverySurvey: string;
  periodDays: number;
  publishedDepthPercent: number;
  durationHours: number;
  raDeg: number;
  decDeg: number;
  shortDescription: string;
  sessions: SessionRecord[];
};

export const systems = catalog as SystemRecord[];
export const featuredSystem = systems[0];
