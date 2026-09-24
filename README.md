# Upscaling App

Scientific Python application for oil-dispersion modelling, parameter estimation, prediction, and statistical analysis.

The project currently covers:

- normalized experimental databases;
- SSDI modelling and validation;
- SSMD modelling and evaluation;
- experimental-data analysis;
- droplet-size distribution data and upcoming distribution modelling;
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
│       │   └── ssmd/
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

`experiment_id` is deterministic and provides the relationship between experimental conditions and measured droplet-size distributions.

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

Examples:

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

Examples currently used in the project include:

```bash
upscaling database build
upscaling analyze experimental descriptive
upscaling analyze experimental ssdi
upscaling analyze experimental ssmd
upscaling analyze experimental treatment-effect
upscaling analyze ssmd
```

Production SSDI and SSMD workflows are also exposed through the project CLI according to the current implementation.

## Development status

### Milestone 1 — Data Architecture and CLI Foundation

**Status: Completed**

Completed work includes:

- `src/` package architecture;
- normalized database builders;
- deterministic experiment identifiers;
- SI normalization;
- project-wide CLI foundation.

### Milestone 2 — SSDI Pipeline Reconstruction

**Status: Completed**

The SSDI workflow now separates:

```text
data selection
physics
calibration
prediction
persistence
statistical analysis
predictive validation
```

The reconstructed SSDI reference and recalibrated models are evaluated independently from the calibration workflow.

### Milestone 3 — SSMD Pipeline Reconstruction

**Status: In progress — finalization stage**

Current SSMD capabilities include:

- normalized 90-experiment / 10-oil calibration dataset;
- untreated-release and water-jet derived physics;
- reconstructed SINTEF Equation 5 and Equation 6;
- explicit model versions;
- by-regime and global `c,d` regression;
- persisted experiment-level predictions;
- SSMD reporting;
- separate experimental and model-analysis workflows;
- parity evaluation used in the current presentation.

Reference SSMD results:

```text
Equation 5 — SINTEF
Log-MSE = 0.716712

Equation 6 — SINTEF
Log-MSE = 0.128723

Global regressed c,d
Log-MSE ≈ 0.116
R²_log  ≈ 0.548
```

The global `c,d` model reduces Log-MSE by approximately 10.1% relative to the reconstructed SINTEF Equation-6 reference while replacing regime-specific `c,d` values with one global pair. `eta` remains gas-condition dependent.

## Next scientific workflow — droplet-size distributions

The normalized distribution database already exists:

```text
experiment_id
droplet_diameter
volume_fraction
```

The next development step is to reconstruct the droplet-size distribution modelling pipeline on top of this database while preserving the same architecture used for SSDI and SSMD:

```text
data selection
        ↓
distribution model / physics
        ↓
parameter estimation
        ↓
prediction
        ↓
persistence
        ↓
statistical evaluation
```

Before structural changes are introduced, consult the existing distribution-related source files and project documentation.
