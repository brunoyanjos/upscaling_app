# Checkpoint — SSDI D50 Desktop Prototype (2026-10-19)

**Purpose:** Preserve what is working, what has **not** been verified, and the exact steps to resume the Upscaling App after a development pause. This is a handoff note, not a replacement for the milestone or a claim of scientific scale-up validation.

## Quick status

- Milestones 1–4: completed. Milestone 5: closed for its current experimental-analysis scope.
- Milestone 6 / Part 1: field-scale D50 numerical prediction and first illustrative scenarios exist, but independent scientific applicability and benchmark closure remain open.
- Milestone 6 / Part 3: PySide6 D50 desktop prototype assembled and reported working by the developer. Interface-level MVP, not production-ready.
- Milestone 6 / Part 2: **distribution upscaling remains open**; no complete-distribution prediction is delivered by the GUI.
- Current scientific source of truth: normalized project databases and persisted SSDI coefficients. Do not change model equations to adjust GUI results.

## Operational workflow and source boundaries

```text
raw oil assays / raw experimental spreadsheets
  -> database layer (only parser of raw sources)
  -> oil_properties.xlsx / experiments.xlsx / distributions.xlsx
  -> SSDI persisted calibration results (predictions.xlsx)

GUI: src/upscaling_app/gui/ssdi_window.py
  -> IO data loading (registered oil data / IFT references)
  -> upscaling.ssdi.model_catalog (persisted global and oil-wise A,B)
  -> screen fields -> SI scenario -> prediction.predict_field_ssdi
  -> derived_properties.add_ssdi_physics -> model.calculate_d_pred (JAX)
  -> result view: D50, D50/D, Re, We, Ca, coefficients and caution
```

The GUI process sets `JAX_PLATFORMS=cpu` before importing modules that use JAX, because JAX GPU startup attempted ~6 GiB VRAM allocation and generated CUDA OOM for scalar inference. This is deliberate **for the GUI only**.

### Supported GUI features

- Registered oil or manually defined `Custom oil`; select/search in-page.
- Registered-oil density populated; stabilized-oil viscosity estimates at 20/40/50 °C and interpolation for 20–50 °C when explicitly requested. Estimated dynamic viscosity uses reference density at 15 °C; it is **not** a PVT/live-oil model.
- Interfacial-tension reference selection: untreated, Corexit 9500A, Finasol IBC where supported by normalized records; source-discrepant oils must remain restricted from unsupported automatic reference use (recent work flags 3015 and 4666).
- Four model modes: SINTEF reference; global 10 oils; retained 7 oils (3016, 4662, 4665 excluded); known-registered-oil-only oil-wise. Oil-wise A,B must be joined via `experiment_id` to `oil_id`, and not transferred to an unknown oil.
- Input fields with explicit user units; internally SI. Prediction result with hero D50, ratio D50/D, Re, We, Ca, coefficients and warning for 470 mm vs lab 2–3 mm nozzles.
- 100/125/150% text sizing, collapsed/available property assistant, animated oil selection and result scrolling, async worker/button label `Calculating…`.

## Reference regression scenario — not external validation

| Input / output | Value |
|---|---|
| Oil | 3016 (Campos Heavy Standard) |
| Selected model | `jax_baseline_all` |
| Nozzle diameter | 470 mm |
| Oil volumetric flow | 12,000 m³/day |
| Local volumetric GOR | 0.9 m³/m³ |
| Gas density | 1.58 kg/m³ (assumed) |
| Oil density | 937 kg/m³ |
| Oil dynamic viscosity | 5 mPa·s |
| IFT | 1.4 mN/m |
| Reference D50 | ~2.0030 mm |
| Reference dimensionless groups | Re ~2.33e5, We ~2.21e6, Ca ~9.46 |

This is a consistency check against a historical calculation under the listed assumptions, **not** evidence that a 470 mm field release has been validated. Actual deep-water gas density, GOR, IFT and live-oil viscosity require scenario-specific justification. Retained-7-oil calibrations must not be interpreted as automatically validated for excluded oils.

## Files and execution

Repository structure (planned / current package paths):

```text
README.md
AGENTS.md
docs/PROJECT_CONTEXT.md
docs/MILESTONE_06_SSDI_FIELD_SCALE_UPSCALING.md
docs/DISTRIBUTIONS_RESEARCH_GOALS_UPDATED.md
docs/UI_DESIGN_GUIDELINES.md
docs/SSDI_GUI_REFACTORING_PLAN.md
docs/CHECKPOINT_2026-10-19_SSDI_GUI_MVP.md
src/upscaling_app/gui/ssdi_window.py
src/upscaling_app/gui/theme.py
src/upscaling_app/upscaling/ssdi/model_catalog.py
src/upscaling_app/upscaling/ssdi/prediction.py
src/upscaling_app/upscaling/ssdi/physics/derived_properties.py
src/upscaling_app/upscaling/ssdi/physics/model.py
```

```bash
# Repository root; use existing project environment
python -m py_compile src/upscaling_app/gui/ssdi_window.py
python -m upscaling_app.gui.ssdi_window

# JAX CUDA fallback for local diagnosis only, if CPU flag is not in GUI:
JAX_PLATFORMS=cpu python -m upscaling_app.gui.ssdi_window

# Distribution baseline (separate from exploratory distribution transfer)
upscaling distributions fit
upscaling analyze distributions
```

Do not use uploaded `ssdi_window(4).py` as a drop-in runnable code baseline. The last shared snapshot had `def _predict_d50` at module level, while its signal callback referred to it as a class method; the developer subsequently corrected this locally. Obtain the **current repository files** before making additional code edits. Likewise `model_catalog.py` and `prediction.py` in the provided attachments may be older than the running local code.

## Technical risks / debt to resolve before new GUI features

1. **Async worker lifecycle:** If input/selection changes while a worker computes, old results may be displayed. `change_text_scale` rebuilds Qt widgets and can invalidate pointers referred to by the callback. Closing with a running `QThread` can be unsafe. Introduce request IDs or immutable scenario snapshots, input-signature checks, safe worker teardown, and controlled re-render behaviour.
2. **Qt object lifetime:** Old animated `QPropertyAnimation` wrappers can outlive their C++ objects; use explicit ownership, `isValid` where necessary, and avoid `deleteLater`/callback race patterns.
3. **Prediction result correctness:** Verify D50 and dimensionless groups against persisted lab test cases; verify solver residual/positivity and zero-gas physics. A reference UI screenshot is not a regression test.
4. **Property provenance:** The IFT value is treatment-specific and experimental (often at 50 °C), not necessarily the true field-condition value; avoid automatic inference. Verify manual-text-edited IFT state tracking (it was attached to the wrong fields loop in one inspected snapshot).
5. **Physical applicability:** The UI currently warns by nozzle diameter, not all relevant Reynolds/Weber/Capillary/GOR/oil-property combinations.
6. **Monolith:** The Qt window source approaches 1,900 lines and mixes widget construction, input collection, state handling, animation, validation and threading. Separate incrementally after tests, preserving current visual output.
7. **Persistence/export:** Structured saved scenarios/results and provenance are not implemented/confirmed as part of the GUI.

## Resume order (recommended)

1. **Freeze a reproducible baseline:** Commit or tag the latest corrected code and document environment/dependency versions. Compare with these docs; don't overwrite local changes with earlier uploaded snapshots.
2. **Verify the GUI:** Launch; test custom/registered oil, four model modes, viscosity and IFT assistants, 100/125/150% scaling, normal/invalid/zero-gas scenarios, loading and prediction. Check this reference scenario and selected laboratory examples.
3. **Close async edge cases:** Change an input, oil, calibration and scale while calculating; try closing window mid-calculation. Prevent stale results, Qt object deletion and `QThread: Destroyed while thread is still running`.
4. **Refactor the GUI conservatively:** Follow `SSDI_GUI_REFACTORING_PLAN.md`; one extraction per commit with smoke tests. Do not combine the refactor with physics or calibration changes.
5. **Resume distribution science:** Read Milestone 4, `DISTRIBUTIONS_RESEARCH_GOALS_UPDATED.md`, and Milestone 6 Part 2. Start with distribution-reconstructed D50 normalization and empirical CDF shape collapse; only afterward examine `k`, `lambda`, regimes/oil effects and grouped predictive transfer.

## Research boundary for distributions

- Baseline is a **direct Rosin–Rammler CDF fit at original** measured `droplet_diameter` values, with `shape=k`, `scale=lambda`, linked via deterministic `experiment_id`.
- Treat reported `measured_d50` and distribution-reconstructed D50 as distinct; the latter is the reference for evaluating the fit of the measured distribution. Do not modify reported values in the database.
- Evaluate `d/D50` normalized curves, `D10/D50`, `D90/D50`, span and deviations by oil/treatment/regime before proposing correlations.
- If reconstructing a full Rosin–Rammler CDF from predicted D50 and shape k, use `lambda = D50 / (ln 2)^(1/k)`, enforce k>0 and λ>0 and maintain median consistency.
- Separate in-sample fit from held-out oil-level predictive validation. No automatic distribution prediction should be added to the GUI before a research decision supports it.

## Handoff statement

The D50 UI prototype is a sound feature checkpoint for further research, but **not** a completed Milestone 6 scientific validation and **not** a released application. This document records present evidence and open risks without assuming local code was rerun or audited in this checkpoint.
