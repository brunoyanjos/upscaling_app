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
diameter              m
volumetric flow       m³/s
interfacial tension   N/m
fractions             dimensionless
```

Perform source-unit conversion during database construction.

## Scientific Code

Keep these responsibilities separate:

```text
data ingestion
physical equations
optimization
prediction
statistical analysis
result persistence
```

Do not modify a physical equation or correlation merely to improve numerical agreement.

Any change to the physical formulation must be explicit and justified.

## JAX

JAX-specific logic should remain inside the scientific implementation layer, not in the CLI.

Prefer vectorized and differentiable formulations when appropriate.

Numerical precision choices must be explicit for scientific calculations.

## Configuration

Dataset selection, model settings, optimizer settings, and analysis options should move toward configuration files rather than hard-coded constants.

Do not duplicate experimental selections across pipelines when the same configuration can be reused.

## Statistical Analysis

Distinguish clearly between:

- calibration error;
- predictive validation;
- outlier sensitivity;
- numerical error;
- experimental variability.

Do not interpret improved fit after removing outliers as independent predictive improvement unless validation supports that conclusion.

## Code Style

Prefer:

- small functions with clear responsibilities;
- explicit names;
- type annotations where useful;
- minimal comments;
- comments only where intent, assumptions, units, or non-obvious logic need clarification.

Avoid redundant comments that restate the code.

## Current Milestone

Milestone 1 is the data architecture and CLI foundation.

The next milestone is reconstruction of the SSDI pipeline using the normalized databases.

The SSDI work should preserve the validated physical formulation while removing hard-coded dataset selection and separating data, physics, optimization, prediction, metrics, and analysis.
