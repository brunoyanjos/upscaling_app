# AGENTS.md

## Purpose

This file defines the working conventions for coding agents operating in this repository.

Read `README.md` and `docs/PROJECT_CONTEXT.md` before making structural changes. For GUI work also read `docs/UI_DESIGN_GUIDELINES.md`, `docs/MILESTONE_06_SSDI_FIELD_SCALE_UPSCALING.md`, and `docs/SSDI_GUI_REFACTORING_PLAN.md`. For resumption after the October 2026 pause, read `docs/CHECKPOINT_2026-10-19_SSDI_GUI_MVP.md`.

## Project Structure

The Python package is located under:

```text
src/upscaling_app/
```

Main areas:

```text
database/        raw-data normalization and database construction
upscaling/       physical models and modelling pipelines
analysis/        statistical analysis and diagnostics
models/          shared domain/data models
gui/             PySide6 presentation (SSDI prototype)
cli.py           command-line entry point
paths.py         project paths
```

Avoid adding new numbered or one-off scripts when the functionality belongs in the package.

## Execution

Install the project in editable mode:

```bash
pip install -e .
```

Main CLI entry point:

```bash
upscaling
```

Database reconstruction:

```bash
upscaling database build
```

Stable distribution workflows:

```bash
upscaling distributions fit
upscaling analyze distributions
```

## Database Rules

Raw spreadsheets must be parsed only in the database layer.

Modelling pipelines must consume normalized databases rather than raw spreadsheets directly.

Current normalized databases:

```text
oil_properties.xlsx
experiments.xlsx
distributions.xlsx
```

Relationships:

```text
oil_properties
      1
      │
      N
experiments
      1
      │
      N
distributions
```

`experiment_id` must remain deterministic across database rebuilds.

Use the shared experiment-ID generator. Do not introduce random UUID4 identifiers for experimental records.

## Units

Use SI units internally whenever applicable.

```text
density              kg/m³
dynamic viscosity    Pa·s
diameter             m
volumetric flow       m³/s
interfacial tension  N/m
fractions             dimensionless
```

Perform source-unit conversion during database construction.

## Scientific Code

Keep these responsibilities separate:

```text
data ingestion
physical equations
optimization / fitting
prediction
statistical analysis
result persistence
reporting
plotting
```

Do not modify a physical equation or correlation merely to improve numerical agreement.

Any change to a physical formulation or stable scientific convention must be explicit and justified.

## Distribution Workflow

The stable Rosin–Rammler reference is the direct CDF fit evaluated at the original experimental `droplet_diameter` coordinates.

Stable fitting contract:

```text
droplet_diameter + volume_fraction
        ↓
empirical CDF
        ↓
direct Rosin–Rammler fit
        ↓
experiment_id + shape + scale
```

Do not silently reintroduce:

```text
upper-edge coordinates for CDF fitting
moment-based fitting in the production workflow
alternative continuous reconstructions
```

Those belong to research diagnostics unless a new validated decision explicitly replaces the current baseline.

For fit analysis:

- compare the fitted CDF against the empirical CDF at original diameters;
- use distribution-reconstructed `D50` as the primary fitted-D50 reference;
- retain reported `measured_d50` as a secondary source-consistency diagnostic;
- do not overwrite the normalized experiment database to force agreement between the two D50 sources.

## JAX

JAX-specific logic should remain inside the scientific implementation layer, not in the CLI.

Prefer vectorized and differentiable formulations when appropriate.

Numerical precision choices must be explicit for scientific calculations.

## SSDI desktop GUI contract

- The GUI is a presentation and orchestration layer, not a second implementation of SSDI equations, optimization, calibration, or database normalization.
- Reuse `upscaling.ssdi.prediction` for single-scenario D50 and `upscaling.ssdi.model_catalog` for **persisted** model coefficients. Do not hard-code coefficients in widgets.
- A `jax_oil_wise` calibration requires a registered oil with matching persisted coefficients; `Custom oil` is not oil-wise eligible. Preserve explicit `model_version`, `oil_id`, and coefficient provenance.
- UI input units differ from SI; convert at the presentation/service boundary, never inside the existing physical equations.
- UI scalar inference currently forces the JAX **CPU** backend before JAX-related imports. Do not apply the same restriction globally to scientific CLI workflows.
- Qt widgets must be touched only on the main GUI thread. Use signals to return numerical results from a worker. Do not allow stale worker output to replace results if inputs, calibration, oil, or text-scale generation changed.
- Before deleting/rebuilding Qt widgets, handle active worker ownership and signal connections. Protect closing/re-rendering against deleted C++ objects; use `shiboken6.isValid` where lifecycle may be uncertain.
- Keep the stable `python -m upscaling_app.gui.ssdi_window` launch route working during incremental refactoring.
- The current window is a **technical-debt prototype** (~1,900 lines). Follow `docs/SSDI_GUI_REFACTORING_PLAN.md` for extraction in small, behaviour-preserving steps; do not introduce new scientific models as part of UI cleanup.

## Configuration

Dataset selection, model settings, optimizer settings, and analysis options should move toward configuration files rather than hard-coded constants.

Do not duplicate experimental selections across pipelines when the same configuration can be reused.

## Statistical Analysis

Distinguish clearly between:

- calibration / fit error;
- predictive validation;
- outlier sensitivity;
- numerical error;
- experimental variability;
- source-consistency diagnostics.

Do not interpret improved fit after removing observations as independent predictive improvement unless validation supports that conclusion.

## Code Style

Prefer:

- small functions with clear responsibilities;
- explicit names;
- type annotations where useful;
- minimal comments;
- comments only where intent, assumptions, units, or non-obvious logic need clarification.

Avoid redundant comments that restate the code.

## Current Project Stage

Completed and stabilized blocks:

```text
Milestone 1 — Data Architecture and CLI Foundation
Milestone 2 — SSDI Pipeline Reconstruction
Milestone 3 — SSMD Pipeline Reconstruction
Milestone 4 — Droplet-Size Distribution Analysis
Milestone 5 — Experimental Analysis architecture
```

Before structural changes, consult the corresponding milestone and research documents.

Milestone 6 — SSDI Field-Scale Upscaling has a D50-only desktop GUI prototype, **not a scientifically validated field-scale predictor**. Part 2 (complete distributions, shape `k` and scale `lambda`) is research still to do. Before extending distributions, capture a fresh runnable GUI source snapshot, fix/test the asynchronous worker lifecycle and record known input/model assumptions. Preserve the stable Milestone 4 distribution-fitting baseline; explore shape transfer separately.
