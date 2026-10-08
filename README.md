# Upscaling App

Scientific Python application for oil-dispersion modelling, parameter estimation, prediction, and statistical analysis.

The project currently covers:

- normalized experimental databases;
- SSDI modelling and predictive validation;
- SSMD modelling and predictive validation;
- experimental-data analysis;
- droplet-size distribution fitting and fit-quality analysis;
- JAX-based parameter estimation where applicable.

## Project structure

```text
upscaling_app/
├── configs/
├── data/
│   ├── raw/
│   ├── database/
│   └── results/
├── docs/
├── src/
│   └── upscaling_app/
│       ├── analysis/
│       │   ├── experimental/
│       │   ├── ssdi/
│       │   ├── ssmd/
│       │   └── distributions/
│       ├── database/
│       ├── upscaling/
│       │   ├── ssdi/
│       │   ├── ssmd/
│       │   └── distributions/
│       ├── cli.py
│       └── paths.py
├── pyproject.toml
└── README.md
```

## Installation

Install the package in editable mode:

```bash
pip install -e .
```

The project-wide CLI entry point is:

```bash
upscaling
```

## Architecture

Raw experimental spreadsheets are processed only by the database layer.

Scientific workflows consume normalized databases:

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

Current normalized databases:

```text
data/database/
├── oil_properties.xlsx
├── experiments.xlsx
└── distributions.xlsx
```

`experiment_id` is deterministic and links experimental conditions to measured droplet-size distributions.

## Core design rules

1. Raw spreadsheets are parsed only in the database layer.
2. Modelling pipelines consume normalized databases.
3. Internal physical units use SI whenever applicable.
4. `experiment_id` remains deterministic across database rebuilds.
5. Data ingestion, physics, calibration, prediction, persistence, and statistical analysis remain separated.
6. Exploratory correlation development must not silently replace validated production references.
7. Reusable scientific logic belongs under `src/upscaling_app/`.

## Units

Processed databases use SI units whenever applicable.

```text
density              kg/m³
dynamic viscosity    Pa·s
diameter             m
volumetric flow      m³/s
interfacial tension  N/m
fractions             dimensionless
```

## Current workflows

The CLI is the application entry point for database, modelling, and analysis workflows.

Core examples include:

```bash
upscaling database build
upscaling distributions fit
upscaling analyze distributions
upscaling analyze experimental summary
upscaling analyze experimental treatment-effect
upscaling analyze experimental ssdi
upscaling analyze experimental ssmd
```

SSDI and SSMD expose their modelling, performance, sensitivity, oil-wise, and predictive-validation workflows through the project CLI according to their milestone documentation.

## Development status

### Milestone 1 — Data Architecture and CLI Foundation

**Status: Completed**

Established the src-layout package, normalized database architecture, deterministic identifiers, SI normalization, and project-wide CLI foundation.

### Milestone 2 — SSDI Pipeline Reconstruction

**Status: Completed**

The SSDI workflow separates:

```text
data selection
physics
calibration
prediction
persistence
statistical analysis
sensitivity analysis
predictive validation
```

The physical formulation remains distinct from diagnostic and predictive-validation workflows.

### Milestone 3 — SSMD Pipeline Reconstruction

**Status: Completed**

The SSMD workflow includes:

- reconstructed SINTEF Equation 5 and Equation 6 references;
- explicit model variants;
- global and oil-wise diagnostics;
- experiment-level persistence;
- separated experimental and model-analysis workflows;
- leave-one-oil-out predictive validation.

The current global `c,d` model remains an upscaling-oriented simplification rather than a universal full-scale closure.

### Milestone 4 — Droplet-Size Distribution Analysis

**Status: Completed**

The stable distribution workflow is:

```text
normalized distributions
        ↓
empirical CDF at original droplet diameters
        ↓
direct Rosin–Rammler CDF fit
        ↓
shape + scale persistence
        ↓
fit-quality and D50 analysis
```

The production fit uses the original `droplet_diameter` coordinates. The alternative upper-edge representation and moment-based estimator were evaluated during research and are not part of the stable fitting workflow.

Persisted distribution parameters are:

```text
experiment_id
shape
scale
```

The principal analysis reference for fitted median diameter is the `D50` reconstructed from the measured distribution. Reported `measured_d50` remains a secondary source-consistency diagnostic and is not overwritten.

### Milestone 5 — Experimental Analysis

**Status: Closed for the current project stage**

The experimental-analysis layer provides dataset coverage, treatment-effect analysis, SSDI-specific diagnostics, and SSMD-specific diagnostics without modifying production model equations.

## Current research boundary

The stable distribution fitting problem is considered closed. Open distribution research remains separate and includes:

```text
shape collapse after D50 normalization
shape-parameter k behaviour
candidate physical predictors for k
distribution-family benchmarking
oil-property dependence
scale and gas transfer
field-scale distribution reconstruction
```

These topics are documented in `DISTRIBUTIONS_RESEARCH_GOALS_UPDATED.md` and should not modify the stable Rosin–Rammler fitting workflow without explicit scientific justification and validation.
