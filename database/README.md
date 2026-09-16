# MicroObservatory Exoplanet Database
    
## Dataset Information
- **Source**: MicroObservatory Image Directory
- **Search Criteria**: ExoPlanets (Last 30 Days)
- **Download Date**: 2026-09-06 01:13:30
- **Total FITS Files**: 1741
- **Science Images**: 1681
- **Calibration Images**: 60
- **Failed Downloads**: 0
- **Total Targets**: 8
- **Total Disk Space**: 1091.94 MB

## Folder Structure
- `observations/`: Contains science images organized by `YYYY-MM-DD/TARGET/session_id/`
- `calibration/`: Contains calibration images (Dark, Bias, Flat) organized by `YYYY-MM-DD/`
- `metadata/`: Contains logs and metadata CSV/JSON files.

## Technical Details
- Duplicate protection verifies file existence and validates the FITS header via `astropy`.
- Invalid or incomplete files are automatically redownloaded.
- Observation sessions are determined intelligently based on target, date, and gaps in exposure time.
- EXOTIC Compatibility: Original FITS files are preserved as downloaded without alteration.
