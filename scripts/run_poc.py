from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pipeline import run_target


DEFAULT_RUNS = [
    ("WASP-10", "2026-08-08"),
    ("WASP-2", "2026-08-11"),
    ("WASP-2", "2026-08-24"),
    ("CoRoT-2", "2026-08-09"),
    ("CoRoT-2", "2026-08-16"),
    ("TRES-3", "2026-08-10"),
    ("Qatar-1", "2026-08-21"),
]


def discover_runs() -> list[tuple[str, str]]:
    runs = []
    observations = ROOT / "database" / "observations"
    for date_dir in sorted(path for path in observations.iterdir() if path.is_dir()):
        for target_dir in sorted(path for path in date_dir.iterdir() if path.is_dir()):
            runs.append((target_dir.name, date_dir.name))
    return runs


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Hack4Dev exoplanet PoC outputs.")
    targets = sorted(json.loads((ROOT / "config" / "targets.json").read_text(encoding="utf-8")))
    parser.add_argument("--target", choices=targets)
    parser.add_argument("--date")
    parser.add_argument("--cached-only", action="store_true", help="Do not submit a new Astrometry.net job.")
    parser.add_argument("--all-sessions", action="store_true", help="Process every discovered science session.")
    parser.add_argument("--no-astap", action="store_true", help="Skip the local ASTAP attempt for uncached fields.")
    args = parser.parse_args()
    if bool(args.target) != bool(args.date):
        parser.error("--target and --date must be supplied together")
    runs = discover_runs() if args.all_sessions else ([(args.target, args.date)] if args.target else DEFAULT_RUNS)
    failures = []
    for target, date in runs:
        print(f"\n=== {target} {date} ===", flush=True)
        try:
            summary = run_target(
                ROOT,
                target,
                date,
                allow_plate_solve=not args.cached_only,
                prefer_astap=not args.no_astap,
            )
            print(json.dumps(summary, indent=2), flush=True)
        except Exception as exc:
            failures.append((target, date, repr(exc)))
            print(f"FAILED: {exc!r}", flush=True)
    if failures:
        print("\nFailures:", failures, flush=True)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
