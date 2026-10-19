# SSDI Desktop GUI — Incremental Refactoring Plan

**Status:** Proposed technical-debt reduction, **not yet implemented**. **Date:** 2026-10-19.

## Why refactor?

The SSDI desktop prototype lives primarily in `src/upscaling_app/gui/ssdi_window.py` (~1,900 lines in the shared snapshot). The same class builds widgets, manages oil/model selection and text scaling, parses/converts input units, starts asynchronous workers, renders scientific results, and animates scrolling. This became useful for rapid prototyping, but creates risks of regressions and stale Qt references. **Do not rewrite the application from scratch.**

## Contracts to preserve

- CLI and scientific modules remain the data/physics/calibration/optimization/prediction source of truth. The GUI is not allowed to parse raw experimental spreadsheets or re-fit A,B.
- Preserve executable module `python -m upscaling_app.gui.ssdi_window` and current PySide6 user experience: oil selector, properties/assistant, calibration buttons, condition inputs, D50 results, extrapolation notice, 100/125/150% scaling.
- Preserve normalized `experiment_id`, `oil_id` mapping, model IDs and persisted coefficient provenance. Oil-wise unavailable for `Custom oil`.
- Preserve SI internally and label/convert the boundary units (mm, m³/day, mPa·s, mN/m).
- Preserve reference numerical fingerprints and scientific model functions, without changing the physics to facilitate a refactor.
- Keep GUI JAX CPU selection local to the GUI process; don't override scientific CLI GPU policy.

## Proposed layout (target, not immediate migration)

```text
src/upscaling_app/gui/
    theme.py                     # shared typography, colours and layout tokens
    ssdi_window.py               # small compatibility entry point; main() remains
    ssdi/
        window.py                # SSDIWindow root composition and persistent UI state
        panels.py                # oil, calibration, conditions and result panel builders
        oil_selector.py          # oil picker behaviour / filtering only, optional extraction
        scenario.py              # pure form-to-SI conversion and validation (no Qt imports)
        prediction_worker.py     # QThread + result signal protocol, no physical equations
```

**This is a target boundary map, not a requirement to create all files.** If `panels.py` becomes too large, split by panel after the first extraction. Consider a controller/service only if a real interface boundary emerges; avoid a framework rewrite or premature generic widgets.

## Staged extraction (one behaviour-preserving commit per stage)

| Stage | Change | Verification / exit |
| --- | --- | --- |
| 0 — Baseline | Capture corrected **local** `ssdi_window.py`, updated `model_catalog.py`, `prediction.py`, `theme.py`; commit and record smoke/regression scenario. | App launches and reproduces D50 fingerprint. |
| 1 — Worker safety | First fix stale result/selection/scale close hazards; use request identity and current-state checks on completion; prevent re-render/close from destroying active worker-owned dependencies. | Inputs/model/oil/text scale altered during calculation never show stale output or crash. |
| 2 — Scenario boundary | Extract pure `parse_and_normalize` logic that converts form strings + model/oil IDs into explicit SI input structure; error messages remain UI-level. | Existing valid/invalid/zero-gas tests pass without requiring QApplication for validation tests. |
| 3 — Prediction worker | Move worker class to `gui/ssdi/prediction_worker.py`; only call the existing scientific prediction entry point. | Button loading and results identical; signals connected exactly once. |
| 4 — Presentational panels | Extract result panel first (`D50`, dimensionless metrics, warning), then calibration and oil/property panels. Keep ownership/state/interaction on window until safe to move. | Visual parity in 100%, 125%, 150%; oil-wise gating and assistant behaviour unchanged. |
| 5 — Window composition | Keep root composition and UI state in `gui/ssdi/window.py`; preserve thin `gui/ssdi_window.py` forwarding wrapper and entry point. | Existing command still works; no circular imports. |
| 6 — Optional polish | Build a minimal suite of UI smoke tests, improve keyboard/focus/animations and document source provenance/tooltips. | Changes no longer require editing one ~1,900-line window. |

## Worker-lifecycle policy (establish before extracting)

The user can edit the scenario, select an oil/model and switch text scale while computation is ongoing. A worker emits results **later**, so the UI must not assume that its original widgets or context are current.

Suggested non-intrusive strategy:

1. Snapshot immutable normalized scenario, model ID, oil ID, coefficients and UI generation (or input revision) before starting.
2. Increment a revision when a meaningful scenario/model/oil property changes. Compare result's request ID/revision to current state before displaying it. Discard stale completion silently or show a nonblocking note; never overwrite newer inputs.
3. Prevent conflicting concurrent requests, then re-enable the button on completion. Ensure the `finished` signal and teardown cannot access deleted widget instances after a scale rebuild.
4. During text-scale re-render or close, choose and document a single supported policy: defer rebuilding/closing until worker finishes, or safely disconnect and wait for the worker to finish. Prefer simpler **defer/disable** behaviour for the MVP; avoid force-terminating JAX threads.
5. A worker owns computation data, not Qt widgets. Only the GUI thread updates labels, focus and scrolling. Be careful with Python references whose underlying C++ instance was destroyed.

No artificial loading timer is needed. Button text `Calculating…` is sufficient; the actual computation ends when the worker emits `completed` or `failed`.

## Minimal test matrix for each refactor stage

**Baseline numerical:** field reference 3016 with global model and expected D50 about 2.0030 mm (under documented assumptions); two selected persisted laboratory cases with known model `D50`; finite positive result and solver convergence check. Do not conflate the field fingerprint with external validation.

**Input validation:** missing IFT/viscosity, invalid/negative values, GOR=0 without gas density, GOR>0 requiring gas density, unsupported oil-wise ID, oil-wise B allowed to be negative when empirically calibrated. **Check first:** current code's scientific solver and input policy may exclude some zero-gas states; do not add unverified claims that they are already supported.

**Qt:** opening/closing selector repeatedly; custom vs registered oil, change oil while oil-wise active, treatment choice, manual IFT edit, optional assistant, 100/125/150% scale, repeated Predict, changing inputs while computing, closing while computing, finish after scale change, focus and smooth scroll.

**Scientific separation:** tests that GUI startup reads persisted results rather than refitting; no raw datasheet parsing in modelling/UI; no data mutation during prediction; stable model/ID mapping.

## Explicitly out of scope

- Rewriting SSDI physics or JAX solver.
- Changing normalized databases, experiment IDs, or fit conventions.
- Adding distribution prediction as a side effect of GUI refactoring.
- Introducing plugins, web services, new database technologies, or a large state-management framework.

## Definition of done

- Each panel and worker have a focused responsibility; scientific prediction and database loading remain outside Qt views.
- The original launch command remains stable.
- No stale predictions or Qt-lifecycle crashes across scaling, editing or close.
- Reference and lab regression tests pass; interface labels, units and coefficient provenance are unchanged.
- Milestone 6 and checkpoint updated with actual test evidence before declaring the refactor completed.
