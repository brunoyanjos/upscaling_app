# Milestone 3 — SSMD Pipeline Reconstruction

**Status:** In progress — finalization stage

## Objective

Reconstruct the SSMD modelling workflow on top of the normalized database architecture established in Milestone 1 and the modelling architecture established in Milestone 2.

The SSMD pipeline preserves the reconstructed SINTEF formulation as the production reference while keeping data access, derived physics, calibration, prediction, persistence, statistical analysis, and predictive validation separated.

Exploratory research on alternative SSMD upscaling correlations remains isolated from the production-reference workflow.

---

## 3.1 Data and Physics Reconstruction

**Status:** Completed

### Normalized data consumption

The SSMD workflow consumes the normalized experiment database rather than the original SINTEF spreadsheets.

The current SSMD dataset contains:

```text
90 SSMD experiments
10 oils

30 experiments — 3 mm nozzle, no gas
30 experiments — 2 mm nozzle, no gas
30 experiments — 2 mm nozzle, with gas
```

Raw spreadsheet interpretation remains confined to the database layer.

### SSMD-specific normalized fields

The experiment database includes:

```text
water_jet_fraction
water_flow
water_nozzle_diameter
```

Internal units follow the SI convention:

```text
water_jet_fraction       dimensionless
water_flow               m³/s
water_nozzle_diameter    m
```

### Treated / untreated pairing

Each SSMD experiment is paired with its untreated reference through:

```text
oil_id
nozzle_diameter
has_gas
```

The modelling workflow keeps measured and predicted untreated droplet sizes separate:

```text
untreated_d50_measured
untreated_d50_pred
```

For SSMD model development:

```text
dR_measured = measured_d50 / untreated_d50_measured
```

For end-to-end prediction:

```text
d50_treated_pred = dR_pred * untreated_d50_pred
```

The predicted untreated diameter is consumed from persisted SSDI reference predictions rather than recalculated inside SSMD.

### Untreated hydrodynamics

The reconstructed preprocessing computes the untreated release quantities required by the SSMD formulation, including:

```text
untreated_gas_void_fraction
untreated_mixed_density
untreated_volumetric_velocity
untreated_modified_velocity
untreated_reduced_gravity
untreated_froude
untreated_effective_velocity
```

For gas-containing releases:

```text
U_vol = (Q_oil + Q_gas) / A

rho_mix =
    (rho_oil Q_oil + rho_gas Q_gas)
    / (Q_oil + Q_gas)

U_modified =
    U_vol sqrt(rho_mix / rho_oil)
```

Reference ambient constants:

```text
rho_water_jet = 1000 kg/m³
rho_seawater  = 1024 kg/m³
g             = 9.81 m/s²
```

### Water-jet properties

The SSMD preprocessing computes:

```text
water_velocity
water_momentum_flux
water_kinetic_power
```

with:

```text
A_w = pi D_w² / 4
U_w = Q_w / A_w
M_w = rho_w Q_w U_w
P_w = 1/2 rho_w Q_w U_w²
```

### Oil / gas momentum and momentum amplification

The untreated oil/gas momentum flux is evaluated with the untreated effective velocity:

```text
M_o =
    (rho_oil Q_oil + rho_gas Q_gas)
    U_effective
```

The momentum amplification is:

```text
A_M = (M_o + M_w) / M_o
```

---

## 3.2 SINTEF Reference Reconstruction

**Status:** Completed and reproducible

### Equation 5

The reconstructed SINTEF momentum-amplification model is:

```text
dR = (eta A_M)^(-3/5)
```

Reference efficiency factors:

```text
no gas    eta = 0.85
with gas  eta = 0.68
```

Reference performance:

```text
Log-MSE = 0.7167120356
```

### Equation 6

The reconstructed oil-property correction is:

```text
dR = (eta A_M)^(-3/5) * (c + d mu/sigma)
```

The IFT term uses the untreated reference IFT.

Full-precision reconstructed SINTEF coefficients:

```text
3 mm — no gas
eta = 0.85
c   = 0.33063475973887657
d   = 0.05

2 mm — no gas
eta = 0.85
c   = 0.46170083447858073
d   = 0.05

2 mm — gas
eta = 0.6779545878291601
c   = 0.5720125321034614
d   = 0.05
```

Reference performance:

```text
Log-MSE = 0.1287225708
```

The large improvement relative to Equation 5 is part of the reconstructed SINTEF reference and does not by itself constitute independent physical validation of the correction term.

---

## 3.3 Explicit SSMD Model Versions

**Status:** Implemented

The current production SSMD package defines:

```text
sintef_baseline
regressed_cd_baseline
regressed_cd_global
```

### `sintef_baseline`

Uses the reconstructed SINTEF Equation-6 coefficients by experimental regime.

### `regressed_cd_baseline`

Preserves the SINTEF model structure and `eta` treatment while fitting `c,d` separately for each experimental regime.

This version is useful as a calibration diagnostic but retains regime-specific empirical coefficients.

### `regressed_cd_global`

Preserves the same Equation-6 structure while fitting one global `c,d` pair across all 90 SSMD experiments.

Current global coefficients are approximately:

```text
c = 0.4457
d = 0.0257
```

Current global in-sample performance:

```text
Log-MSE ≈ 0.116
R²_log  ≈ 0.548
```

For comparison, the reconstructed SINTEF reference gives approximately:

```text
Log-MSE ≈ 0.129
R²_log  ≈ 0.498
```

Therefore the global `c,d` regression reduces Log-MSE by approximately:

```text
10.1 %
```

Interpretation:

> A single global `c,d` pair slightly improves the overall in-sample fit while removing the regime dependence of these two coefficients.

Important limitation:

```text
eta remains gas-condition dependent
```

The global regression is therefore an upscaling-oriented simplification, not a completed universal SSMD closure.

---

## 3.4 Prediction and Persistence

**Status:** Implemented

The SSMD baseline workflow currently:

```text
load normalized calibration data
        ↓
add derived SSMD physics
        ↓
build SINTEF reference prediction
        ↓
fit c,d by regime
        ↓
fit global c,d
        ↓
build experiment-level prediction tables
        ↓
persist predictions
```

Prediction outputs contain explicit `model_version` labels so that model analysis can consume persisted results without recalibrating inside the analysis layer.

The final treated prediction convention remains:

```text
d50_treated_pred = dR_pred * untreated_d50_pred
```

---

## 3.5 Statistical Analysis and Presentation Evaluation

**Status:** Implemented for current presentation needs; predictive validation remains incomplete

The modelling and analysis responsibilities are separated.

The `analysis/ssmd/` workflow currently supports model evaluation from persisted predictions, including parity analysis for:

```text
Equation 5 reference
SINTEF Equation 6 reference
regressed_cd_global
```

Current presentation reference metrics:

```text
Equation 5
Log-MSE = 0.716712

SINTEF Equation 6
Log-MSE = 0.128723
R²_log  ≈ 0.498

Global regressed c,d
Log-MSE ≈ 0.116
R²_log  ≈ 0.548
```

The experimental-analysis layer also contains SSMD-specific descriptive diagnostics, including regime-separated water-jet response, monotonicity, hydrodynamic screening, and property screening.

These diagnostics are descriptive and must remain distinct from model calibration and predictive validation.

---

## 3.6 Known Scientific Limitations

### Experimental-regime structure

The database treats:

```text
2 mm — no gas
3 mm — no gas
2 mm — gas
```

as distinct experimental conditions.

### Identifiability limitation

Within a fixed:

```text
oil_id
nozzle_diameter
has_gas
```

group, the water-jet variables are strongly coupled by the experimental design.

For fixed water-nozzle geometry:

```text
U_w proportional to Q_w
M_w proportional to Q_w²
P_w proportional to Q_w³
```

Therefore the current campaign cannot independently identify whether water flow, velocity, momentum flux, or kinetic power is the fundamental controlling variable.

### Full-scale limitation

The SINTEF formulation still contains empirical parameters whose transferability is incomplete.

The global regression removes regime dependence from `c,d`, but `eta` remains condition dependent.

No universal mapping from arbitrary full-scale operating conditions to all SSMD coefficients has yet been validated.

Exploratory correlation development remains tracked separately in:

```text
RESEARCH_SSMD_UPSCALING_UPDATED.md
```

---

## 3.7 Pipeline Finalization

**Status:** In progress

### Completed items

```text
- normalized SSMD data consumption;
- treated / untreated pairing;
- derived SSMD physics;
- reconstructed SINTEF Equation 5;
- reconstructed SINTEF Equation 6;
- explicit SSMD model versions;
- by-regime c,d regression;
- global c,d regression;
- experiment-level prediction tables;
- result persistence;
- model reporting;
- separated analysis/ssmd workflow;
- parity evaluation for presentation;
- SSMD experimental-analysis workflow;
- CLI dispatch for SSMD analysis.
```

### Remaining items before Milestone 3 can be marked Completed

```text
- confirm final CLI surface and command naming;
- finish standard SSMD analysis reporting organization;
- decide and implement predictive validation where scientifically meaningful;
- remove or isolate any remaining temporary exploratory diagnostics;
- verify final persisted-output paths and schemas;
- freeze final numerical reference outputs in documentation;
- perform a final architecture / reproducibility check.
```

---

## Current Architecture Rule

```text
normalized database
        ↓
data selection
        ↓
derived physics
        ↓
physical model
        ↓
calibration / reference coefficients
        ↓
prediction
        ↓
persistence
        ↓
statistical analysis
        ↓
validation
```

Exploratory correlation development remains outside the production pipeline.

---

## Milestone Completion Criteria

Milestone 3 should be marked **Completed** only when:

```text
- SINTEF SSMD baseline is frozen and reproducible;
- prediction outputs are persisted;
- model versions are explicit;
- reporting is implemented;
- statistical analysis is separated from modelling;
- CLI workflows are stable;
- numerical reference results are documented;
- current limitations are documented;
- exploratory research code is separated from production code.
```

The project is close to these criteria, but predictive-validation scope and final CLI / reporting cleanup still need to be closed explicitly.

---

## Next Immediate Step

For the current presentation, the SSMD section is considered closed.

The next scientific workflow to reconstruct is the droplet-size distribution pipeline.

Before introducing structural changes, inspect the normalized `distributions.xlsx` database and the existing distribution-related source files.
