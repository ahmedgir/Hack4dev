from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from astropy.io import fits


ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def classify(path: Path) -> tuple[str, str, str]:
    relative = path.relative_to(ROOT / "database")
    parts = relative.parts
    if parts[0] == "observations":
        return "science", parts[2], parts[1]
    return "dark", "Dark", parts[1]


def main() -> int:
    parser = argparse.ArgumentParser(description="Read and audit every FITS file in the Hack4Dev dataset.")
    parser.add_argument("--no-hash", action="store_true", help="Skip SHA-256 for a faster diagnostic run.")
    args = parser.parse_args()
    paths = sorted((ROOT / "database" / "observations").rglob("*.fits"))
    paths += sorted((ROOT / "database" / "calibration").rglob("*.fits"))
    rows = []
    for index, path in enumerate(paths, start=1):
        kind, target, date = classify(path)
        row = {
            "relative_path": str(path.relative_to(ROOT)),
            "kind": kind,
            "target": target,
            "date": date,
            "read_ok": False,
            "error": "",
            "sha256": "" if args.no_hash else sha256(path),
            "size_bytes": path.stat().st_size,
        }
        try:
            with fits.open(path, memmap=False, checksum=True) as hdul:
                data = np.asarray(hdul[0].data)
                header = hdul[0].header
            finite = np.isfinite(data)
            row.update({
                "read_ok": True,
                "shape": "x".join(map(str, data.shape)),
                "finite_fraction": float(finite.mean()),
                "minimum": float(np.nanmin(data)),
                "median": float(np.nanmedian(data)),
                "maximum": float(np.nanmax(data)),
                "saturated_fraction_4095": float(np.mean(data >= 4095)),
                "object": str(header.get("OBJECT", "")),
                "date_obs": str(header.get("DATE-OBS", "")),
                "mjd_obs": header.get("MJD-OBS"),
                "exptime": header.get("EXPTIME"),
                "has_required_science_headers": kind == "dark" or all(
                    key in header for key in ("OBJECT", "MJD-OBS", "EXPTIME", "RA", "DEC")
                ),
            })
        except Exception as exc:
            row["error"] = repr(exc)
        rows.append(row)
        if index % 100 == 0 or index == len(paths):
            print(f"Audited {index}/{len(paths)}", flush=True)
    table = pd.DataFrame(rows)
    output_dir = ROOT / "outputs" / "audit"
    output_dir.mkdir(parents=True, exist_ok=True)
    table.to_csv(output_dir / "fits_file_audit.csv", index=False)
    summary = {
        "files_discovered": len(table),
        "files_read_ok": int(table.read_ok.sum()),
        "files_failed": int((~table.read_ok).sum()),
        "science_files": int((table.kind == "science").sum()),
        "dark_files": int((table.kind == "dark").sum()),
        "science_headers_complete": int(table.loc[table.kind == "science", "has_required_science_headers"].sum()),
        "more_than_half_saturated": int((table.saturated_fraction_4095 > 0.5).sum()),
        "sha256_recorded": not args.no_hash,
    }
    (output_dir / "fits_audit_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 1 if summary["files_failed"] else 0


if __name__ == "__main__":
    sys.exit(main())
