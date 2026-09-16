from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    audit_path = ROOT / "outputs" / "audit" / "fits_file_audit.csv"
    if not audit_path.exists():
        raise FileNotFoundError("Run scripts/audit_dataset.py first")
    audit = pd.read_csv(audit_path)
    science_audit = audit[audit.kind == "science"]
    rows = []
    observations = ROOT / "database" / "observations"
    for date_dir in sorted(path for path in observations.iterdir() if path.is_dir()):
        for target_dir in sorted(path for path in date_dir.iterdir() if path.is_dir()):
            science_paths = sorted(target_dir.rglob("*.fits"))
            expected = len(science_paths)
            audited = science_audit[
                (science_audit.target == target_dir.name) & (science_audit.date == date_dir.name)
            ]
            output = ROOT / "outputs" / target_dir.name.lower().replace("-", "_") / date_dir.name
            astap_attempt_path = output / "astap_attempt.json"
            astap_attempted = astap_attempt_path.exists()
            astap_success = False
            if astap_attempted:
                astap_success = bool(json.loads(astap_attempt_path.read_text(encoding="utf-8")).get("success"))
            summary_path = output / "summary.json"
            photometry_path = output / "photometry.csv"
            timeline_path = output / "web_timeline.json"
            photometry_rows = len(pd.read_csv(photometry_path)) if photometry_path.exists() else 0
            timeline_rows = len(json.loads(timeline_path.read_text(encoding="utf-8"))) if timeline_path.exists() else 0
            wcs_files = list(output.glob("wcs_*.fits"))
            summary = json.loads(summary_path.read_text(encoding="utf-8")) if summary_path.exists() else {}
            rows.append({
                "date": date_dir.name,
                "target": target_dir.name,
                "science_frames": expected,
                "audited_frames": len(audited),
                "audit_all_read_ok": len(audited) == expected and bool(audited.read_ok.all()),
                "astap_attempted": astap_attempted,
                "astap_success": astap_success,
                "wcs_available": bool(wcs_files) or summary.get("plate_solution") == "ASTAP local",
                "pipeline_complete": summary_path.exists() and photometry_rows == expected,
                "photometry_frames": photometry_rows,
                "timeline_frames": timeline_rows,
                "all_frames_accounted_for": photometry_rows == expected and timeline_rows == expected,
                "accepted_frames": summary.get("accepted_frames"),
                "scientific_status": summary.get("scientific_status", "not_analysed"),
                "plate_solution": summary.get("plate_solution", "none"),
            })
    table = pd.DataFrame(rows)
    output_dir = ROOT / "outputs" / "audit"
    table.to_csv(output_dir / "session_completeness.csv", index=False)
    report = {
        "sessions_total": len(table),
        "sessions_all_files_audited": int(table.audit_all_read_ok.sum()),
        "sessions_astap_attempted": int(table.astap_attempted.sum()),
        "sessions_astap_solved": int(table.astap_success.sum()),
        "sessions_with_wcs": int(table.wcs_available.sum()),
        "sessions_pipeline_complete": int(table.pipeline_complete.sum()),
        "sessions_all_frames_accounted_for": int(table.all_frames_accounted_for.sum()),
        "science_frames_total": int(table.science_frames.sum()),
        "science_frames_audited": int(table.audited_frames.sum()),
        "science_frames_in_photometry": int(table.photometry_frames.sum()),
        "rows": table.to_dict(orient="records"),
    }
    (output_dir / "session_completeness.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key != "rows"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
