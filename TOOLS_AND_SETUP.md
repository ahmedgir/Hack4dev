# Hack4Dev Exoplanet POC - Tools and Setup

This file documents the local scientific environment used for the proof of concept.

## Installed environment

- Environment name: `exoplanet-poc`
- Environment path: `C:\Users\iix_m\miniconda3\envs\exoplanet-poc`
- Python version: `3.10.21`
- Jupyter kernel name: `Python (exoplanet-poc)`

The existing system Python 3.14 was not changed. All astronomy packages are isolated in this environment.

## How to activate the environment

### Beginner mental model

- Conda is the isolated toolbox containing the correct Python and astronomy packages.
- `conda activate exoplanet-poc` selects that toolbox for the current terminal.
- JupyterLab is the visual workspace opened from that toolbox.
- A Jupyter kernel is the Python process that actually runs notebook cells.

Activating Conda does not permanently change Windows or the system Python. It only changes which tools the current terminal uses until it is closed or `conda deactivate` is run.

The easiest method is to open **Miniconda PowerShell Prompt** from the Windows Start menu, then run:

```powershell
conda activate exoplanet-poc
cd C:\Users\iix_m\Downloads\hack4dev
```

From an ordinary PowerShell window, run:

```powershell
& "$env:USERPROFILE\miniconda3\shell\condabin\conda-hook.ps1"
conda activate exoplanet-poc
cd C:\Users\iix_m\Downloads\hack4dev
```

## Core tools

### Miniconda

Purpose: creates an isolated Python environment so the astronomy stack does not conflict with system Python.

Typical commands:

```powershell
conda activate exoplanet-poc
conda deactivate
conda env list
```

### Python 3.10

Purpose: runs the scientific pipeline and is compatible with the installed EXOTIC release.

```powershell
python --version
python script_name.py
```

### EXOTIC 4.3.1

Purpose: the reference exoplanet-transit reduction pipeline. It can process FITS observations, align frames, perform aperture photometry, select comparison stars, fit a transit model, and generate light-curve results.

After activating the environment:

```powershell
exotic
```

The optional graphical launcher is:

```powershell
exotic-gui
```

For this project, EXOTIC should first be used as a scientific baseline on one observation session. Its output should be validated before being connected to the web application.

### Astropy 6.1.7

Purpose: reads FITS images and headers, handles astronomical coordinates, units, and observation time.

Example:

```python
from astropy.io import fits

data = fits.getdata("image.fits")
header = fits.getheader("image.fits")
print(data.shape, header["OBJECT"], header["EXPTIME"])
```

### Photutils 2.0.2

Purpose: measures light inside circular apertures around the target and comparison stars and estimates the sky background using an annulus.

It will be used for transparent, inspectable photometry and for checking EXOTIC results.

### Astroalign 2.6.2 and scikit-image 0.24.0

Purpose: align the image sequence and compensate for telescope drift so that the same stars are measured in every frame.

### NumPy 1.26.4

Purpose: fast numerical operations on FITS pixel arrays.

### Pandas 2.2.3

Purpose: stores per-frame measurements such as time, target flux, comparison flux, background, uncertainty, position drift, and rejection reason. It also exports compact CSV files for the website.

### SciPy 1.14.1

Purpose: scientific calculations, robust statistics, filtering, optimization, and curve fitting.

### Matplotlib 3.9.4

Purpose: produces the first static inspection plots: raw FITS image, calibrated image, detected stars, and light curve.

### Plotly 7.0.0

Purpose: produces interactive charts for the later web experience, including hover details and before/after quality-filter comparisons.

### JupyterLab 4.6.3

Purpose: provides a visual notebook for the proof of concept, mixing code, plots, observations, and scientific explanations.

Launch it after activating the environment:

```powershell
python -m jupyter lab
```

Select the kernel named `Python (exoplanet-poc)` when creating or opening a notebook.

To see the first real FITS images without writing code, open:

```text
notebooks\00_see_the_data.ipynb
```

Then run each cell with `Shift+Enter`.

The completed interactive POC notebook is:

```text
notebooks\01_transit_pipeline_poc.ipynb
```

It uses **ipywidgets 8.1.9** to provide a session selector and frame slider. Moving the slider displays the selected FITS frame, the tracked host-star position, its acceptance/rejection state, and the corresponding point on the light curve.

### Astrometry.net and Gaia

- Astrometry.net solves the sky coordinate system of the selected reference image. It answers: "which direction in the sky does each pixel represent?"
- Gaia supplies catalogued stars after that solution. The pipeline uses it to verify the WASP host and select comparison stars.
- Plate solutions and Gaia results are cached in each output folder, so ordinary reruns do not need another online query.

### ASTAP local solver

ASTAP CLI and the D05/D20 star databases are installed on the main Windows development machine at:

```text
%LOCALAPPDATA%\Programs\ASTAP\astap_cli.exe
```

This makes ASTAP callable by Python or Codex without opening its GUI. Verify the installation with:

```powershell
python scripts\check_astap.py
```

Current status: installation and CLI/database discovery pass. ASTAP was then called automatically on all 18 sessions without cached WCS and solved zero. The repeated failure is associated with the small `650×500`, strongly undersampled fields. ASTAP is therefore **not the production solver for this dataset**. For a new field, the pipeline records the ASTAP attempt, falls back to Astrometry.net, and caches a successful WCS.

### Project POC pipeline

`pipeline/poc_pipeline.py` performs calibration, reference selection, coordinate solving, star tracking, aperture photometry, time conversion, quality filtering, a diagnostic transit fit, and export.

Run all currently verified sessions without network calls:

```powershell
.\run_poc.ps1 --cached-only
```

Run one session (a new session may require an initial online plate solve):

```powershell
.\run_poc.ps1 --target WASP-10 --date 2026-08-08
```

Audit every FITS file and prove session-level completeness:

```powershell
python scripts\audit_dataset.py
python scripts\build_completeness_report.py
```

Generate frame-by-frame WebP assets for the future Timeline:

```powershell
python scripts\build_timeline_previews.py --target CoRoT-2 --date 2026-08-09
```

## Proof-of-concept datasets

Start with the cleaner WASP-10 session:

```text
database\observations\2026-08-08\WASP-10\session_01
```

Use its dark frames from:

```text
database\calibration\2026-08-08
```

The first deliverables should be:

1. A readable rendering of one raw FITS image.
2. The same frame after dark subtraction.
3. Target and comparison stars marked on the image.
4. A normalized differential light curve.
5. Per-frame quality metrics and documented rejection reasons.
6. A comparison between the measured curve and the expected transit.

The current automated run also includes both WASP-2 sessions:

```text
database\observations\2026-08-11\WASP-2\session_01
database\observations\2026-08-24\WASP-2\session_01
```

None of the three processed sessions currently satisfies the required pre-transit, in-transit, and post-transit coverage together with sufficiently low scatter. They are therefore POC and quality-control examples, not transit confirmations.

## Not installed yet

The following are intentionally deferred until the scientific POC works:

- TensorFlow, PyTorch, and GPU/CUDA ML tooling
- Streamlit
- Next.js/React project dependencies
- Hosting and cloud database tools

The final web stack should be chosen after the pipeline outputs and user experience are understood.

## Verified installation

The environment successfully imported EXOTIC, Astropy, Photutils, NumPy, Pandas, SciPy, Matplotlib, Plotly, JupyterLab, and ipywidgets. It also successfully opened a real WASP-10 FITS file and read:

- Object: `WASP-10`
- Shape: `500 x 650`
- Exposure: `60 seconds`
- Filter: `Clear`
