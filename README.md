# Upscaling App

Scientific Python application for the analysis and modelling of oil dispersion experiments.

The project currently focuses on:

- SSDI modelling;
- SSMD modelling;
- droplet-size distribution analysis;
- parameter estimation using JAX;
- statistical analysis and model validation.

## Project structure

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
│       ├── models/
│       ├── upscaling/
│       ├── cli.py
│       └── paths.py
├── pyproject.toml
└── README.md
```

## Installation

Install the project in editable mode:

```bash
pip install -e .
```

## Command-line interface

The application is executed through:

```bash
upscaling
```

Available workflows will include:

```bash
upscaling database build
upscaling ssdi --config <config.toml>
upscaling ssmd --config <config.toml>
upscaling distribution --config <config.toml>
upscaling analyze --config <config.toml>
```

## Database architecture

Raw experimental data are converted into normalized databases:

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

The current databases are:

```text
data/database/
├── oil_properties.xlsx
├── experiments.xlsx
└── distributions.xlsx
```

`experiment_id` provides the link between experimental conditions and droplet-size distributions.

Experimental identifiers are deterministic so that database reconstruction preserves relationships between datasets.

## Units

Processed databases use SI units whenever applicable.

Examples:

- density: kg/m³
- viscosity: Pa·s
- diameter: m
- volumetric flow rate: m³/s
- interfacial tension: N/m
- fractions: dimensionless

## Current development status

### Milestone 1 — Data architecture and CLI foundation

Current work includes:

- Python package structure using `src/`;
- command-line interface;
- normalization of raw SINTEF data;
- oil-property database;
- experiment database;
- droplet-size distribution database;
- deterministic relationships between experimental data.

### Next milestone

Milestone 2 will reconstruct the SSDI modelling pipeline using the new database architecture.
