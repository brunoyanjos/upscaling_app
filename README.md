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

Production baseline SSDI and SSMD workflows are exposed through the project CLI according to the current implementation. Newer oil-wise and presentation-performance workflows are implemented in the package but are pending final CLI integration.

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

The reconstructed SSDI reference and recalibrated models are evaluated independently from the calibration workflow. The current presentation workflow also includes oil-wise in-sample calibration and a 2 mm gas / no-gas performance diagnostic.

Current reference comparison:

```text
reference    Log-MSE 0.435997    R² 0.643330    RMSE 0.4910 mm    MAPE 64.43 %
global       Log-MSE 0.426986    R² 0.685533    RMSE 0.4610 mm    MAPE 57.96 %
oil-wise     Log-MSE 0.128635    R² 0.828497    RMSE 0.3405 mm    MAPE 30.11 %
```

The oil-wise result is an in-sample diagnostic; leave-one-oil-out remains the cross-oil predictive validation workflow.

### Milestone 3 — SSMD Pipeline Reconstruction

**Status: In progress — finalization stage**

Current SSMD capabilities include:

- normalized 90-experiment / 10-oil calibration dataset;
- untreated-release and water-jet derived physics;
- reconstructed SINTEF Equation 5 and Equation 6;
- explicit model versions;
- by-regime and global `c,d` regression;
- oil-wise identifiable-factor regression;
- persisted experiment-level predictions and local calibration summaries;
- SSMD reporting;
- separate experimental and model-analysis workflows;
- parity evaluation used in the current presentation;
- global / oil-wise comparison overall and by SSMD regime.

Reference SSMD results:

```text
Equation 5 — SINTEF
Log-MSE = 0.716712

Equation 6 — SINTEF
Log-MSE = 0.128723

Global regressed c,d
Log-MSE = 0.115841
R²      = 0.570007
MAPE    = 30.08 %

Oil-wise identifiable factor
Log-MSE = 0.119372
R²      = 0.515264
MAPE    = 31.39 %
```

The global `c,d` model remains slightly better than the oil-wise SSMD diagnostic on the pooled in-sample dataset. The oil-wise workflow fits the identifiable factor `k_i = c + d mu_i/sigma_i` rather than independent local `c_i,d_i` pairs. `eta` remains gas-condition dependent.

## Current finalization checkpoint

The main presentation analyses for SSDI and SSMD are implemented. Before the modelling milestones are treated as fully stabilized, the following engineering work remains:

```text
- expose SSDI oil-wise and performance workflows through the CLI;
- expose SSMD oil-wise and performance workflows through the CLI;
- review model-version constants and persistence schemas;
- remove temporary diagnostic code;
- run end-to-end reproducibility checks from a clean state;
- freeze final numerical reference outputs in the documentation.
```

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
