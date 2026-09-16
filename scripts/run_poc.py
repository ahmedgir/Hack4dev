from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
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


def _run_session(target: str, date: str, cached_only: bool, no_astap: bool) -> dict:
    return run_target(
        ROOT,
        target,
        date,
        allow_plate_solve=not cached_only,
        prefer_astap=not no_astap,
    )


def _record_result(
    target: str,
    date: str,
    summary: dict | None,
    error: Exception | None,
    failures: list[tuple[str, str, str]],
) -> None:
    print(f"\n=== {target} {date} ===", flush=True)
    if error is not None:
        failures.append((target, date, repr(error)))
        print(f"FAILED: {error!r}", flush=True)
        return
    print(json.dumps(summary, indent=2), flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Hack4Dev exoplanet PoC outputs.")
    targets = sorted(json.loads((ROOT / "config" / "targets.json").read_text(encoding="utf-8")))
    parser.add_argument("--target", choices=targets)
    parser.add_argument("--date")
    parser.add_argument("--cached-only", action="store_true", help="Do not submit a new Astrometry.net job.")
    parser.add_argument("--all-sessions", action="store_true", help="Process every discovered science session.")
    parser.add_argument("--no-astap", action="store_true", help="Skip the local ASTAP attempt for uncached fields.")
    parser.add_argument(
        "--jobs",
        type=int,
        default=1,
        metavar="N",
        help="Process up to N sessions concurrently in separate processes (default: 1).",
    )
    args = parser.parse_args()
    if bool(args.target) != bool(args.date):
        parser.error("--target and --date must be supplied together")
    if args.jobs < 1:
        parser.error("--jobs must be at least 1")
    runs = discover_runs() if args.all_sessions else ([(args.target, args.date)] if args.target else DEFAULT_RUNS)
    failures = []
    if args.jobs == 1 or len(runs) <= 1:
        for target, date in runs:
            try:
                summary = _run_session(target, date, args.cached_only, args.no_astap)
                _record_result(target, date, summary, None, failures)
            except Exception as exc:
                _record_result(target, date, None, exc, failures)
    else:
        worker_count = min(args.jobs, len(runs))
        print(f"Processing {len(runs)} sessions with {worker_count} concurrent workers.", flush=True)
        with ProcessPoolExecutor(max_workers=worker_count) as executor:
            futures = {
                executor.submit(_run_session, target, date, args.cached_only, args.no_astap): (target, date)
                for target, date in runs
            }
            for future in as_completed(futures):
                target, date = futures[future]
                try:
                    _record_result(target, date, future.result(), None, failures)
                except Exception as exc:
                    _record_result(target, date, None, exc, failures)
    if failures:
        print("\nFailures:", failures, flush=True)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
