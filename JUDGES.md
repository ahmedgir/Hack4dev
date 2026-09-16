# Judge quick review

## What we built

An evidence-first discovery tool that connects real MicroObservatory FITS frames to an inspectable light curve. It marks the **host star**, keeps every accepted and rejected frame, and explains why a session does or does not support recovery of a known transit.

## Three-minute route

1. Start at the homepage and open **CoRoT-2 b**.
2. Switch between its two nights and move the timeline through accepted and rejected frames.
3. Open **Qatar-1 b** to see a transit-like curve rejected because its fitted parameters disagree with published values.
4. Open **TrES-5 b** and **HAT-P-10 b** to see complete processing with, respectively, excessive scatter and missing pre-transit baseline.
5. Open Methodology and Sources to inspect the pipeline and provenance.

## Reproducibility

```powershell
conda env create -f environment.yml
conda activate exoplanet-poc
python scripts/restore_dataset.py
python scripts/audit_dataset.py
.\run_poc.ps1 --cached-only

cd webapp/frontend
pnpm install
pnpm validate:data
pnpm typecheck
pnpm build
```

The raw FITS archive is excluded from Git because it is about 1.1 GB; its source URLs and hashes are committed. Compact CSV, JSON, WCS, and figures needed to review the results are committed.

## Evidence boundary

- CoRoT-2 is a promising preliminary recovery of a known transit in two nights, cross-checked with EXOTIC on the same observations.
- Qatar-1 remains `transit_like_but_parameters_inconsistent`.
- Every other reviewed result is `insufficient_for_transit_claim`.
- TrES-1 remains awaiting analysis because its 91 frames contain too few usable stars for a verified coordinate solution.
- The planet is not visible in the FITS images; the marker identifies its host star.

## Submission items outside this repository

- Public Vercel URL
- Short demo video and presentation deck
- Final Hack4Dev form fields, team details, and challenge selection
