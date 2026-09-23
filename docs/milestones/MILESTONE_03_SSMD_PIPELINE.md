# Milestone 3 — SSMD Pipeline Reconstruction

**Status:** In progress

## Objective

Reconstruct the SSMD modelling workflow on top of the normalized database architecture established in Milestone 1 and the modelling architecture established in Milestone 2.

The SSMD pipeline must preserve the validated SINTEF formulation as the production reference while keeping data access, derived physics, calibration, prediction, persistence, statistical analysis, and predictive validation separated.

Exploratory research on alternative SSMD upscaling correlations must remain isolated from the reconstructed production pipeline.

---

## 3.1 Data and Physics Reconstruction

**Status:** Completed

### Normalized data consumption

The SSMD workflow consumes the normalized experiment database rather than the original SINTEF spreadsheets.

The SSMD dataset currently contains:

```text
90 SSMD experiments
10 oils

30 experiments — 3 mm nozzle, no gas
30 experiments — 2 mm nozzle, no gas
30 experiments — 2 mm nozzle, with gas
```

Raw spreadsheet interpretation remains confined to the database layer.

### SSMD-specific normalized fields

The experiment database was extended with:

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

The SSMD calibration dataset keeps measured and predicted untreated droplet sizes separate:

```text
untreated_d50_measured
untreated_d50_pred
```

For SSMD model development:

```text
dR_measured =
    measured_d50 / untreated_d50_measured
```

For end-to-end prediction:

```text
d50_treated_pred =
    dR_pred * untreated_d50_pred
```

The predicted untreated diameter is obtained from persisted SSDI reference predictions rather than recalculated inside SSMD.

### SSDI integration

SSMD consumes persisted SSDI results through:

```text
experiment_id
model_version
d50_pred
```

The current reference SSDI version is:

```text
sintef_baseline
```

### Untreated hydrodynamics

The untreated hydrodynamics were reconstructed consistently with the validated SINTEF implementation.

Derived quantities include:

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
U_vol =
    (Q_oil + Q_gas) / A

rho_mix =
    (rho_oil Q_oil + rho_gas Q_gas)
    / (Q_oil + Q_gas)

U_modified =
    U_vol sqrt(rho_mix / rho_oil)
```

The reduced gravity uses ambient seawater density:

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
A_w = π D_w² / 4

U_w = Q_w / A_w

M_w = rho_w Q_w U_w

P_w = 1/2 rho_w Q_w U_w²
```

### Oil / gas momentum

The untreated oil/gas momentum flux is evaluated using the untreated effective velocity:

```text
M_o =
    (rho_oil Q_oil + rho_gas Q_gas)
    U_effective
```

The momentum amplification is:

```text
A_M =
    (M_o + M_w) / M_o
```

### Relative droplet-size response

The experimental SSMD response is:

```text
dR_measured =
    d50_treated_measured
    / d50_untreated_measured
```

---

## 3.2 SINTEF Baseline Reconstruction

**Status:** Reconstructed; production workflow still to be finalized

### Equation 5

The reconstructed SINTEF momentum-amplification model is:

dR = (eta A_M)^(-3/5)

The SINTEF efficiency factors are:

```text
no gas    eta = 0.85
with gas  eta = 0.68
```

### Equation 6

The oil-property correction is:

dR = (eta A_M)^(-3/5) * (c + d mu/sigma)

The reconstructed full-precision reference coefficients are:

```text
3 mm:
eta = 0.85
c   = 0.33063475973887657
d   = 0.05

2 mm:
eta = 0.85
c   = 0.46170083447858073
d   = 0.05

2 mm + gas:
eta = 0.6779545878291601
c   = 0.5720125321034614
d   = 0.05
```

The IFT term must use the untreated reference IFT.

### Reconstructed reference performance

```text
Equation 5 — SINTEF
Log-MSE = 0.7167120356

Equation 6 — SINTEF
Log-MSE = 0.1287225708
```

### Prediction convention

The final treated prediction uses:

```text
d50_treated_pred =
    dR_pred * untreated_d50_pred
```

The measured untreated diameter is used only for experimental response construction and calibration diagnostics.

---

## 3.3 Statistical Validation and Model Limitations

**Status:** Partially completed

### Diagnostic analyses performed

The current reconstruction has already been used to investigate:

```text
logarithmic residuals
momentum-amplification sensitivity
gas / no-gas separation
oil-property residual structure
leave-one-oil-out diagnostics
within-group response to water-jet intensity
```

These analyses guide a separate research programme and must not replace the reconstructed SINTEF baseline.

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

### Full-scale limitation of the SINTEF correlation

The reconstructed SINTEF model requires:

```text
eta
c
d
```

whose values are currently condition-dependent.

The campaign does not provide a universal mapping from full-scale operating conditions to these coefficients.

The reconstructed model should therefore be interpreted as valid within the experimental domain, not as a closed universal full-scale SSMD correlation.

The extrapolation research is tracked separately in:

```text
RESEARCH_SSMD_UPSCALING.md
```

---

## 3.4 Pipeline Completion

**Status:** Pending

The remaining production work should complete the SSMD architecture following the SSDI reference pattern.

Target structure:

```text
src/upscaling_app/
├── upscaling/
│   └── ssmd/
│       ├── calibration/
│       ├── io/
│       │   ├── data.py
│       │   └── persistence.py
│       ├── physics/
│       │   ├── derived_properties.py
│       │   └── model.py
│       ├── workflows/
│       │   └── baseline.py
│       ├── prediction.py
│       ├── reporting.py
│       ├── results.py
│       └── versions.py
│
└── analysis/
    └── ssmd/
        ├── evaluation/
        ├── io/
        ├── metrics.py
        ├── pipeline.py
        ├── plotting.py
        └── reporting.py
```

Remaining tasks:

```text
1. Freeze the reconstructed SINTEF baseline equations.
2. Define explicit SSMD model versions.
3. Produce experiment-level prediction tables.
4. Persist SSMD results under data/results/.
5. Add standard SSMD metrics and reporting.
6. Separate modelling and statistical-analysis CLI workflows.
7. Add predictive validation where scientifically meaningful.
8. Remove temporary exploratory diagnostics from the production baseline.
9. Document final reference outputs.
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

At that point this document must be updated from:

```text
Status: In progress
```

to:

```text
Status: Completed
```

and the final architecture, model versions, reference metrics, persisted outputs, known limitations, and next milestone must be recorded.

---

## Next Immediate Step

Return to the reconstructed SINTEF baseline and finish the production SSMD pipeline before continuing development of a new full-scale SSMD correlation.

The exploratory findings obtained during reconstruction are preserved separately in:

```text
RESEARCH_SSMD_UPSCALING.md
```
