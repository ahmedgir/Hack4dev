# Hack4Dev Exoplanet Project State

Last updated: 2026-09-15

## Current objective

Build a scientifically defensible proof of concept before designing the final web application.

The product direction is an Arabic/English, non-technical explanation experience that turns raw telescope images into understandable evidence of a known exoplanet transit while allowing judges and technical reviewers to inspect the underlying measurements and limitations.

## Current challenge decision

**Provisional primary challenge: E - Discovery Tool.**

The official submission must name one challenge. Challenge E is the best current fit because the final deliverable is an interactive tool connected to the real dataset and designed around a clear user need.

The project will still use methods associated with other challenges:

- D - FITS Analysis supplies the scientific data-processing pipeline.
- A - Transit Hunter supplies transit-like signal interpretation.
- B - Analyst supplies data-quality analysis and documented cleaning.

These are implementation methods, not separate challenge claims.

This decision becomes final only after the POC proves that we can produce at least one defensible light curve and explain the difference between a clean and a problematic session. If this fails, reconsider D as the primary challenge or B as a lower-risk data-quality project.

## Verified dataset facts

- 1,741 FITS files in total.
- 1,681 science images.
- 60 dark calibration images.
- 8 observed host stars.
- 22 observation sessions.
- Typical exposure: 60 seconds.
- Typical cadence: about 3 minutes.
- Image dimensions: 650 x 500 pixels.
- Telescope: Cecilia at the MicroObservatory/Whipple site.
- Science filter: Clear.
- Calibration filter: Opaque.
- The sessions appear to be intentionally centered on predicted transits of already-confirmed planets.
- The dataset is not a labelled planet-versus-false-planet ML dataset.

## Verified data issues

- `dataset_index.csv` has a blank exposure column because `index.py` reads `EXPOSURE` while the files use `EXPTIME`.
- Only dark calibration files were found; no bias or flat frames were found.
- Most calibration-date folders contain only two dark frames.
- The 2026-09-04 TRES-5 session has no same-date dark folder.
- A preliminary pixel audit found 32 frames that are more than 50% saturated at value 4095. This is an exploratory flag, not yet a scientific rejection rule.
- Several sessions show strongly varying image backgrounds and need explicit quality control.

## Installed scientific environment

- Miniconda installed for the current Windows user.
- Environment: `exoplanet-poc`
- Python 3.10.21
- EXOTIC 4.3.1
- Astropy 6.1.7
- Photutils 2.0.2
- NumPy 1.26.4
- Pandas 2.2.3
- SciPy 1.14.1
- Matplotlib 3.9.4
- Plotly 7.0.0
- JupyterLab 4.6.3

All package imports passed, `pip check` found no broken requirements, and a real WASP-10 FITS image was opened successfully.

## POC plan

### Clean-session case

Use:

```text
database\observations\2026-08-08\WASP-10\session_01
database\calibration\2026-08-08
```

Required outputs:

1. Raw FITS image rendered visibly.
2. Dark frame rendered visibly.
3. Dark-corrected science image.
4. Target and comparison stars marked.
5. Normalized differential light curve.
6. Quality metrics and rejection reasons per frame.
7. Comparison with the expected transit window/model.

### Problematic-session case

Use:

```text
database\observations\2026-08-17\TRES-5\session_01
```

Goal: demonstrate how obvious bad frames distort the result and how documented quality control changes it.

## Expected website data products

The final website should not load or process all 1.1 GB of FITS files live. The Python pipeline will precompute compact web-ready artifacts:

- selected PNG/WebP image previews;
- raw and calibrated image comparisons;
- per-frame quality metrics in CSV/Parquet;
- light-curve points in compact JSON;
- session summaries and limitations in JSON;
- target and comparison-star coordinates;
- rejected-frame reasons;
- expected-versus-measured transit parameters.

The raw FITS data and reproducible pipeline remain in the project for scientific verification. The web interface consumes the compact derived outputs.

## Team roles under consideration

- Hussein: product lead, integration, scope, presentation, and final scientific story.
- Ahmed Haider: user research, UX journey, visual system, and accessible explanation.
- Ahmed Bari: scientific pipeline and backend outputs, preferably through asynchronous tasks with explicit input/output contracts.
- Zainab: data-quality rules, scientific review, interpretation, and visual/data review.

## Decisions intentionally deferred

- Final frontend framework.
- Hosting provider.
- Whether Streamlit is needed as a fallback.
- Any ML component.
- Final product name and visual identity.
- Whether external NASA Archive data is included in the demo.

## POC completion checkpoint

The automated pipeline now processes four sessions end-to-end. The initial three were:

- WASP-10 on 2026-08-08: 31/86 accepted; 4/27/0 pre/in/post points; 4.276% residual scatter.
- WASP-2 on 2026-08-11: 22/78 accepted; 0/22/0 pre/in/post points; 0.855% residual scatter.
- WASP-2 on 2026-08-24: 40/77 accepted; 0/9/31 pre/in/post points; 9.468% residual scatter.

A fourth, deliberately selected session produced the first promising result:

- CoRoT-2 on 2026-08-09: 73/87 accepted; 11/45/17 pre/in/post points; 1.690% residual scatter. The fitted depth is 3.184% versus 2.75% published, the fitted duration is 2.509 versus 2.267 hours, and the midpoint offset is about -4.2 minutes. Status: `promising_preliminary_transit`.

The three WASP runs are explicitly labelled `insufficient_for_transit_claim`. CoRoT-2 is a promising recovery of a known transit, not an independent planet confirmation; it still needs a second-session check and independent EXOTIC validation.

The pipeline now exports verified-field images, readable light curves, quality-control plots, full per-frame photometry CSV, comparison-star CSV, session summary JSON, and compact web light-curve JSON. Cached plate solutions make reruns deterministic and avoid waiting for Astrometry.net.

The executed notebook `notebooks/01_transit_pipeline_poc.ipynb` presents these results and includes an interactive FITS-frame slider synchronized with the light curve.

## Immediate next decision gate

The technical POC is proven, but the scientific signal is not. The next phase has two tracks:

1. Slow down and document the complete Discovery Webapp story, every tool, every input/output, and the explanation for the rest of the team.
2. Later, batch-screen the remaining sessions for complete transit coverage and lower scatter, then validate the best candidate independently with EXOTIC before making any detection claim.

## First user observation

The first notebook run displayed the science frame as nearly white and the dark frame as a confusing dotted image. This was a visualization problem, not a user knowledge problem. The notebook was revised to use robust intensity limits, show a background-removed display view, explain that WASP-10 is the host star and WASP-10 b is the invisible planet, and clarify that a dark frame represents sensor noise rather than the sky.

This feedback validates a central product need: raw astronomical data is not self-explanatory. The Discovery Tool must progressively reveal what the user is seeing instead of displaying scientific plots without context.

## WASP-10 identification checkpoint (resolved)

- The FITS header identifies the field as `WASP-10`, with pointing coordinates RA `349.308497`, Dec `31.605056`, an image scale of about 5 arcsec/pixel, and 60-second exposures.
- SIMBAD resolves the host star WASP-10 to RA `348.99291924226`, Dec `31.46286001563`.
- The files do not contain a complete WCS solution, so the host star could not be labelled from the header alone.
- An early raw-frame Astrometry.net attempt failed. A Gaia geometric match with only nine matches and a 37.99-pixel target residual was rejected and must not be reused as evidence.
- Stacking the 86 frames without registration produced visible short trails. This demonstrates real field drift during the session. The apparent motion is telescope/camera drift, not evidence of the exoplanet.
- A better reference frame was selected automatically and solved successfully. Correcting the display/WCS Y-axis convention placed WASP-10 at approximately `(203.08, 188.82)` in `WASP-10260808083916.fits`.
- The blue circles in the current verified-field image are Gaia comparison stars. The yellow circle is the catalogue position of the WASP-10 host, not a visible planet.

### Next technical action

Preserve the current POC as a transparent baseline. Do not tune its rejection rules until the team understands the evidence and failure modes. The next scientific run should screen all remaining sessions with an explicit coverage/precision score and reserve EXOTIC as an independent validation path.
