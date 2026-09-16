# Hack4Dev Exoplanet Project — Conversation Recap

## User

Now that you have access to all the files, walk me through what we should start working on now.

---

## Codex

I reviewed the challenge notes and inspected the complete workspace, including:

- `observations/`
- `calibration/`
- `metadata/`
- `dataset_index.csv`
- `README.md`
- Sample science and calibration FITS headers

The dataset is complete enough to begin the project. It contains real astronomical telescope images organized into repeated observation sessions.

## Verified dataset information

- **Source:** MicroObservatory Exoplanet Database
- **Total FITS files:** 1,741
- **Science images:** 1,681
- **Calibration images:** 60
- **Science targets:** 8
- **Dataset size:** approximately 1.1 GB
- **Science filter:** Clear
- **Calibration filter:** Opaque
- **Image dimensions:** 650 × 500 pixels
- **Science exposure time:** 60 seconds
- **Typical cadence:** approximately one image every 3 minutes
- **Telescope:** Cecilia at Whipple Observatory, Arizona

The eight science targets are:

| Target | Science images |
|---|---:|
| TRES-5 | 427 |
| CoRoT-2 | 346 |
| TRES-3 | 261 |
| Qatar-1 | 222 |
| WASP-2 | 155 |
| HATP-10 | 93 |
| TRES-1 | 91 |
| WASP-10 | 86 |

The observations are not isolated images. They are dense time-series sequences, which means we can attempt real differential photometry and generate light curves.

---

# Recommended project

## Exoplanet Discovery Dashboard

We should build an interactive scientific dashboard that transforms raw FITS telescope images into explainable light curves and highlights possible transit-like signals.

The project combines:

- **Challenge D:** FITS analysis
- **Challenge E:** Interactive discovery tool
- **A limited part of Challenge A:** Transit-signal analysis

The proposed pitch is:

> An explainable exoplanet observation explorer that transforms raw telescope FITS images into calibrated light curves and helps researchers prioritize transit-like signals for further investigation.

We must not claim that the project discovers or confirms a planet. A brightness dip should be described as:

> A potential transit-like signal requiring further confirmation.

---

# What we should work on first

Our first goal should be narrow and measurable:

> Produce one scientifically defensible light curve from one complete observation session.

We should not start by processing all 1,681 science images. We should first prove that the complete pipeline works for one session.

## Recommended first session

- **Target:** TRES-1
- **Date:** 2026-08-06
- **Frames:** 91
- **Duration:** approximately 5 hours
- **Median cadence:** approximately 3 minutes
- **Exposure:** 60 seconds per frame
- **Calibration:** Matching dark frames are available for this date

This is a strong first test because it has long time coverage, many exposures, and same-date dark calibration data.

---

# First scientific pipeline

The initial Python pipeline should perform these steps:

```text
FITS science images
        ↓
Read image arrays and FITS metadata
        ↓
Create a master dark frame
        ↓
Subtract the master dark
        ↓
Align the image sequence
        ↓
Detect the target and comparison stars
        ↓
Perform aperture photometry
        ↓
Calculate differential brightness
        ↓
Normalize the measurements
        ↓
Generate the light curve
        ↓
Evaluate quality and possible dips
```

Differential brightness should be calculated approximately as:

```text
target-star flux / combined comparison-star flux
```

Using comparison stars helps distinguish a genuine change in the target from clouds, atmospheric variation, or other effects that influence the entire image.

## First success criterion

The initial goal is not to detect a planet. It is to answer:

> Can we extract a stable, explainable light curve from the real FITS images?

If the answer is yes, the hardest and most important part of the project is working.

---

# Validation requirements

Before creating a transit score, the project should calculate and display:

- Target-star flux
- Comparison-star ensemble flux
- Image background level
- Target position drift
- Signal-to-noise ratio
- Measurement uncertainty
- Rejected frames
- The reason each frame was rejected
- Normalized relative flux

This is necessary because an apparent brightness dip could be caused by:

- Clouds or atmospheric transparency changes
- Telescope tracking movement
- A star moving outside the measurement aperture
- Saturated pixels
- High image background
- Cosmic rays
- Poor comparison stars
- Bad or corrupted frames

The dashboard must explain why a signal was highlighted and what its limitations are.

---

# Dashboard structure

After producing the first valid light curve, we should build a Streamlit application with four focused pages.

## 1. Dataset Overview

Display:

- Total FITS files
- Science and calibration image counts
- Available targets
- Observation dates
- Session lengths
- Filters and exposure times
- Images per target

## 2. FITS Explorer

Allow the user to:

- Select a target, date, session, and image
- View the raw or calibrated FITS image
- Adjust image display scaling
- View a pixel-value histogram
- Inspect important FITS header fields
- See detected stars and photometry apertures

## 3. Light Curve Lab

Allow the user to:

- Select a processed observation session
- View the normalized light curve
- Compare target and reference-star behavior
- Inspect rejected frames
- View uncertainty and quality metrics
- Highlight a possible transit-like dip
- Read an explanation of why the dip may or may not be trustworthy

## 4. Candidate Comparison

Compare processed sessions using explainable measurements such as:

- Possible dip depth
- Possible dip duration
- Light-curve noise
- Observation coverage
- Number of usable frames
- Comparison-star stability
- Overall evidence or quality score

The score should prioritize observations for human review. It should not be presented as a probability that a planet exists.

---

# Important issues discovered

## 1. Exposure metadata bug

The existing `index.py` script searches for this FITS keyword:

```python
header.get("EXPOSURE")
```

However, the real FITS files store exposure time under:

```python
header.get("EXPTIME")
```

This is why the `exposure` column in `dataset_index.csv` is currently blank. The indexing code should be corrected and the index regenerated.

## 2. Limited calibration data

The calibration directory appears to contain dark frames only. Bias and flat-field frames were not found.

Therefore:

- We can perform dark subtraction.
- We cannot honestly describe the pipeline as fully bias- and flat-corrected.
- This limitation must be documented in the dashboard, README, and presentation.
- Same-date dark frames should be used where available.

## 3. Python environment

The currently detected system Python is version 3.14 and does not have Astropy installed. To reduce package compatibility risk during the hackathon, a dedicated Python 3.12 virtual environment is recommended.

Suggested libraries:

```text
astropy
photutils
numpy
pandas
scipy
scikit-image
plotly
streamlit
```

GPU training is not required. The RTX 5070 is not the main advantage for this project; CPU processing, memory, caching, and a reliable scientific pipeline matter more.

---

# Recommended execution order

## Stage 1 — Environment and data verification

Estimated time: 30–45 minutes

1. Create a Python 3.12 virtual environment.
2. Install the scientific dependencies.
3. Correct `EXPOSURE` to `EXPTIME` in the indexer.
4. Regenerate or repair the dataset index.
5. Load and display one science FITS image.
6. Load and display one dark frame.
7. Confirm the image arrays, timestamps, exposure values, and target metadata.

## Stage 2 — First light curve

Estimated time: 2–3 hours

1. Load the TRES-1 session from 2026-08-06.
2. Build a master dark frame.
3. Dark-correct the science frames.
4. Align the images.
5. Detect suitable stars.
6. Select the target and comparison-star ensemble.
7. Perform aperture photometry.
8. Calculate normalized differential flux.
9. Plot the first light curve.
10. Save the results to a compact CSV or Parquet file.

## Stage 3 — Quality control

Estimated time: approximately 1 hour

1. Calculate uncertainty and signal-to-noise measurements.
2. Measure background and position drift.
3. Identify saturated or abnormal frames.
4. Reject poor frames using clear, documented rules.
5. Show the curve before and after quality filtering.

## Stage 4 — Streamlit dashboard

Estimated time: approximately 2 hours

1. Create the four dashboard pages.
2. Load precomputed results for fast demonstrations.
3. Add interactive Plotly charts.
4. Add explanations beside scientific outputs.
5. Add caching so FITS files are not repeatedly processed.

## Stage 5 — Additional sessions and presentation

Estimated time: 1–2 hours

1. Run the proven pipeline on a few strong additional sessions.
2. Compare their quality and possible signals.
3. Document the scientific question and methodology.
4. Document validation and limitations.
5. Prepare a short live demonstration.
6. Prepare backup screenshots in case the live demo fails.

---

# What not to do first

Do not begin with:

- A neural network
- A large machine-learning classifier
- Processing all targets simultaneously
- A complicated candidate-ranking formula
- Website styling and animation
- An AI chatbot
- Claims of planet discovery

These features do not matter if the photometry is scientifically unreliable.

The correct order is:

```text
Trustworthy data result
        ↓
Scientific validation
        ↓
Interactive dashboard
        ↓
Candidate comparison
        ↓
Presentation polish
```

---

# Final decision

We should build the **Exoplanet Discovery Dashboard**, but the immediate task is the single-session TRES-1 photometry pipeline.

The first concrete milestone is:

> Load, calibrate, align, and measure the 91 TRES-1 images from 2026-08-06, then produce a normalized differential light curve with quality metrics.

Once that result is trustworthy, we can confidently build the website around it.
