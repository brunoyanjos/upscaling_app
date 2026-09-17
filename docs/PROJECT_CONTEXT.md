# Project Context

## Purpose

The project develops a reproducible workflow for processing, modelling, and analysing oil-dispersion experiments.

The main scientific components are:

- SSDI modelling;
- SSMD modelling;
- droplet-size distribution analysis;
- parameter estimation with JAX;
- statistical validation and residual analysis.

The current objective is to replace isolated analysis scripts with a structured application composed of normalized databases, reusable pipelines, configuration files, and a command-line interface.

## Current Architecture

The Python package follows a `src/` layout:

```text
upscaling_app/
├── configs/
├── data/
│   ├── raw/
│   └── database/
├── docs/
├── src/
│   └── upscaling_app/
│       ├── analysis/
│       ├── database/
│       │   ├── build.py
│       │   └── utils/
│       ├── models/
│       ├── upscaling/
│       │   ├── ssdi/
│       │   ├── ssmd/
│       │   └── distributions/
│       ├── cli.py
│       └── paths.py
├── pyproject.toml
└── README.md
```

The application is installed in editable mode:

```bash
pip install -e .
```

The command-line entry point is:

```bash
upscaling
```

## Database Design

Raw experimental files are not used directly by modelling pipelines.

They are first converted into normalized databases:

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

### Oil properties

`oil_properties.xlsx` stores properties that belong to the oil itself.

Typical fields include:

```text
oil_id
oil_name
density
pour_point
wax_fraction
asphaltene_fraction
viscosity_20c
viscosity_50c
```

`oil_id` is the SINTEF oil code, such as `3014` or `4661`.

### Experiments

`experiments.xlsx` stores individual experimental conditions.

Typical fields include:

```text
experiment_id
oil_id
dispersion_kind
dispersion_tag
nozzle_diameter
has_gas
ift
oil_flow
gas_flow
oil_viscosity
gas_density
oil_density
measured_d50
source_sheet
```

The 2 mm experiments with and without gas are considered distinct experimental conditions.

Gas presence must remain explicit through `has_gas` and `gas_flow`.

### Droplet-size distributions

`distributions.xlsx` stores the measured droplet-size distribution associated with each experiment.

The normalized structure is:

```text
experiment_id
droplet_diameter
volume_fraction
```

Each experiment therefore has multiple distribution rows.

## Identifiers

`experiment_id` must be deterministic.

The same experiment must receive the same identifier every time the database is rebuilt.

The identifier is generated from experimental metadata using UUID5 rather than UUID4.

The current identity uses:

```text
oil_id
source sheet
dispersion tag
```

The same identifier-generation function must be used by both the experiment builder and the distribution builder.

## Dispersion Types

The current high-level classification is:

```text
Untreated
SSDI
SSMD
```

Examples of source tags include:

```text
3014-Untreated
SSDI-C9500
SSDI-IBC
WJ-40%
WJ-45%
WJ-50%
```

Raw source naming should be normalized during database construction rather than inside modelling pipelines.

## Units

Normalized databases should use SI units whenever applicable.

Current convention:

```text
density              kg/m³
dynamic viscosity    Pa·s
diameter              m
volumetric flow       m³/s
interfacial tension   N/m
fractions             dimensionless
```

Temperature values such as pour point may remain in °C when this is the natural reporting unit.

Conversions from source spreadsheets must occur during database construction.

## CLI

The current CLI is the application entry point.

The first implemented database workflow is:

```bash
upscaling database build
```

This command builds:

```text
data/database/
├── oil_properties.xlsx
├── experiments.xlsx
└── distributions.xlsx
```

Future workflows will include:

```bash
upscaling ssdi --config <config.toml>
upscaling ssmd --config <config.toml>
upscaling distribution --config <config.toml>
upscaling analyze --config <config.toml>
```

## Design Principles

The project should follow these rules:

1. Raw spreadsheets are parsed only in the database layer.
2. Modelling pipelines consume normalized databases.
3. Physical equations must remain separate from data ingestion.
4. Statistical analysis must remain separate from model calibration.
5. Experimental identifiers must be stable across database rebuilds.
6. SI units should be used internally whenever applicable.
7. Reusable logic should live inside `src/upscaling_app/`.
8. Avoid numbered one-off scripts as the project grows.
9. Configuration should define experimental selections and model settings rather than hard-coded constants.
10. Database rebuilding should be deterministic and idempotent.

## Milestone 1 — Data Architecture and CLI Foundation

Current completed work:

- migration to a `src/` Python package layout;
- `pyproject.toml` package configuration;
- CLI entry point;
- database build command;
- oil-property database design;
- experiment database design;
- droplet-size distribution database design;
- deterministic experiment identifiers;
- normalization of raw SINTEF data.

## Next Milestone — SSDI Pipeline

The next development phase is the reconstruction of the SSDI workflow using the normalized database architecture.

The previous SSDI implementation included:

- dataset selection by oil and nozzle diameter;
- Weber and Capillary number evaluation;
- grid search for initial coefficients;
- JAX-based model evaluation;
- gradient calculation with `jax.value_and_grad`;
- L-BFGS-B coefficient optimization;
- parity analysis;
- residual analysis;
- IQR-based outlier investigation.

The new implementation should preserve the validated physical formulation while removing hard-coded dataset selections and separating:

```text
data selection
physics
optimization
prediction
metrics
outlier analysis
result persistence
```

The SSDI reconstruction should be performed before expanding the same architecture to SSMD and distribution-model fitting.
