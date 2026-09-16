from __future__ import annotations

import json
import os
import subprocess
import time
from dataclasses import dataclass
from io import StringIO
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
import sep
import astroalign as aa
from astropy.coordinates import EarthLocation, SkyCoord
from astropy.io import fits
from astropy.time import Time
from astropy.wcs import WCS
from astroquery.gaia import Gaia
from exotic.api.plate_solution import PlateSolution
from scipy.ndimage import gaussian_filter, median_filter
from scipy.optimize import least_squares


@dataclass
class SessionPaths:
    root: Path
    target: str
    date: str
    science_dir: Path
    dark_dir: Path
    output_dir: Path


def _robust_sigma(values: np.ndarray) -> float:
    values = np.asarray(values, dtype=float)
    median = np.nanmedian(values)
    sigma = 1.4826 * np.nanmedian(np.abs(values - median))
    return float(sigma if np.isfinite(sigma) and sigma > 0 else np.nanstd(values))


def _paths(root: Path, target: str, date: str) -> SessionPaths:
    science_root = root / "database" / "observations" / date / target
    session_dirs = sorted(path for path in science_root.glob("session_*") if path.is_dir())
    if not session_dirs:
        raise FileNotFoundError(f"No science session found for {target} on {date}")
    dark_dir = root / "database" / "calibration" / date
    output_dir = root / "outputs" / target.lower().replace("-", "_") / date
    output_dir.mkdir(parents=True, exist_ok=True)
    return SessionPaths(root, target, date, session_dirs[0], dark_dir, output_dir)


def _master_dark(paths: SessionPaths) -> tuple[np.ndarray, list[Path], str]:
    dark_paths = sorted(paths.dark_dir.glob("*.fits"))
    dark_source_date = paths.date
    if not dark_paths:
        available = [path for path in (paths.root / "database" / "calibration").glob("*") if path.is_dir()]
        if not available:
            raise FileNotFoundError("No dark calibration directories are available")
        nearest = min(available, key=lambda path: abs(pd.Timestamp(path.name) - pd.Timestamp(paths.date)))
        dark_paths = sorted(nearest.glob("*.fits"))
        dark_source_date = nearest.name
    if not dark_paths:
        raise FileNotFoundError(f"No dark frames found for {paths.date} or its nearest calibration date")
    stack = [fits.getdata(path).astype("float32") for path in dark_paths]
    return np.median(stack, axis=0).astype("float32"), dark_paths, dark_source_date


def _calibrated(path: Path, dark: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
    data = np.ascontiguousarray(fits.getdata(path).astype("float32") - dark)
    background = sep.Background(data, bw=32, bh=32, fw=3, fh=3)
    subtracted = np.ascontiguousarray(data - background.back())
    return data, subtracted, float(background.globalrms)


def _select_reference(science_paths: list[Path], dark: np.ndarray) -> tuple[int, pd.DataFrame]:
    rows = []
    for index, path in enumerate(science_paths):
        raw = fits.getdata(path)
        saturated_fraction = float(np.mean(raw >= 4095))
        _, subtracted, rms = _calibrated(path, dark)
        objects = sep.extract(subtracted, max(4.0 * rms, 1.0), minarea=2)
        strong = objects[objects["peak"] > 8.0 * rms]
        stellar_signal = float(np.sum(np.sort(strong["flux"])[-40:])) if len(strong) else 0.0
        usable_reference = saturated_fraction < 0.05 and len(strong) >= 5
        rows.append({
            "frame_index": index,
            "file_name": path.name,
            "background_rms": rms,
            "detected_sources": int(len(strong)),
            "saturated_fraction_4095": saturated_fraction,
            "usable_reference": usable_reference,
            "reference_score": stellar_signal / max(rms, 1e-6) if usable_reference else 0.0,
        })
    table = pd.DataFrame(rows)
    if not table.usable_reference.any():
        raise RuntimeError("No usable reference frame: all candidates are saturated or contain fewer than five stars")
    return int(table["reference_score"].idxmax()), table


def _make_plate_image(science_path: Path, dark: np.ndarray, destination: Path) -> None:
    _, subtracted, _ = _calibrated(science_path, dark)
    clean = gaussian_filter(subtracted, 0.65)
    noise = _robust_sigma(clean)
    # Ignore bright sensor borders when selecting the display stretch. They can
    # otherwise suppress the actual stars until a solver sees an almost-black image.
    core = clean[15:-15, 15:-15]
    core_median = float(np.nanmedian(core))
    core_noise = _robust_sigma(core)
    low = core_median + 2.0 * core_noise
    high = float(np.nanpercentile(core, 99.97))
    scaled = np.clip((clean - low) / max(high - low, 1e-6), 0, 1)
    display = np.arcsinh(12 * scaled) / np.arcsinh(12)
    plt.imsave(destination, display, cmap="gray", origin="lower", vmin=0, vmax=1)


def _query_gaia_catalog(ra_deg: float, dec_deg: float, radius_deg: float, limit: int = 1500) -> pd.DataFrame:
    """Query the Gaia DR3 VizieR mirror with a bounded synchronous request."""
    query = f"""
    SELECT TOP {limit} Source,RA_ICRS,DE_ICRS,Gmag
    FROM "I/355/gaiadr3"
    WHERE 1=CONTAINS(
        POINT('ICRS',RA_ICRS,DE_ICRS),
        CIRCLE('ICRS',{ra_deg},{dec_deg},{radius_deg})
    )
    AND Gmag BETWEEN 8 AND 16
    ORDER BY Gmag ASC
    """
    response = requests.post(
        "https://tapvizier.cds.unistra.fr/TAPVizieR/tap/sync",
        data={"REQUEST": "doQuery", "LANG": "ADQL", "FORMAT": "csv", "QUERY": query},
        timeout=45,
    )
    response.raise_for_status()
    table = pd.read_csv(StringIO(response.text), dtype={"Source": str})
    return table.rename(columns={
        "Source": "source_id",
        "RA_ICRS": "ra",
        "DE_ICRS": "dec",
        "Gmag": "g_mag",
    })


def _plate_solve(image_path: Path, header, output_dir: Path, timeout_minutes: int = 12) -> Path:
    cache = output_dir / f"wcs_{image_path.stem}.fits"
    if cache.exists():
        return cache
    api = "https://nova.astrometry.net/api/"
    api_key = PlateSolution().api_key["apikey"]
    login = requests.post(
        api + "login",
        data={"request-json": json.dumps({"apikey": api_key})},
        timeout=60,
    ).json()
    options = {
        "session": login["session"],
        "allow_commercial_use": "n",
        "allow_modifications": "n",
        "publicly_visible": "n",
        "scale_units": "arcsecperpix",
        "scale_type": "ul",
        "scale_lower": 4.3,
        "scale_upper": 5.7,
        "center_ra": float(header["RA"]),
        "center_dec": float(header["DEC"]),
        "radius": 2.0,
    }
    with image_path.open("rb") as handle:
        upload = requests.post(
            api + "upload",
            files={"file": handle},
            data={"request-json": json.dumps(options)},
            timeout=120,
        ).json()
    if upload.get("status") != "success":
        raise RuntimeError(f"Astrometry.net upload failed: {upload}")
    subid = upload["subid"]
    deadline = time.time() + timeout_minutes * 60
    jobid = None
    while time.time() < deadline and jobid is None:
        status = requests.get(api + f"submissions/{subid}", timeout=30).json()
        jobs = [job for job in status.get("jobs", []) if job is not None]
        jobid = jobs[0] if jobs else None
        if jobid is None:
            time.sleep(10)
    if jobid is None:
        raise TimeoutError(f"Astrometry.net did not start submission {subid}")
    while time.time() < deadline:
        status = requests.get(api + f"jobs/{jobid}", timeout=30).json().get("status")
        if status == "success":
            response = requests.get(f"https://nova.astrometry.net/wcs_file/{jobid}/", timeout=60)
            response.raise_for_status()
            cache.write_bytes(response.content)
            (output_dir / "plate_solution.json").write_text(
                json.dumps({"submission_id": subid, "job_id": jobid}, indent=2), encoding="utf-8"
            )
            return cache
        if status == "failure":
            raise RuntimeError(f"Astrometry.net job {jobid} failed")
        time.sleep(10)
    raise TimeoutError(f"Astrometry.net job {jobid} timed out")


def _plate_solve_gaia(
    science_path: Path,
    dark: np.ndarray,
    target_cfg: dict,
    output_dir: Path,
) -> Path:
    """Build a constrained WCS by matching image stars to a Gaia cone search."""
    cache = output_dir / f"wcs_plate_solve_{science_path.stem}.fits"
    if cache.exists():
        return cache

    catalog_cache = output_dir / "gaia_solver_catalog.csv"
    if catalog_cache.exists():
        catalog = pd.read_csv(catalog_cache)
    else:
        catalog = _query_gaia_catalog(target_cfg["ra_deg"], target_cfg["dec_deg"], 1.2)
        catalog.to_csv(catalog_cache, index=False)

    _, subtracted, rms = _calibrated(science_path, dark)
    sources = sep.extract(subtracted, max(4.0 * rms, 1.0), minarea=2)
    height, width = subtracted.shape
    sources = sources[sources["flux"] > 0]
    if len(sources) < 6:
        raise RuntimeError(f"Gaia matcher found only {len(sources)} image stars")
    detected_xy = np.column_stack([sources["x"], sources["y"]])
    sources = sources[np.argsort(sources["flux"])[-50:]]
    observed_xy = np.column_stack([sources["x"], (height - 1) - sources["y"]])

    target_coord = SkyCoord(target_cfg["ra_deg"], target_cfg["dec_deg"], unit="deg")
    catalog = catalog.sort_values("g_mag").head(120)
    catalog_coords = SkyCoord(catalog.ra.to_numpy(), catalog.dec.to_numpy(), unit="deg")
    offset_lon, offset_lat = target_coord.spherical_offsets_to(catalog_coords)
    nominal_scale_deg = 5.16 / 3600.0
    synthetic_center = np.array([1000.0, 1000.0])
    catalog_xy = np.column_stack([
        synthetic_center[0] - offset_lon.deg / nominal_scale_deg,
        synthetic_center[1] + offset_lat.deg / nominal_scale_deg,
    ])
    nearby = (
        (np.abs(catalog_xy[:, 0] - synthetic_center[0]) < 700)
        & (np.abs(catalog_xy[:, 1] - synthetic_center[1]) < 700)
    )
    catalog_xy = catalog_xy[nearby]
    if len(catalog_xy) < 12:
        raise RuntimeError(f"Gaia matcher found only {len(catalog_xy)} catalogue stars")

    transform, (matched_image, matched_catalog) = aa.find_transform(
        observed_xy,
        catalog_xy,
        max_control_points=50,
    )
    residuals = np.linalg.norm(transform(matched_image) - matched_catalog, axis=1)
    residual_rms = float(np.sqrt(np.mean(residuals**2)))
    target_pixel_fits = transform.inverse(synthetic_center[None, :])[0]
    target_pixel_array = np.array([target_pixel_fits[0], (height - 1) - target_pixel_fits[1]])
    nearest_image_star = float(
        np.min(np.linalg.norm(detected_xy - target_pixel_array, axis=1))
    )
    match_count = len(matched_image)
    if match_count < 5:
        raise RuntimeError(f"Gaia matcher retained only {match_count} matched stars")
    if not 0.97 <= transform.scale <= 1.03:
        raise RuntimeError(f"Gaia matcher scale is implausible: {transform.scale}")
    if abs(transform.rotation) > 0.03:
        raise RuntimeError(f"Gaia matcher rotation is implausible: {transform.rotation}")
    if residual_rms > 1.25:
        raise RuntimeError(f"Gaia matcher residual is too large: {residual_rms:.3f} px")
    if not (12 <= target_pixel_array[0] < width - 12 and 12 <= target_pixel_array[1] < height - 12):
        raise RuntimeError(f"Gaia matcher places the target outside the usable frame: {target_pixel_array}")
    if nearest_image_star > 2.5:
        raise RuntimeError(f"No detected image star at the Gaia target position ({nearest_image_star:.3f} px)")

    wcs = WCS(naxis=2)
    wcs.wcs.crpix = target_pixel_fits + 1.0
    wcs.wcs.crval = [target_cfg["ra_deg"], target_cfg["dec_deg"]]
    wcs.wcs.ctype = ["RA---TAN", "DEC--TAN"]
    synthetic_cd = np.array([[-nominal_scale_deg, 0.0], [0.0, nominal_scale_deg]])
    wcs.wcs.cd = synthetic_cd @ transform.params[:2, :2]
    solved_header = fits.getheader(science_path).copy()
    solved_header.update(wcs.to_header())
    fits.writeto(cache, fits.getdata(science_path), solved_header, overwrite=True)
    (output_dir / "plate_solution.json").write_text(
        json.dumps({
            "solver": "Gaia catalogue star-pattern match",
            "matched_stars": match_count,
            "residual_rms_px": residual_rms,
            "nearest_target_star_px": nearest_image_star,
            "scale_ratio": float(transform.scale),
            "rotation_radians": float(transform.rotation),
        }, indent=2),
        encoding="utf-8",
    )
    return cache


def _plate_solve_astap(science_path: Path, dark: np.ndarray, output_dir: Path) -> Path:
    """Attempt a local ASTAP solve and return a FITS file containing WCS headers."""
    local_app_data = os.environ.get("LOCALAPPDATA")
    if not local_app_data:
        raise RuntimeError("LOCALAPPDATA is unavailable; ASTAP discovery is Windows-specific")
    executable = Path(local_app_data) / "Programs" / "ASTAP" / "astap_cli.exe"
    if not executable.exists():
        raise FileNotFoundError(f"ASTAP CLI not found: {executable}")
    header = fits.getheader(science_path).copy()
    _, subtracted, _ = _calibrated(science_path, dark)
    # These MicroObservatory stars are severely undersampled (often ~1 px wide).
    # Give ASTAP a positive, gently broadened detection image while preserving
    # the original pixel grid so a successful WCS still maps to the raw frames.
    clean = gaussian_filter(subtracted, 1.15)
    core = clean[15:-15, 15:-15]
    core_median = float(np.nanmedian(core))
    core_noise = _robust_sigma(core)
    low = core_median + 3.0 * core_noise
    high = float(np.nanpercentile(core, 99.97))
    astap_pixels = np.clip((clean - low) / max(high - low, 1e-6), 0, 1)
    astap_pixels = (astap_pixels * 60000).astype("uint16")
    astap_input = output_dir / f"astap_{science_path.stem}.fits"
    fits.writeto(astap_input, astap_pixels, header, overwrite=True)
    ra_hours = float(header["RA"]) / 15.0
    south_pole_distance = float(header["DEC"]) + 90.0
    command = [
        str(executable), "-f", str(astap_input), "-r", "5", "-fov", "0.95",
        "-ra", str(ra_hours), "-spd", str(south_pole_distance), "-D", "d20",
        "-s", "500", "-t", "0.012", "-m", "1", "-speed", "slow", "-update", "-log",
    ]
    result = subprocess.run(command, capture_output=True, text=True, errors="replace", timeout=180)
    solved_header = fits.getheader(astap_input)
    solved = result.returncode == 0 and "CTYPE1" in solved_header and "CRVAL1" in solved_header
    attempt = {
        "solver": "ASTAP",
        "success": solved,
        "return_code": result.returncode,
        "command": command,
        "stdout": result.stdout[-4000:],
        "stderr": result.stderr[-4000:],
    }
    (output_dir / "astap_attempt.json").write_text(json.dumps(attempt, indent=2), encoding="utf-8")
    if not solved:
        raise RuntimeError(f"ASTAP did not solve {science_path.name}; see astap_attempt.json")
    cache = output_dir / f"wcs_plate_solve_{science_path.stem}.fits"
    fits.writeto(cache, fits.getdata(astap_input), solved_header, overwrite=True)
    return cache


def _gaia_catalog(wcs: WCS, shape: tuple[int, int], target_cfg: dict, output_dir: Path) -> pd.DataFrame:
    cache = output_dir / "gaia_catalog.csv"
    if cache.exists():
        return pd.read_csv(cache)
    center = wcs.pixel_to_world((shape[1] - 1) / 2, (shape[0] - 1) / 2)
    corners = wcs.pixel_to_world(
        np.array([0, shape[1] - 1, shape[1] - 1, 0]),
        np.array([0, 0, shape[0] - 1, shape[0] - 1]),
    )
    radius = max(center.separation(corners).deg) * 1.1
    table = _query_gaia_catalog(center.ra.deg, center.dec.deg, radius, limit=1000)
    coords = SkyCoord(ra=table.ra.to_numpy(), dec=table.dec.to_numpy(), unit="deg")
    x, y = wcs.world_to_pixel(coords)
    y = (shape[0] - 1) - y
    frame = pd.DataFrame({
        "source_id": table.source_id.astype(str),
        "ra": table.ra.to_numpy(dtype=float),
        "dec": table.dec.to_numpy(dtype=float),
        "g_mag": table.g_mag.to_numpy(dtype=float),
        "x_ref": x,
        "y_ref": y,
    })
    frame.to_csv(cache, index=False)
    return frame


def _aperture_flux(image: np.ndarray, x: float, y: float, radius: float = 4.0) -> tuple[float, float]:
    height, width = image.shape
    outer = 10
    x0, x1 = max(0, int(x) - outer), min(width, int(x) + outer + 1)
    y0, y1 = max(0, int(y) - outer), min(height, int(y) + outer + 1)
    if x1 - x0 < 2 * outer or y1 - y0 < 2 * outer:
        return np.nan, np.nan
    yy, xx = np.mgrid[y0:y1, x0:x1]
    rr = np.sqrt((xx - x) ** 2 + (yy - y) ** 2)
    aperture = rr <= radius
    annulus = (rr >= 6.0) & (rr <= 9.0)
    sky = float(np.nanmedian(image[y0:y1, x0:x1][annulus]))
    values = image[y0:y1, x0:x1][aperture]
    flux = float(np.nansum(values - sky))
    noise = _robust_sigma(image[y0:y1, x0:x1][annulus])
    snr = flux / max(noise * np.sqrt(aperture.sum()), 1e-6)
    return flux, float(snr)


def _centroid_near(image: np.ndarray, expected: np.ndarray, rms: float, search: int = 7) -> np.ndarray | None:
    x, y = expected
    xi, yi = int(round(x)), int(round(y))
    if xi < search + 2 or yi < search + 2 or xi >= image.shape[1] - search - 2 or yi >= image.shape[0] - search - 2:
        return None
    cut = gaussian_filter(image[yi-search:yi+search+1, xi-search:xi+search+1], 0.7)
    peak_index = np.unravel_index(np.nanargmax(cut), cut.shape)
    if cut[peak_index] < 3.0 * rms:
        return None
    py, px = peak_index
    py0, py1 = max(0, py - 2), min(cut.shape[0], py + 3)
    px0, px1 = max(0, px - 2), min(cut.shape[1], px + 3)
    patch = cut[py0:py1, px0:px1]
    weights = np.clip(patch - np.nanmedian(cut), 0, None)
    if weights.sum() <= 0:
        return None
    yy, xx = np.mgrid[py0:py1, px0:px1]
    cx = xi - search + float((xx * weights).sum() / weights.sum())
    cy = yi - search + float((yy * weights).sum() / weights.sum())
    return np.array([cx, cy])


def _choose_stars(
    catalog: pd.DataFrame,
    target_pixel: np.ndarray,
    reference_subtracted: np.ndarray,
    rms: float,
    target_cfg: dict,
) -> tuple[np.ndarray, pd.DataFrame]:
    height, width = reference_subtracted.shape
    inside = catalog[
        catalog.x_ref.between(20, width - 20)
        & catalog.y_ref.between(20, height - 20)
        & catalog.g_mag.between(target_cfg["gaia_mag"] - 2.5, target_cfg["gaia_mag"] + 2.0)
    ].copy()
    distance = np.sqrt((inside.x_ref - target_pixel[0]) ** 2 + (inside.y_ref - target_pixel[1]) ** 2)
    inside = inside[distance > 25].copy()
    fluxes, snrs = [], []
    for row in inside.itertuples():
        flux, snr = _aperture_flux(reference_subtracted, row.x_ref, row.y_ref)
        fluxes.append(flux)
        snrs.append(snr)
    inside["reference_flux"] = fluxes
    inside["reference_snr"] = snrs
    selected = inside[(inside.reference_snr > 8) & (inside.reference_flux > 0)].nlargest(10, "reference_snr")
    if len(selected) < 4:
        selected = inside[(inside.reference_snr > 4) & (inside.reference_flux > 0)].nlargest(10, "reference_snr")
    if len(selected) < 3:
        raise RuntimeError(f"Only {len(selected)} reliable comparison stars found")
    anchors = np.vstack([target_pixel, selected[["x_ref", "y_ref"]].to_numpy()])
    return anchors, selected.reset_index(drop=True)


def _track_and_measure(
    science_paths: list[Path],
    dark: np.ndarray,
    reference_index: int,
    anchors: np.ndarray,
) -> pd.DataFrame:
    records: list[dict] = [None] * len(science_paths)  # type: ignore

    def measure(index: int, previous_shift: np.ndarray) -> tuple[dict, np.ndarray]:
        path = science_paths[index]
        calibrated, subtracted, rms = _calibrated(path, dark)
        estimates = []
        for anchor in anchors:
            centroid = _centroid_near(subtracted, anchor + previous_shift, rms)
            if centroid is not None:
                estimates.append(centroid - anchor)
        if estimates:
            estimates_array = np.asarray(estimates)
            shift = np.nanmedian(estimates_array, axis=0)
            residuals = np.sqrt(((estimates_array - shift) ** 2).sum(axis=1))
            inliers = estimates_array[residuals < 2.0]
            if len(inliers) >= 2:
                shift = np.nanmedian(inliers, axis=0)
        else:
            shift = previous_shift.copy()
            inliers = np.empty((0, 2))
        fluxes, snrs = [], []
        for anchor in anchors:
            flux, snr = _aperture_flux(calibrated, *(anchor + shift))
            fluxes.append(flux)
            snrs.append(snr)
        header = fits.getheader(path)
        record = {
            "frame_index": index,
            "file_name": path.name,
            "mjd_utc": float(header["MJD-OBS"]) + float(header.get("EXPTIME", 60.0)) / 2 / 86400,
            "weather": float(header.get("WEATHER", np.nan)),
            "background_rms": rms,
            "shift_x": float(shift[0]),
            "shift_y": float(shift[1]),
            "registration_stars": int(len(inliers)),
            "target_flux": fluxes[0],
            "target_snr": snrs[0],
        }
        for comp_index, (flux, snr) in enumerate(zip(fluxes[1:], snrs[1:]), start=1):
            record[f"comp_{comp_index}_flux"] = flux
            record[f"comp_{comp_index}_snr"] = snr
        return record, shift

    records[reference_index], _ = measure(reference_index, np.zeros(2))
    shift = np.zeros(2)
    for index in range(reference_index + 1, len(science_paths)):
        records[index], shift = measure(index, shift)
    shift = np.zeros(2)
    for index in range(reference_index - 1, -1, -1):
        records[index], shift = measure(index, shift)
    return pd.DataFrame(records).sort_values("frame_index").reset_index(drop=True)


def _time_and_lightcurve(table: pd.DataFrame, target_cfg: dict, header) -> tuple[pd.DataFrame, dict]:
    location = EarthLocation.from_geodetic(
        lon=float(header["LONGITUD"]), lat=float(header["LATITUDE"]), height=float(header["HEIGHT"])
    )
    target_coord = SkyCoord(target_cfg["ra_deg"], target_cfg["dec_deg"], unit="deg")
    times = Time(table.mjd_utc.to_numpy(), format="mjd", scale="utc", location=location)
    table["bjd_tdb"] = (times.tdb + times.light_travel_time(target_coord)).jd
    comp_columns = [column for column in table if column.startswith("comp_") and column.endswith("_flux")]
    provisional = (table.registration_stars >= 2) & (table.target_flux > 0) & (table.target_snr > 3)
    normalized_comps = []
    used_comp_columns = []
    for column in comp_columns:
        median = np.nanmedian(table.loc[provisional & (table[column] > 0), column])
        if np.isfinite(median) and median > 0:
            normalized_comps.append(table[column].to_numpy() / median)
            used_comp_columns.append(column)
    if len(normalized_comps) < 2:
        raise RuntimeError("Fewer than two comparison stars survived photometry")
    ensemble = np.nanmedian(np.vstack(normalized_comps), axis=0)
    target_median = np.nanmedian(table.loc[provisional, "target_flux"])
    table["ensemble_flux"] = ensemble
    table["differential_flux"] = (table.target_flux / target_median) / ensemble
    ensemble_good = np.nanmedian(ensemble[provisional])
    rms_limit = np.nanmedian(table.background_rms) + 4 * _robust_sigma(table.background_rms.to_numpy())
    table["reject_registration"] = table.registration_stars < 2
    table["reject_target_flux"] = ~(table.target_flux > 0)
    table["reject_target_snr"] = ~(table.target_snr > 3)
    table["reject_nonfinite_flux"] = ~np.isfinite(table.differential_flux)
    table["reject_comparison_ensemble"] = ~(ensemble > 0.30 * ensemble_good)
    table["reject_background"] = ~(table.background_rms < rms_limit)
    reject_columns = [column for column in table if column.startswith("reject_")]
    table["accepted"] = ~table[reject_columns].any(axis=1)
    table["rejection_reason"] = table[reject_columns].apply(
        lambda row: ";".join(column.removeprefix("reject_") for column, rejected in row.items() if rejected)
        or "accepted",
        axis=1,
    )
    period = target_cfg["period_days"]
    epoch = target_cfg["epoch_bjd"]
    expected_mid = epoch + round((np.nanmedian(table.bjd_tdb) - epoch) / period) * period
    duration_days = target_cfg["duration_hours"] / 24
    dt_hours = (table.bjd_tdb - expected_mid) * 24
    table["hours_from_expected_mid"] = dt_hours
    good = table.accepted.to_numpy()
    outside = good & (np.abs(dt_hours) > target_cfg["duration_hours"] * 0.62)
    if outside.sum() >= 6:
        coeff = np.polyfit(dt_hours[outside], table.loc[outside, "differential_flux"], 1)
        baseline = np.polyval(coeff, dt_hours)
    else:
        coeff = np.array([0.0, np.nanmedian(table.loc[good, "differential_flux"])])
        baseline = np.polyval(coeff, dt_hours)
    table["detrended_flux"] = table.differential_flux / baseline

    def trapezoid(parameters, hours):
        depth, midpoint, duration, ingress_fraction = parameters
        distance = np.abs(hours - midpoint)
        half = duration / 2
        ingress = max(duration * ingress_fraction, 0.05)
        shape = np.clip((half - distance) / ingress + 1, 0, 1)
        return 1 - depth * shape

    fit_good = good & np.isfinite(table.detrended_flux)
    initial = [target_cfg["published_depth_percent"] / 100, 0.0, target_cfg["duration_hours"], 0.15]
    bounds = ([0.0, -0.8, 0.5 * target_cfg["duration_hours"], 0.05],
              [0.10, 0.8, 1.5 * target_cfg["duration_hours"], 0.35])
    result = least_squares(
        lambda p: trapezoid(p, dt_hours[fit_good]) - table.loc[fit_good, "detrended_flux"].to_numpy(),
        initial,
        bounds=bounds,
        loss="soft_l1",
        f_scale=0.01,
    )
    model = trapezoid(result.x, dt_hours.to_numpy())
    table["transit_model"] = model
    residual_scatter = _robust_sigma((table.loc[fit_good, "detrended_flux"] - model[fit_good]).to_numpy())
    coverage = {
        "pre_transit_points": int((fit_good & (dt_hours < -target_cfg["duration_hours"] / 2)).sum()),
        "in_transit_points": int((fit_good & (np.abs(dt_hours) <= target_cfg["duration_hours"] / 2)).sum()),
        "post_transit_points": int((fit_good & (dt_hours > target_cfg["duration_hours"] / 2)).sum()),
    }
    summary = {
        "expected_mid_bjd_tdb": float(expected_mid),
        "published_depth_percent": float(target_cfg["published_depth_percent"]),
        "fitted_depth_percent": float(result.x[0] * 100),
        "fitted_mid_offset_minutes": float(result.x[1] * 60),
        "fitted_duration_hours": float(result.x[2]),
        "residual_scatter_percent": float(residual_scatter * 100),
        "accepted_frames": int(good.sum()),
        "total_frames": int(len(table)),
        "comparison_stars_used": len(used_comp_columns),
        **coverage,
    }
    summary["coverage_complete"] = (
        summary["pre_transit_points"] >= 5
        and summary["in_transit_points"] >= 10
        and summary["post_transit_points"] >= 5
    )
    summary["precision_sufficient"] = (
        summary["residual_scatter_percent"] < max(1.5, summary["published_depth_percent"])
    )
    depth_ratio = summary["fitted_depth_percent"] / max(summary["published_depth_percent"], 1e-6)
    duration_ratio = summary["fitted_duration_hours"] / max(target_cfg["duration_hours"], 1e-6)
    summary["depth_ratio_to_published"] = float(depth_ratio)
    summary["duration_ratio_to_published"] = float(duration_ratio)
    summary["depth_consistent"] = 0.5 <= depth_ratio <= 1.75
    summary["duration_consistent"] = 0.65 <= duration_ratio <= 1.35
    summary["timing_consistent"] = (
        abs(summary["fitted_mid_offset_minutes"]) <= 0.25 * target_cfg["duration_hours"] * 60
    )
    consistent_fit = (
        summary["depth_consistent"]
        and summary["duration_consistent"]
        and summary["timing_consistent"]
    )
    if summary["coverage_complete"] and summary["precision_sufficient"] and consistent_fit:
        summary["scientific_status"] = "promising_preliminary_transit"
    elif summary["coverage_complete"] and summary["precision_sufficient"]:
        summary["scientific_status"] = "transit_like_but_parameters_inconsistent"
    else:
        summary["scientific_status"] = "insufficient_for_transit_claim"
    summary["fit_valid"] = summary["scientific_status"] == "promising_preliminary_transit"
    summary["fit_interpretation"] = (
        "preliminary_candidate"
        if summary["fit_valid"]
        else "diagnostic_only_do_not_claim_transit"
    )
    return table, summary


def _plots(
    table: pd.DataFrame,
    summary: dict,
    reference_subtracted: np.ndarray,
    target_pixel: np.ndarray,
    comparisons: pd.DataFrame,
    cfg: dict,
    output_dir: Path,
) -> None:
    low, high = np.nanpercentile(reference_subtracted, [2, 99.9])
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.imshow(reference_subtracted, origin="lower", cmap="gray", vmin=low, vmax=high)
    ax.scatter(target_pixel[0], target_pixel[1], s=360, facecolors="none", edgecolors="#ffbf00", linewidths=2.5, label=cfg["planet_name"].replace(" b", ""))
    ax.scatter(comparisons.x_ref, comparisons.y_ref, s=150, facecolors="none", edgecolors="#23b5d3", linewidths=1.5, label="Gaia comparison stars")
    ax.legend(loc="upper right")
    ax.set(title=f"Verified field: {cfg['planet_name']}", xlabel="X pixel", ylabel="Y pixel")
    fig.tight_layout()
    fig.savefig(output_dir / "01_verified_field.png", dpi=160)
    plt.close(fig)

    good = table.accepted.to_numpy()
    fig, ax = plt.subplots(figsize=(11, 6))
    accepted_flux = table.loc[good, "detrended_flux"].to_numpy(dtype=float)
    accepted_flux = accepted_flux[np.isfinite(accepted_flux)]
    center = float(np.nanmedian(accepted_flux)) if accepted_flux.size else 1.0
    scatter = _robust_sigma(accepted_flux) if accepted_flux.size else 0.02
    half_range = max(5 * scatter, 2 * cfg["published_depth_percent"] / 100, 0.03)
    half_range = min(half_range, 0.25)
    y_min, y_max = center - half_range, center + half_range
    rejected_x = table.loc[~good, "hours_from_expected_mid"]
    ax.scatter(rejected_x, np.full(len(rejected_x), y_min + 0.015 * (y_max - y_min)),
               marker="x", s=25, color="0.65", label="Rejected frame (position only)")
    ax.scatter(table.loc[good, "hours_from_expected_mid"], table.loc[good, "detrended_flux"], s=28, color="#1769aa", label="Accepted")
    order = np.argsort(table.hours_from_expected_mid)
    fit_label = "Preliminary fit" if summary["fit_valid"] else "Diagnostic fit (not scientifically valid)"
    ax.plot(table.hours_from_expected_mid.iloc[order], table.transit_model.iloc[order],
            color="#d1495b", linewidth=2, linestyle="-" if summary["fit_valid"] else "--", label=fit_label)
    half = cfg["duration_hours"] / 2
    ax.axvspan(-half, half, color="#f4a261", alpha=0.13, label="Published transit window")
    ax.axhline(1, color="0.3", linewidth=1)
    ax.set_ylim(y_min, y_max)
    ax.set(title=f"{cfg['planet_name']} differential light curve", xlabel="Hours from expected mid-transit", ylabel="Normalized relative flux")
    ax.legend(ncol=2)
    fig.tight_layout()
    fig.savefig(output_dir / "02_light_curve.png", dpi=160)
    plt.close(fig)

    fig, axes = plt.subplots(3, 1, figsize=(11, 9), sharex=True)
    axes[0].plot(table.hours_from_expected_mid, table.ensemble_flux, ".-", color="#5e548e")
    axes[0].set_ylabel("Comparison ensemble")
    axes[1].plot(table.hours_from_expected_mid, table.shift_x, label="X shift")
    axes[1].plot(table.hours_from_expected_mid, table.shift_y, label="Y shift")
    axes[1].set_ylabel("Shift (pixels)")
    axes[1].legend()
    axes[2].plot(table.hours_from_expected_mid, table.background_rms, ".-", color="#2a9d8f")
    axes[2].scatter(table.loc[~good, "hours_from_expected_mid"], table.loc[~good, "background_rms"], color="#d1495b", label="Rejected")
    axes[2].set(xlabel="Hours from expected mid-transit", ylabel="Background RMS")
    axes[2].legend()
    fig.suptitle(f"Quality-control evidence: {cfg['planet_name']}")
    fig.tight_layout()
    fig.savefig(output_dir / "03_quality_control.png", dpi=160)
    plt.close(fig)


def run_target(
    root: str | Path,
    target: str,
    date: str,
    allow_plate_solve: bool = True,
    prefer_astap: bool = True,
) -> dict:
    root = Path(root).resolve()
    cfg = json.loads((root / "config" / "targets.json").read_text(encoding="utf-8"))[target]
    paths = _paths(root, target, date)
    science_paths = sorted(paths.science_dir.glob("*.fits"))
    dark, dark_paths, dark_source_date = _master_dark(paths)
    reference_index, reference_scores = _select_reference(science_paths, dark)
    reference_path = science_paths[reference_index]
    header = fits.getheader(reference_path)
    plate_png = paths.output_dir / f"plate_solve_{reference_path.stem}.png"
    _make_plate_image(reference_path, dark, plate_png)
    wcs_path = paths.output_dir / f"wcs_{plate_png.stem}.fits"
    plate_solution = "astrometry.net WCS cache"
    flip_wcs_y = True
    if not wcs_path.exists():
        gaia_error = None
        astap_error = None
        if allow_plate_solve:
            try:
                wcs_path = _plate_solve_gaia(reference_path, dark, cfg, paths.output_dir)
                plate_solution = "Gaia catalogue star-pattern match"
            except Exception as exc:
                gaia_error = repr(exc)
        if not wcs_path.exists() and prefer_astap:
            try:
                wcs_path = _plate_solve_astap(reference_path, dark, paths.output_dir)
                plate_solution = "ASTAP local"
                flip_wcs_y = False
            except Exception as exc:
                astap_error = repr(exc)
        if not wcs_path.exists():
            if not allow_plate_solve:
                raise FileNotFoundError(
                    f"Missing cached WCS; Gaia result: {gaia_error}; ASTAP result: {astap_error}"
                )
            wcs_path = _plate_solve(plate_png, header, paths.output_dir)
            plate_solution = "Astrometry.net online"
    else:
        solution_metadata = paths.output_dir / "plate_solution.json"
        if solution_metadata.exists():
            metadata = json.loads(solution_metadata.read_text(encoding="utf-8"))
            plate_solution = metadata.get("solver", plate_solution)
    wcs = WCS(fits.getheader(wcs_path))
    target_coord = SkyCoord(cfg["ra_deg"], cfg["dec_deg"], unit="deg")
    target_pixel = np.array(wcs.world_to_pixel(target_coord), dtype=float)
    shape = fits.getdata(reference_path).shape
    if flip_wcs_y:
        target_pixel[1] = (shape[0] - 1) - target_pixel[1]
    if not (0 <= target_pixel[0] < shape[1] and 0 <= target_pixel[1] < shape[0]):
        raise RuntimeError(f"Target projects outside the solved frame at {target_pixel.tolist()}")
    _, reference_subtracted, reference_rms = _calibrated(reference_path, dark)
    catalog = _gaia_catalog(wcs, shape, cfg, paths.output_dir)
    if not flip_wcs_y:
        catalog["y_ref"] = (shape[0] - 1) - catalog["y_ref"]
    anchors, comparisons = _choose_stars(catalog, target_pixel, reference_subtracted, reference_rms, cfg)
    table = _track_and_measure(science_paths, dark, reference_index, anchors)
    table, summary = _time_and_lightcurve(table, cfg, header)
    summary.update({
        "target": target,
        "planet_name": cfg["planet_name"],
        "date": date,
        "reference_frame_index": reference_index,
        "reference_file": reference_path.name,
        "target_x_reference": float(target_pixel[0]),
        "target_y_reference": float(target_pixel[1]),
        "dark_frames": len(dark_paths),
        "dark_source_date": dark_source_date,
        "same_date_dark": dark_source_date == date,
        "plate_solution": plate_solution,
    })
    table.to_csv(paths.output_dir / "photometry.csv", index=False)
    reference_scores.to_csv(paths.output_dir / "frame_reference_scores.csv", index=False)
    comparisons.to_csv(paths.output_dir / "comparison_stars.csv", index=False)
    (paths.output_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    web_columns = [
        "frame_index", "file_name", "mjd_utc", "bjd_tdb", "hours_from_expected_mid",
        "detrended_flux", "transit_model", "accepted", "rejection_reason", "target_snr",
        "background_rms", "registration_stars", "shift_x", "shift_y",
    ]
    web_points = table[web_columns].copy()
    web_points["preview_path"] = web_points.frame_index.map(lambda value: f"timeline_frames/{value:04d}.webp")
    (paths.output_dir / "web_timeline.json").write_text(web_points.to_json(orient="records"), encoding="utf-8")
    (paths.output_dir / "web_light_curve.json").write_text(web_points.to_json(orient="records"), encoding="utf-8")
    _plots(table, summary, reference_subtracted, target_pixel, comparisons, cfg, paths.output_dir)
    return summary
