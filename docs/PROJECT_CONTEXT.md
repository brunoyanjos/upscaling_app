# Project Context

## Purpose

The project develops a reproducible scientific Python workflow for processing, modelling, predicting, and analysing oil-dispersion experiments.

The main scientific components are:

- SSDI modelling;
- SSMD modelling;
- droplet-size distribution modelling;
- parameter estimation;
- statistical analysis, residual analysis, and predictive validation.

The application replaces isolated analysis scripts with normalized databases, reusable pipelines, explicit model versions, persisted results, and a project-wide command-line interface.

## Current status

```text
Milestone 1 — Data Architecture and CLI Foundation
Status: Completed

Milestone 2 — SSDI Pipeline Reconstruction
Status: Completed

Milestone 3 — SSMD Pipeline Reconstruction
Status: In progress — finalization stage

Next scientific workflow
Droplet-size distributions
```

For the current presentation, the SSDI and SSMD blocks are considered closed. The next presentation section is droplet-size distributions.

## Current architecture

The Python package follows a `src/` layout:

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
│       │   ├── build.py
│       │   └── utils/
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

## Database design

Raw experimental spreadsheets are not consumed directly by scientific pipelines.

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

Current databases:

```text
data/database/
├── oil_properties.xlsx
├── experiments.xlsx
└── distributions.xlsx
```

### Oil properties

`oil_properties.xlsx` stores properties associated with the oil itself, including identifiers, density, pour point, wax/asphaltene content, and reference viscosities.

### Experiments

`experiments.xlsx` stores normalized experimental conditions.

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
water_jet_fraction
water_flow
water_nozzle_diameter
oil_viscosity
gas_density
oil_density
measured_d50
source_sheet
```

The 2 mm conditions with and without gas remain distinct experimental regimes.

### Droplet-size distributions

`distributions.xlsx` stores measured droplet-size distribution data in normalized form:

```text
experiment_id
droplet_diameter
volume_fraction
```

Each experiment therefore has multiple distribution rows linked by deterministic `experiment_id`.

## Identifiers

`experiment_id` must remain deterministic.

The same experiment must receive the same identifier every time the database is rebuilt.

The current database architecture uses UUID5-based deterministic identifiers shared between experiment and distribution builders.

## Dispersion types

The current high-level classification is:

```text
Untreated
SSDI
SSMD
```

Normalized tags include forms such as:

```text
3014-Untreated
SSDI-C9500
SSDI-IBC
WJ-40%
WJ-45%
WJ-50%
```

Raw source naming is normalized during database construction rather than interpreted inside modelling pipelines.

## Units

Normalized databases use SI units whenever applicable:

```text
density              kg/m³
dynamic viscosity    Pa·s
diameter             m
volumetric flow      m³/s
interfacial tension  N/m
fractions             dimensionless
```

Temperature quantities such as pour point may remain in °C when that is the natural reporting unit.

## Architectural rules

1. Raw spreadsheets are parsed only in the database layer.
2. Modelling pipelines consume normalized databases.
3. Physical equations remain separate from data ingestion.
4. Calibration / optimization remain separate from statistical analysis.
5. Prediction outputs are persisted before downstream model evaluation whenever practical.
6. Experimental identifiers remain stable across database rebuilds.
7. SI units are used internally whenever applicable.
8. Reusable logic belongs inside `src/upscaling_app/`.
9. Avoid numbered one-off scripts as the long-term execution path.
10. Exploratory models must remain distinguishable from production-reference models.

## SSDI status

Milestone 2 is completed.

The SSDI architecture separates:

```text
data selection
        ↓
derived physics
        ↓
physical correlation
        ↓
coefficient calibration
        ↓
prediction
        ↓
persistence
        ↓
statistical analysis
        ↓
predictive validation
```

The current presentation includes hydrodynamic screening, physical scaling, coefficient calibration, parity analysis, residual diagnostics, in-sample sensitivity analyses, and leave-one-oil-out validation.

## SSMD status

Milestone 3 is in finalization.

### Dataset

```text
90 SSMD experiments
10 oils

30 — 3 mm, no gas
30 — 2 mm, no gas
30 — 2 mm, gas
```

### Derived physics

The SSMD preprocessing includes untreated-release hydrodynamics and water-jet quantities such as:

```text
water_velocity
water_momentum_flux
water_kinetic_power
oil / gas momentum
momentum_amplification
```

The primary treatment variable is:

```text
A_M = (M_o + M_w) / M_o
```

The measured relative response is:

```text
dR_measured = measured_d50 / untreated_d50_measured
```

### Production reference

SINTEF Equation 5:

```text
dR = (eta A_M)^(-3/5)
Log-MSE = 0.716712
```

SINTEF Equation 6:

```text
dR = (eta A_M)^(-3/5) * (c + d mu/sigma)
Log-MSE = 0.128723
```

The IFT term uses the untreated reference IFT.

### Current model versions

```text
sintef_baseline
regressed_cd_baseline
regressed_cd_global
```

`regressed_cd_global` fits one global pair of `c,d` coefficients over all SSMD experiments while retaining the SINTEF model structure and gas-dependent `eta` treatment.

Current approximate global fit:

```text
c_global ≈ 0.4457
d_global ≈ 0.0257
Log-MSE  ≈ 0.116
R²_log   ≈ 0.548
```

The reconstructed SINTEF Equation-6 reference gives approximately:

```text
Log-MSE ≈ 0.129
R²_log  ≈ 0.498
```

The global `c,d` regression therefore reduces Log-MSE by approximately 10.1% while replacing regime-specific `c,d` values with a single pair.

This is an in-sample calibration result. `eta` remains condition dependent, and no universal full-scale SSMD closure has yet been validated.

### SSMD analysis

Model evaluation is separated from calibration.

The SSMD analysis workflow consumes persisted predictions and currently supports parity comparisons for the momentum-only Equation 5, reconstructed SINTEF Equation 6, and the global `c,d` regression.

Experimental SSMD analysis remains in `analysis/experimental/` and includes descriptive regime response, monotonicity, and physical screening diagnostics.

## CLI

The `upscaling` command remains the project-wide execution entry point.

Current analysis examples include:

```bash
upscaling analyze experimental descriptive
upscaling analyze experimental ssdi
upscaling analyze experimental ssmd
upscaling analyze experimental treatment-effect
upscaling analyze ssmd
```

CLI command naming should be treated as part of the public project surface and stabilized before Milestone 3 is formally closed.

## Next scientific workflow — droplet-size distributions

The next phase is to reconstruct the droplet-size distribution workflow using the normalized `distributions.xlsx` database.

Before structural changes, inspect:

```text
- the normalized distribution database;
- existing distribution-related source files;
- any previous analytical distribution fitting methodology;
- current presentation requirements.
```

The distribution pipeline should preserve the same separation used elsewhere:

```text
data selection
        ↓
distribution formulation
        ↓
parameter estimation
        ↓
prediction
        ↓
persistence
        ↓
statistical evaluation
```

No new distribution model structure should be introduced before the existing implementation and project documentation are reviewed.
