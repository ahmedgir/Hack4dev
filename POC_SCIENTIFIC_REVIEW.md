# POC Scientific Review

Last updated: 2026-09-15

## Verdict

The POC successfully demonstrates a reproducible path from raw FITS images to an explainable Discovery Webapp artifact. The initial three WASP sessions were insufficient, while a deliberately selected CoRoT-2 session now shows a promising recovery of a known transit. It is not yet an independent confirmation.

That distinction is a strength if presented honestly: the product can teach users how astronomical evidence is built, why frames fail, and why a plausible-looking curve is not automatically a detection.

## Results

| Session | Accepted | Pre / in / post | Residual scatter | Published depth | Verdict |
|---|---:|---:|---:|---:|---|
| WASP-10, 2026-08-08 | 31 / 86 | 4 / 27 / 0 | 4.276% | 2.525% | Insufficient coverage and precision |
| WASP-2, 2026-08-11 | 22 / 78 | 0 / 22 / 0 | 0.855% | 1.646% | Cleaner, but no baseline outside transit |
| WASP-2, 2026-08-24 | 40 / 77 | 0 / 9 / 31 | 9.468% | 1.646% | Post-transit coverage, but excessive scatter |
| CoRoT-2, 2026-08-09 | 73 / 87 | 11 / 45 / 17 | 1.690% | 2.750% | Promising preliminary recovery; validate independently |

The fitted depths in `summary.json` are retained for pipeline diagnosis but are marked `fit_valid: false` and `diagnostic_only_do_not_claim_transit`.

## What a judge can verify

- The selected reference field has an Astrometry.net WCS solution.
- The yellow target marker comes from the catalogue sky coordinate transformed into image pixels.
- The blue comparison markers come from Gaia and are used to remove brightness changes shared by the whole field.
- The target and comparison apertures follow the measured field drift across frames.
- Rejected frames are visible in the output and their quality metrics remain in the CSV.
- Expected transit timing uses BJD_TDB rather than filename order or local clock time.
- Compact JSON artifacts are separate from the raw FITS data, which is appropriate for a web frontend.

## What an astronomer should challenge

1. Only two dark frames are available for these dates, and no flats or bias frames were identified.
2. The current aperture radius, annulus, centroid search, and comparison-star selection are transparent defaults, not optimized per target.
3. The comparison ensemble is selected from a single reference frame; variable or colour-mismatched comparison stars are not yet excluded by a full stability analysis.
4. Weather/background changes and target loss remove large parts of each sequence.
5. None of the sessions has adequate accepted measurements before, during, and after the predicted transit.
6. The simple trapezoid is a diagnostic overlay, not a physical limb-darkened transit model.
7. EXOTIC has not yet independently reproduced a candidate result.

## Product implication

The first public experience should not say “we found the planet.” It should say:

> We followed the light of a known host star through real telescope frames. Here is which data survived, what the expected transit would look like, and why this session is or is not strong enough to support a conclusion.

The UI should progressively expose four layers:

1. **See:** the host star and a moving-frame slider.
2. **Measure:** the synchronized light-curve point.
3. **Question:** accepted/rejected frames and plain-language reasons.
4. **Verify:** coordinates, comparison stars, timing, metrics, and downloadable data.

## Reproduction

Run all cached POC sessions:

```powershell
.\run_poc.ps1 --cached-only
```

Open the executed notebook:

```text
notebooks\01_transit_pipeline_poc.ipynb
```

The next scientific phase is to score the remaining sessions for baseline coverage and precision, then validate only the best candidate with EXOTIC.
