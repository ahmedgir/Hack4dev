# Codex project memory

Read `START_HERE_NEXT_DEVICE.md` before changing this repository. It is the canonical handoff from the original development chat.

## Working rules

- Speak Arabic with Hussein unless he asks otherwise; explain astronomy plainly and correct misconceptions directly.
- Preserve scientific honesty. The planet is not visible in FITS images; the marked object is the host star.
- Never describe a visually plausible curve as a confirmed transit. Respect `scientific_status`, coverage, precision, depth, duration, and timing checks.
- Treat the two CoRoT-2 sessions as promising preliminary recoveries of a known transit, not a new discovery or independent confirmation.
- Qatar-1 is `transit_like_but_parameters_inconsistent`; do not promote it to a success without new evidence.
- ASTAP is installed on the original Windows PC but solved 0/18 uncached sessions. Do not claim it works for this dataset merely because it is installed.
- Raw FITS files are intentionally excluded from Git. Restore them with `python scripts/restore_dataset.py`; the website should consume the committed compact outputs instead.
- Every website Timeline must include accepted and rejected frames. Use `web_timeline.json` and show `rejection_reason`.
- Before changing scientific thresholds, preserve the current result, explain the reason, and rerun the cached regression set.
- Preserve user work and unrelated changes. Never commit secrets, tokens, raw FITS, generated `timeline_frames`, or local ASTAP scratch files.

## Verification commands

```powershell
conda activate exoplanet-poc
python scripts/audit_dataset.py
python scripts/build_completeness_report.py
.\run_poc.ps1 --cached-only
```

Expected current checkpoint: 1,741 FITS audited when raw data is present, 22 sessions inventoried, 7 sessions pipeline-complete, and 558 science frames represented in photometry/Timeline outputs.
