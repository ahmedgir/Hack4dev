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
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Hack4Dev exoplanet PoC outputs.")
    parser.add_argument("--target", choices=["WASP-10", "WASP-2", "CoRoT-2"])
    parser.add_argument("--date")
    parser.add_argument("--cached-only", action="store_true", help="Do not submit a new Astrometry.net job.")
    args = parser.parse_args()
    runs = [(args.target, args.date)] if args.target and args.date else DEFAULT_RUNS
    failures = []
    for target, date in runs:
        print(f"\n=== {target} {date} ===", flush=True)
        try:
            summary = run_target(ROOT, target, date, allow_plate_solve=not args.cached_only)
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
