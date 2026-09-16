from __future__ import annotations

import argparse
import csv
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path, PureWindowsPath

import requests
from astropy.io import fits


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "database" / "metadata" / "observations.csv"


def valid_existing(path: Path, expected_size: int) -> bool:
    if not path.exists() or path.stat().st_size != expected_size:
        return False
    try:
        with fits.open(path, memmap=False) as hdul:
            return hdul[0].data is not None
    except Exception:
        return False


def display_path(path: Path) -> str:
    return str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)


def restore(row: dict[str, str], verify_only: bool, dataset_root: Path) -> tuple[str, str]:
    destination = dataset_root / Path(*PureWindowsPath(row["filepath"]).parts)
    expected_size = int(row["file_size"])
    if valid_existing(destination, expected_size):
        return "ok", display_path(destination)
    if verify_only:
        return "missing", display_path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".part")
    try:
        with requests.get(row["fits_url"], stream=True, timeout=(20, 180)) as response:
            response.raise_for_status()
            with temporary.open("wb") as handle:
                for chunk in response.iter_content(1024 * 1024):
                    if chunk:
                        handle.write(chunk)
        if temporary.stat().st_size != expected_size:
            raise RuntimeError(
                f"Size mismatch: expected {expected_size}, received {temporary.stat().st_size}"
            )
        with fits.open(temporary, memmap=False) as hdul:
            if hdul[0].data is None:
                raise RuntimeError("Downloaded FITS contains no primary image")
        os.replace(temporary, destination)
        return "downloaded", display_path(destination)
    except Exception as exc:
        if temporary.exists():
            temporary.unlink()
        return "failed", f"{display_path(destination)}: {exc!r}"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Restore all Hack4Dev FITS files from the committed MicroObservatory manifest."
    )
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--verify-only", action="store_true")
    parser.add_argument("--limit", type=int, help="Process only the first N entries for testing.")
    parser.add_argument(
        "--destination-root",
        type=Path,
        default=ROOT / "database",
        help="Dataset root; defaults to the repository database directory.",
    )
    args = parser.parse_args()
    with MANIFEST.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if args.limit:
        rows = rows[: args.limit]
    counts = {"ok": 0, "downloaded": 0, "missing": 0, "failed": 0}
    failures: list[str] = []
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        destination_root = args.destination_root.resolve()
        futures = [executor.submit(restore, row, args.verify_only, destination_root) for row in rows]
        for index, future in enumerate(as_completed(futures), start=1):
            status, detail = future.result()
            counts[status] += 1
            if status == "failed":
                failures.append(detail)
            if index % 100 == 0 or index == len(rows):
                print(f"Processed {index}/{len(rows)}: {counts}", flush=True)
    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
    print(f"Final: {counts}")
    return 1 if counts["failed"] or (args.verify_only and counts["missing"]) else 0


if __name__ == "__main__":
    sys.exit(main())
