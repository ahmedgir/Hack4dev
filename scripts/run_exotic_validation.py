#!/usr/bin/env python3
"""Run the committed EXOTIC validations without its unavailable LDTk FTP service.

EXOTIC normally downloads PHOENIX limb-darkening grids through LDTk at run time.
This runner obtains the same four-parameter (Claret) model family from
PyLightCurve's local ExoTETHyS/PHOENIX cache, then delegates the reduction and
fit to EXOTIC 4.3.1.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

import numpy as np
from pylightcurve import exotethys

import exotic.exotic as exotic_cli


REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIGS = {
    "2026-08-09": REPO_ROOT / "config/exotic/corot_2_2026-08-09.json",
    "2026-08-16": REPO_ROOT / "config/exotic/corot_2_2026-08-16.json",
}
# Both raw sequences begin with one cloud-obscured frame in which the target is
# not measurable. The committed pixel coordinates are therefore defined on the
# second frame, which is the first usable alignment reference for EXOTIC.
LEADING_REFERENCE_FRAMES_TO_SKIP = {
    "2026-08-09": 1,
    "2026-08-16": 1,
}


def _uncertainty(value: object, fallback: float) -> float:
    """Return a finite, positive one-sigma uncertainty."""
    try:
        parsed = abs(float(value))
    except (TypeError, ValueError):
        return fallback
    return parsed if np.isfinite(parsed) and parsed > 0 else fallback


def offline_limb_darkening(planet: dict, info: dict):
    """Provide EXOTIC's expected limb-darkening tuple from local PHOENIX grids."""
    temperature = float(planet["teff"])
    gravity = float(planet["logg"])
    metallicity = float(planet.get("met") or 0.0)
    temperature_error = max(
        _uncertainty(planet.get("teffUncPos"), 100.0),
        _uncertainty(planet.get("teffUncNeg"), 100.0),
    )
    gravity_error = max(
        _uncertainty(planet.get("loggUncPos"), 0.1),
        _uncertainty(planet.get("loggUncNeg"), 0.1),
    )

    def coefficients(teff: float, logg: float) -> np.ndarray:
        # The PHOENIX grid is solar-metallicity only. CoRoT-2's [Fe/H] is
        # +0.03 +/- 0.06, so that documented grid constraint is appropriate.
        return np.asarray(
            exotethys(
                logg,
                teff,
                metallicity,
                "clear",
                method="claret",
                stellar_model="phoenix",
            ),
            dtype=float,
        )

    central = coefficients(temperature, gravity)
    boundary_models = np.asarray(
        [
            coefficients(temperature + dt, gravity + dg)
            for dt in (-temperature_error, temperature_error)
            for dg in (-gravity_error, gravity_error)
        ]
    )
    errors = np.max(np.abs(boundary_models - central), axis=0)
    values = tuple((float(value), float(error)) for value, error in zip(central, errors))

    info.update(
        {
            "filter": "CV",
            "filter_desc": "MicroObservatory clear filter (local PHOENIX model)",
            "wl_min": 350.0,
            "wl_max": 850.0,
        }
    )
    formatted = ", ".join(f"u{i + 1}={v:.6f}+/-{e:.6f}" for i, (v, e) in enumerate(values))
    print(f"Offline PHOENIX limb darkening: {formatted}", flush=True)
    return central.tolist(), *values


def prepare_input_sequence(date: str, config_path: Path) -> Path:
    """Stage the usable EXOTIC reference sequence and write its effective config."""
    config = json.loads(config_path.read_text(encoding="utf-8"))
    source = Path(config["user_info"]["Directory with FITS files"])
    images = sorted(source.glob("*.fits"))
    skip = LEADING_REFERENCE_FRAMES_TO_SKIP[date]
    if len(images) <= skip:
        raise FileNotFoundError(f"not enough FITS images in {source}")

    output = Path(config["user_info"]["Directory to Save Plots"])
    staging = output / "input_fits"
    staging.mkdir(parents=True, exist_ok=True)
    for existing in staging.iterdir():
        if existing.is_symlink() or existing.is_file():
            existing.unlink()
    for image in images[skip:]:
        (staging / image.name).symlink_to(image)

    config["user_info"]["Directory with FITS files"] = str(staging)
    config["validation_provenance"] = {
        "source_directory": str(source),
        "excluded_leading_frames": [image.name for image in images[:skip]],
        "reason": "target not measurable; coordinates use the first usable reference frame",
    }
    effective_config = output / "effective_config.json"
    effective_config.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    print(
        f"Staged {len(images) - skip}/{len(images)} FITS images; excluded "
        f"{', '.join(image.name for image in images[:skip])}",
        flush=True,
    )
    return effective_config


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("date", choices=sorted(CONFIGS), help="CoRoT-2 observing date")
    args = parser.parse_args()

    config = CONFIGS[args.date]
    if not config.is_file():
        parser.error(f"missing EXOTIC configuration: {config}")

    effective_config = prepare_input_sequence(args.date, config)
    os.environ.setdefault("MPLBACKEND", "Agg")
    exotic_cli.get_ld_values = offline_limb_darkening
    sys.argv = ["exotic", "--reduce", str(effective_config), "--nasaexoarch"]
    result = exotic_cli.main()
    return int(result) if isinstance(result, int) else 0


if __name__ == "__main__":
    raise SystemExit(main())
