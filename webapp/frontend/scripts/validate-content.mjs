import { access, readFile } from "node:fs/promises";
import path from "node:path";

const root = process.cwd();
const catalogPath = path.join(root, "src/data/catalog.json");
const systems = JSON.parse(await readFile(catalogPath, "utf8"));
const allowedStatuses = new Set([
  "promising_preliminary_transit",
  "insufficient_for_transit_claim",
  "transit_like_but_parameters_inconsistent",
  "not_analysed",
]);

const errors = [];
for (const system of systems) {
  if (!system.slug || !system.starName || !system.planetName) {
    errors.push("Every system needs slug, starName, and planetName.");
  }
  if (!system.catalogImagePath || !system.sourceUrl || !system.shortDescription) {
    errors.push(`${system.slug}: missing catalog image, source URL, or description.`);
  } else {
    try {
      await access(path.join(root, "public", system.catalogImagePath.replace(/^\//, "")));
    } catch {
      errors.push(`${system.slug}: missing catalog image at ${system.catalogImagePath}`);
    }
  }
  for (const session of system.sessions ?? []) {
    if (!allowedStatuses.has(session.status)) {
      errors.push(`${session.id}: unknown scientific status ${session.status}`);
    }
    if (session.acceptedFrames > session.totalFrames) {
      errors.push(`${session.id}: acceptedFrames exceeds totalFrames.`);
    }
    for (const key of ["summaryPath", "lightCurvePath", "fieldImagePath"]) {
      const value = session[key];
      if (!value) continue;
      try {
        await access(path.join(root, "public", value.replace(/^\//, "")));
      } catch {
        errors.push(`${session.id}: missing ${key} at ${value}`);
      }
    }
    try {
      const summary = JSON.parse(
        await readFile(path.join(root, "public", session.summaryPath.replace(/^\//, "")), "utf8"),
      );
      if (summary.scientific_status !== session.status) {
        errors.push(`${session.id}: catalog status does not match summary.json.`);
      }
      if (summary.total_frames !== session.totalFrames || summary.accepted_frames !== session.acceptedFrames) {
        errors.push(`${session.id}: frame counts do not match summary.json.`);
      }
    } catch {
      // The missing-path error above is more actionable.
    }
  }
}

if (errors.length) {
  console.error(errors.map((error) => `- ${error}`).join("\n"));
  process.exit(1);
}

console.log(`Validated ${systems.length} system(s).`);
