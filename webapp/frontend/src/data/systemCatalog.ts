export type CatalogStatus = "promising" | "insufficient" | "inconsistent" | "not_analysed";

export type CatalogSystem = {
  slug: string;
  starName: string;
  planetName: string;
  alias?: string;
  survey: string;
  periodDays: number;
  depthPercent: number;
  durationHours: number;
  raDeg: number;
  decDeg: number;
  status: CatalogStatus;
  statusLabel: string;
  summary: string;
  imagePath: string;
  imageKind: "artist_concept" | "verified_field" | "representative_concept";
  imageLabel: string;
  sourceUrl: string;
  analysedSessions: number;
};

const nasa = (slug: string) => `https://science.nasa.gov/exoplanet-catalog/${slug}/`;

export const systemCatalog: CatalogSystem[] = [
  {
    slug: "corot-2", starName: "CoRoT-2", planetName: "CoRoT-2 b", survey: "CoRoT",
    periodDays: 1.7429935, depthPercent: 2.75, durationHours: 2.26704,
    raDeg: 291.7770457, decDeg: 1.3836634, status: "promising",
    statusLabel: "Promising preliminary recovery", analysedSessions: 2,
    summary: "Two nights processed through the project pipeline and cross-checked with EXOTIC.",
    imagePath: "/media/catalog/corot-2/artist-concept.jpg", imageKind: "artist_concept",
    imageLabel: "NASA artist’s concept of the CoRoT-2 system", sourceUrl: nasa("corot-2-b"),
  },
  {
    slug: "wasp-10", starName: "WASP-10", planetName: "WASP-10 b", survey: "WASP",
    periodDays: 3.0927616, depthPercent: 2.525, durationHours: 2.2271,
    raDeg: 348.9930457, decDeg: 31.4627508, status: "insufficient",
    statusLabel: "Insufficient coverage", analysedSessions: 1,
    summary: "The sequence lacks post-transit baseline and does not yet support a recovery claim.",
    imagePath: "/media/catalog/wasp-10/verified-field.png", imageKind: "verified_field",
    imageLabel: "Processed MicroObservatory field; marker identifies the host star", sourceUrl: nasa("wasp-10-b"),
  },
  {
    slug: "wasp-2", starName: "WASP-2", planetName: "WASP-2 b", survey: "WASP",
    periodDays: 2.152175, depthPercent: 1.646, durationHours: 1.78824,
    raDeg: 307.7255587, decDeg: 6.4293305, status: "insufficient",
    statusLabel: "Insufficient evidence", analysedSessions: 2,
    summary: "Two sessions were reviewed, but incomplete baseline and noise prevent a reliable result.",
    imagePath: "/media/catalog/wasp-2/verified-field.png", imageKind: "verified_field",
    imageLabel: "Processed MicroObservatory field; marker identifies the host star", sourceUrl: nasa("wasp-2-b"),
  },
  {
    slug: "qatar-1", starName: "Qatar-1", planetName: "Qatar-1 b", survey: "Qatar",
    periodDays: 1.4200242, depthPercent: 2.14, durationHours: 1.66104,
    raDeg: 303.3818697, decDeg: 65.1623313, status: "inconsistent",
    statusLabel: "Transit-like, but inconsistent", analysedSessions: 1,
    summary: "A dip is present, but its measured properties are not consistent enough for a recovery claim.",
    imagePath: "/media/catalog/qatar-1/verified-field.png", imageKind: "verified_field",
    imageLabel: "Processed MicroObservatory field; marker identifies the host star", sourceUrl: nasa("qatar-1-b"),
  },
  {
    slug: "tres-3", starName: "TrES-3", planetName: "TrES-3 b", survey: "TrES",
    periodDays: 1.30618581, depthPercent: 2.739, durationHours: 1.4177746,
    raDeg: 268.0291106, decDeg: 37.5463268, status: "insufficient",
    statusLabel: "Insufficient coverage", analysedSessions: 1,
    summary: "The available sequence is too incomplete to establish the expected transit shape.",
    imagePath: "/media/catalog/tres-3/verified-field.png", imageKind: "verified_field",
    imageLabel: "Processed MicroObservatory field; marker identifies the host star", sourceUrl: nasa("tres-3-b"),
  },
  {
    slug: "tres-1", starName: "TrES-1", planetName: "TrES-1 b", survey: "TrES",
    periodDays: 3.03007, depthPercent: 1.8, durationHours: 2.508,
    raDeg: 286.0408755, decDeg: 36.632536, status: "not_analysed",
    statusLabel: "Awaiting analysis", analysedSessions: 0,
    summary: "Target parameters are ready; no reviewed pipeline result is published yet.",
    imagePath: "/media/catalog/concepts/hot-jupiter.jpg", imageKind: "representative_concept",
    imageLabel: "Representative NASA hot-Jupiter concept — not an image of TrES-1 b", sourceUrl: nasa("tres-1-b"),
  },
  {
    slug: "tres-5", starName: "TrES-5", planetName: "TrES-5 b", survey: "TrES",
    periodDays: 1.48224686, depthPercent: 2.192, durationHours: 1.595,
    raDeg: 305.2219454, decDeg: 59.4489033, status: "not_analysed",
    statusLabel: "Awaiting analysis", analysedSessions: 0,
    summary: "Target parameters are ready; no reviewed pipeline result is published yet.",
    imagePath: "/media/catalog/concepts/hot-jupiter.jpg", imageKind: "representative_concept",
    imageLabel: "Representative NASA hot-Jupiter concept — not an image of TrES-5 b", sourceUrl: nasa("tres-5-b"),
  },
  {
    slug: "hat-p-10", starName: "HAT-P-10", planetName: "HAT-P-10 b", alias: "WASP-11 b", survey: "HATNet / WASP",
    periodDays: 3.72247, depthPercent: 1.6, durationHours: 2.556,
    raDeg: 47.3689472, decDeg: 30.6733817, status: "not_analysed",
    statusLabel: "Awaiting analysis", analysedSessions: 0,
    summary: "Target parameters are ready; no reviewed pipeline result is published yet.",
    imagePath: "/media/catalog/concepts/hot-jupiter.jpg", imageKind: "representative_concept",
    imageLabel: "Representative NASA hot-Jupiter concept — not an image of HAT-P-10 b", sourceUrl: nasa("wasp-11-b"),
  },
];
