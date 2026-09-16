import { access, copyFile, mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";

const args = Object.fromEntries(
  process.argv.slice(2).map((item) => {
    const [key, ...value] = item.replace(/^--/, "").split("=");
    return [key, value.join("=")];
  }),
);

if (!args.slug || !args.output) {
  console.error("Usage: pnpm import:session --slug=<system-slug> --output=<pipeline-output-folder>");
  process.exit(1);
}

const root = process.cwd();
const output = path.resolve(root, args.output);
const catalogPath = path.join(root, "src/data/catalog.json");
const summaryPath = path.join(output, "summary.json");
const curvePath = path.join(output, "web_light_curve.json");
const fieldPath = path.join(output, "01_verified_field.png");

for (const required of [summaryPath, curvePath, fieldPath]) await access(required);

const summary = JSON.parse(await readFile(summaryPath, "utf8"));
const catalog = JSON.parse(await readFile(catalogPath, "utf8"));
const system = catalog.find((item) => item.slug === args.slug);
if (!system) throw new Error(`Unknown system slug: ${args.slug}. Add its published profile to catalog.json first.`);
if (!summary.date) throw new Error("summary.json does not contain a date.");

const publicData = path.join(root, "public/data/systems", args.slug, summary.date);
const publicMedia = path.join(root, "public/media/systems", args.slug, summary.date);
await mkdir(publicData, { recursive: true });
await mkdir(publicMedia, { recursive: true });
await Promise.all([
  copyFile(summaryPath, path.join(publicData, "summary.json")),
  copyFile(curvePath, path.join(publicData, "light-curve.json")),
  copyFile(fieldPath, path.join(publicMedia, "verified-field.png")),
]);

const session = {
  id: `${args.slug}-${summary.date}`,
  date: summary.date,
  totalFrames: summary.total_frames,
  acceptedFrames: summary.accepted_frames,
  referenceFrameIndex: summary.reference_frame_index,
  measuredDepthPercent: summary.fitted_depth_percent,
  measuredDurationHours: summary.fitted_duration_hours,
  midpointOffsetMinutes: summary.fitted_mid_offset_minutes,
  residualScatterPercent: summary.residual_scatter_percent,
  preTransitPoints: summary.pre_transit_points,
  inTransitPoints: summary.in_transit_points,
  postTransitPoints: summary.post_transit_points,
  coverageComplete: summary.coverage_complete,
  fitValid: summary.fit_valid,
  status: summary.scientific_status,
  summaryPath: `/data/systems/${args.slug}/${summary.date}/summary.json`,
  lightCurvePath: `/data/systems/${args.slug}/${summary.date}/light-curve.json`,
  fieldImagePath: `/media/systems/${args.slug}/${summary.date}/verified-field.png`,
};

const existing = system.sessions.findIndex((item) => item.id === session.id);
if (existing >= 0) system.sessions[existing] = session;
else system.sessions.push(session);
system.sessions.sort((a, b) => a.date.localeCompare(b.date));

await writeFile(catalogPath, `${JSON.stringify(catalog, null, 2)}\n`);
console.log(`Imported ${system.planetName} session ${summary.date}. Run pnpm build before publishing.`);
