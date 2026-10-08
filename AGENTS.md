# AGENTS.md

## Purpose

This file defines the working conventions for coding agents operating in this repository.

Read `README.md` and `docs/PROJECT_CONTEXT.md` before making structural changes.

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

The next distribution research questions concern normalized shape behaviour and possible prediction of the Rosin–Rammler shape parameter `k`. These remain exploratory and must stay separate from the stable distribution fitting workflow.
