# Milestone 3 — SSMD Pipeline Reconstruction

**Status:** Completed — reconstructed, reproducible, and predictively validated within the current experimental scope

## Objective

Reconstruct the SSMD modelling workflow on top of the normalized database architecture established in Milestone 1 and the modelling architecture established in Milestone 2.

The SSMD pipeline preserves the reconstructed SINTEF formulation as the production reference while keeping:

```text
data access
derived physics
calibration
prediction
persistence
statistical analysis
predictive validation
```

as separate responsibilities.

Exploratory research on alternative SSMD upscaling correlations remains isolated from the production-reference workflow.

Milestone completion means that the current SSMD workflow is structurally reproducible, numerically documented, and equipped with an out-of-oil predictive-validation workflow. It does **not** imply that the current formulation is a universal full-scale SSMD closure.

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
dR_measured =
    measured_d50
    /
    untreated_d50_measured
```

For end-to-end prediction:

```text
d50_treated_pred =
    dR_pred
    *
    untreated_d50_pred
```

The predicted untreated diameter is consumed from persisted SSDI predictions rather than recalculated inside SSMD.

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
U_vol =
    (Q_oil + Q_gas)
    /
    A

rho_mix =
    (rho_oil Q_oil + rho_gas Q_gas)
    /
    (Q_oil + Q_gas)

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
A_M =
    (M_o + M_w)
    /
    M_o
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
no gas     eta = 0.85
with gas   eta = 0.68
```

Reference performance:

```text
Log-MSE = 0.7167120356
```

The negative logarithmic-space predictive skill observed for this momentum-only form is mathematically valid and indicates that momentum amplification alone is insufficient to reproduce the measured SSMD response.

### Equation 6

The reconstructed oil-property correction is:

```text
dR =
    (eta A_M)^(-3/5)
    *
    (c + d mu/sigma)
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
R²_log  ≈ 0.498
```

The large improvement relative to Equation 5 is part of the reconstructed SINTEF reference and does not by itself constitute independent physical validation of the correction term.

---

## 3.3 Explicit SSMD Model Variants

**Status:** Implemented

The reconstructed SSMD workflow currently distinguishes the following model roles:

```text
SINTEF reference
by-regime c,d calibration
global c,d calibration
oil-wise factor diagnostic
```

The production package retains explicit model-version labels in persisted prediction outputs.

### SINTEF reference

Uses the reconstructed SINTEF Equation-6 coefficients by experimental regime.

Its purpose is to preserve the published/reference formulation independently from any recalibration performed in this project.

### By-regime `c,d` calibration

Preserves the SINTEF Equation-6 structure and `eta` treatment while fitting `c,d` separately for each experimental regime.

This branch is retained as a calibration diagnostic because it still preserves regime-specific empirical coefficients.

### Global `c,d` calibration

Preserves the same Equation-6 structure while fitting one global `c,d` pair across all 90 SSMD experiments.

Current global coefficients are approximately:

```text
c_global ≈ 0.4457
d_global ≈ 0.0257
```

Current global in-sample performance:

```text
Log-MSE = 0.115841
R²_log  = 0.547970
RMSE    = 0.048987
MAPE    = 30.075610 %
```

For comparison, the reconstructed SINTEF Equation-6 reference gives approximately:

```text
Log-MSE ≈ 0.128723
R²_log  ≈ 0.498
```

The global `c,d` calibration therefore reduces in-sample Log-MSE by approximately:

```text
10.1 %
```

Interpretation:

> A single global `c,d` pair slightly improves the overall in-sample representation while removing the experimental-regime dependence of these two coefficients.

Important limitation:

```text
eta remains gas-condition dependent
```

The global regression is therefore an upscaling-oriented simplification, not a completed universal SSMD closure.

### Oil-wise factor diagnostic

The SSMD workflow also includes an oil-wise factor model used to diagnose oil-dependent heterogeneity.

For each oil, the local multiplicative property response is evaluated relative to the momentum term and summarized as an oil-specific factor:

```text
k_oil
```

This workflow is used to compare:

```text
global property response
vs.
oil-specific property response
```

and to inspect whether the global parameterization masks systematic oil-to-oil differences.

The oil-wise model is diagnostic. It is not interpreted as a predictive model for an unseen oil because its oil-specific factor is fitted using data from that oil.

---

## 3.4 Prediction and Persistence

**Status:** Implemented

The production modelling sequence is:

```text
load normalized calibration data
        ↓
add derived SSMD physics
        ↓
select model variant
        ↓
fit or load coefficients
        ↓
predict dR
        ↓
attach persisted SSDI untreated prediction
        ↓
predict treated d50
        ↓
build experiment-level prediction table
        ↓
persist predictions
```

Prediction outputs preserve the distinction between:

```text
SSMD model version
SSDI source version
experiment_id
```

The final treated prediction convention remains:

```text
d50_treated_pred =
    dR_pred
    *
    untreated_d50_pred
```

The SSMD layer therefore does not reimplement the SSDI untreated-droplet model.

### Separation of relative and end-to-end prediction

Two targets remain conceptually distinct:

```text
dR
    SSMD relative response

d50_treated
    end-to-end prediction
    =
    SSMD dR
    ×
    SSDI untreated d50
```

This distinction is important for validation because an end-to-end unseen-oil test would require both SSMD and SSDI upstream components to be independently trained without the held-out oil.

---

## 3.5 Statistical Analysis

**Status:** Implemented

The modelling and analysis responsibilities are separated.

Current SSMD statistical analysis is organized by scientific question rather than by generic scripts:

```text
src/upscaling_app/analysis/ssmd/
├── io/
├── metrics.py
├── performance/
│   ├── analysis.py
│   ├── pipeline.py
│   ├── plotting.py
│   ├── persistence.py
│   └── reporting.py
├── oil_wise/
│   ├── analysis.py
│   ├── pipeline.py
│   ├── plotting.py
│   ├── persistence.py
│   └── reporting.py
└── validation/
    ├── analysis.py
    ├── pipeline.py
    ├── plotting.py
    ├── persistence.py
    └── reporting.py
```

Shared prediction metrics are kept outside the question-specific modules so that performance evaluation and predictive validation use the same definitions.

### Performance analysis

The performance workflow evaluates persisted model predictions rather than recalibrating inside the analysis layer.

Current reference results:

```text
Equation 5
Log-MSE = 0.716712

SINTEF Equation 6
Log-MSE = 0.128723
R²_log  ≈ 0.498

Global regressed c,d
Log-MSE = 0.115841
R²_log  = 0.547970
```

### Oil-wise heterogeneity analysis

The oil-wise analysis compares the response implied by the global property factor with the independently fitted oil-specific factors.

Its purpose is to answer:

> Does one global property correction represent the ten oils uniformly, or does systematic oil-level heterogeneity remain?

This analysis is descriptive / diagnostic and remains separate from predictive validation.

### Experimental SSMD analysis

The independent experimental-analysis layer contains SSMD-specific descriptive diagnostics, including:

```text
water-jet response
regime-separated response
monotonicity
hydrodynamic screening
property screening
```

These diagnostics do not modify the validated SSMD equations.

---

## 3.6 Leave-One-Oil-Out Predictive Validation

**Status:** Implemented and numerically validated

### Scientific question

The global `c,d` calibration is fitted using all oils, so its in-sample metrics do not answer whether the same parameterization generalizes to an oil that did not participate in calibration.

The validation question is therefore:

> How well does the global SSMD `c,d` formulation predict an oil that is completely absent from the calibration data?

### Validation design

The implemented validation is leave-one-oil-out:

```text
for each oil:

    hold out one complete oil
            ↓
    calibrate c,d using the other 9 oils
            ↓
    predict dR for the held-out oil
            ↓
    store the out-of-oil predictions

repeat for all 10 oils
```

This produces:

```text
10 folds
90 out-of-oil predictions
1 prediction per SSMD experiment
```

Each fold contains:

```text
81 training experiments
9 test experiments
9 training oils
1 held-out oil
```

No oil appears simultaneously in the training and test populations of a fold.

### Primary validation target

The primary validation target is:

```text
dR
```

rather than end-to-end treated `d50`.

This is intentional.

The relative prediction:

```text
dR_pred
```

isolates the SSMD model being validated.

The end-to-end prediction:

```text
d50_treated_pred =
    dR_pred
    *
    untreated_d50_pred
```

also depends on the upstream SSDI model.

If the SSDI source was calibrated using the complete oil population, the resulting treated-D50 prediction would not constitute a fully independent unseen-oil end-to-end validation.

Therefore the current validation should be described as:

> out-of-oil predictive validation of the SSMD global `c,d` calibration

and not as:

> fully independent end-to-end unseen-oil validation of the complete SSDI + SSMD chain.

### Pooled validation result

Current in-sample global result:

```text
n                    = 90
Log-MSE              = 0.115841
R²_log               = 0.547970
RMSE                 = 0.048987
MAPE                  = 30.075610 %
mean log residual    = -0.058151
std log residual     = 0.337229
```

Current leave-one-oil-out result:

```text
n                    = 90
n_oils               = 10
Log-MSE              = 0.142664
R²_log               = 0.443304
RMSE                 = 0.061169
MAPE                  = 34.689105 %
mean log residual    = -0.088359
std log residual     = 0.369286
```

Relative degradation from the in-sample calibration:

```text
LOO Log-MSE increase = 23.154704 %
```

Interpretation:

> The global `c,d` formulation retains substantial predictive capability when transferred to a completely held-out oil, but its performance degrades measurably relative to the in-sample calibration.

The LOO result therefore supports some transferability across oils while also demonstrating that the available data retain important oil-dependent structure.

### Comparison with the SINTEF reference

The reconstructed SINTEF Equation-6 reference has:

```text
Log-MSE ≈ 0.128723
```

whereas the leave-one-oil-out global calibration gives:

```text
Log-MSE ≈ 0.142664
```

These values must not be interpreted as a direct predictive-validation ranking because they come from different evaluation designs:

```text
SINTEF Equation 6
    fixed reference formulation
    evaluated on the available dataset

global c,d LOO
    coefficients repeatedly recalibrated
    with one complete oil excluded per fold
```

The valid conclusion is narrower:

> The approximately 10.1 % in-sample Log-MSE improvement of the global `c,d` calibration over the reconstructed SINTEF reference does not persist as an equivalent out-of-oil predictive advantage.

### Oil-level validation results

Current fold-level results are:

| Held-out oil | c | d | Log-MSE | R²_log | Mean log residual | Std log residual |
|---:|---:|---:|---:|---:|---:|---:|
| 3014 | 0.451556 | 0.025175 | 0.054254 | 0.624083 | -0.126511 | 0.207436 |
| 3015 | 0.454082 | 0.025258 | 0.121400 | 0.330252 | -0.207663 | 0.296750 |
| 3016 | 0.447216 | 0.024255 | 0.175957 | 0.539734 | -0.073020 | 0.438124 |
| 4661 | 0.447906 | 0.025154 | 0.055627 | 0.721267 | -0.053776 | 0.243573 |
| 4662 | 0.424908 | 0.053771 | 0.293570 | 0.038237 | -0.527854 | 0.129644 |
| 4663 | 0.428561 | 0.026691 | 0.135918 | 0.128538 | +0.246978 | 0.290319 |
| 4664 | 0.453133 | 0.025242 | 0.033587 | 0.572410 | -0.149414 | 0.112564 |
| 4665 | 0.434717 | 0.026738 | 0.102170 | -0.876700 | +0.140422 | 0.304562 |
| 4666 | 0.430939 | 0.026666 | 0.273243 | 0.424107 | +0.104783 | 0.543181 |
| 4667 | 0.455152 | 0.024775 | 0.180915 | 0.401690 | -0.237532 | 0.374240 |

Important observations:

```text
oil 4662
    strong negative mean log residual
    comparatively small within-fold residual scatter
    unusually large fitted d coefficient when held out

oil 4666
    comparatively high Log-MSE
    small mean bias relative to its residual scatter
    strong within-oil variability

oil 4665
    negative fold-level R²_log
    but a lower Log-MSE than several other oils
```

The negative `R²_log` for oil 4665 is not by itself evidence of the largest absolute prediction error. It indicates poor explanatory performance relative to the within-fold logarithmic mean baseline.

For oil-level interpretation, the combined quantities:

```text
Log-MSE
mean log residual
std log residual
```

are therefore more informative than using `R²_log` alone.

### Coefficient stability

Most leave-one-oil-out folds produce:

```text
d ≈ 0.024 to 0.027
```

When oil `4662` is excluded:

```text
c = 0.424908
d = 0.053771
```

The much larger fitted `d` coefficient indicates that oil `4662` has strong leverage on the global property-correction slope.

This is an important identifiability / population-sensitivity result and should remain visible in future correlation-development studies.

It does not by itself justify removing oil `4662` from the production population.

### Validation outputs

The predictive-validation module produces:

```text
predictions
    one out-of-oil prediction per experiment

by_oil
    one summary row per held-out oil

summary
    pooled LOO metrics

comparison
    global in-sample vs pooled LOO metrics
```

The standard validation figures are:

```text
loo_parity.png
loo_residual_by_oil.png
```

The parity plot compares measured and predicted `dR`.

The residual-by-oil plot presents the already-calculated:

```text
mean log residual ± standard deviation
```

without introducing ranking or additional model fitting inside the plotting layer.

---

## 3.7 Scientific Interpretation

The SSMD reconstruction now distinguishes three levels of evidence:

```text
reference reconstruction
        ≠
in-sample calibration
        ≠
predictive validation
```

### Reference reconstruction

Demonstrates that the reconstructed implementation reproduces the intended SINTEF model structure and reference coefficients.

### In-sample global calibration

Shows that one global pair of `c,d` coefficients can represent the complete current calibration population with slightly lower in-sample error than the reconstructed regime-specific SINTEF Equation-6 reference.

### Predictive validation

Shows how the same modelling structure behaves when the target oil has not participated in the `c,d` calibration.

Current evidence indicates:

```text
in-sample global model:
    good empirical representation of the current dataset

leave-one-oil-out:
    moderate degradation
    still meaningful predictive skill
    important oil-dependent heterogeneity remains
```

This is stronger evidence than the previous in-sample comparison alone, but it still does not demonstrate universal full-scale transferability.

---

## 3.8 Known Scientific Limitations

### Experimental-regime structure

The database treats:

```text
2 mm — no gas
3 mm — no gas
2 mm — gas
```

as distinct experimental conditions.

The global `c,d` calibration removes regime dependence from `c,d`, but not from all model parameters.

### `eta` remains condition dependent

The current production formulation still uses different efficiency treatment according to gas condition.

Therefore:

```text
global c,d
≠
fully global SSMD closure
```

### Experimental identifiability limitation

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

Therefore the current campaign cannot independently identify whether:

```text
water flow
water velocity
momentum flux
kinetic power
```

is the fundamental controlling mechanical variable.

### Oil-property identifiability

The leave-one-oil-out result shows that the inferred global property correction is sensitive to the oil population.

Oil `4662` has particularly strong leverage on the fitted `d` coefficient.

This supports further oil-property research but does not justify modifying the production-reference correlation solely to improve fit.

### End-to-end validation limitation

The current leave-one-oil-out workflow validates the SSMD `dR` calibration.

A fully independent end-to-end unseen-oil validation would require:

```text
held-out oil
    excluded from SSDI calibration
and
    excluded from SSMD calibration
```

before evaluating:

```text
d50_treated_pred
```

That stricter validation has not been claimed by this milestone.

### Full-scale limitation

No universal mapping from arbitrary full-scale operating conditions to all SSMD model parameters has yet been validated.

Exploratory correlation development remains tracked separately in:

```text
RESEARCH_SSMD_UPSCALING_UPDATED.md
```

---

## 3.9 Current SSMD Architecture

The production architecture is:

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
predictive validation
```

The responsibilities remain separated as follows:

```text
upscaling/ssmd/
    production physics
    calibration
    prediction
    model persistence
    modelling workflows

analysis/ssmd/
    model evaluation
    oil-wise diagnostics
    predictive validation
    figures
    reporting
    analysis persistence

analysis/experimental/
    descriptive experimental behaviour

database/
    raw-data interpretation
    normalization

commands/
    CLI dispatch only
```

Exploratory correlation development remains outside the production pipeline.

---

## 3.10 CLI Surface

The SSMD modelling workflows are exposed through:

```bash
upscaling ssmd reference
upscaling ssmd global
upscaling ssmd oil-wise
```

Each modelling workflow can use an explicit persisted SSDI source for the untreated `d50` prediction.

SSMD analysis is exposed through:

```bash
upscaling analyze ssmd performance
upscaling analyze ssmd oil-wise
upscaling analyze ssmd validation
```

The CLI remains a dispatcher.

It does not perform:

```text
DataFrame manipulation
physics
calibration
regression
prediction
metric calculation
plotting
```

directly.

---

## 3.11 Milestone Completion

**Status:** Completed

The original completion criteria are now satisfied for the reconstructed SSMD production workflow.

Completed items:

```text
- normalized SSMD data consumption;
- deterministic experiment linkage;
- treated / untreated pairing;
- SI internal representation;
- derived SSMD physics;
- reconstructed SINTEF Equation 5;
- reconstructed SINTEF Equation 6;
- explicit SSMD model variants;
- by-regime c,d calibration;
- global c,d calibration;
- oil-wise factor diagnostic;
- experiment-level prediction tables;
- model-result persistence;
- model reporting;
- separated analysis/ssmd architecture;
- shared SSMD performance metrics;
- parity / performance evaluation;
- oil-wise heterogeneity analysis;
- leave-one-oil-out predictive validation;
- validation persistence;
- validation reporting;
- validation plotting;
- SSMD experimental-analysis workflow;
- project-wide CLI dispatch.
```

Frozen numerical reference results:

```text
SINTEF Equation 5
Log-MSE = 0.7167120356

SINTEF Equation 6
Log-MSE = 0.1287225708
R²_log  ≈ 0.498

Global c,d — in sample
Log-MSE = 0.115841
R²_log  = 0.547970

Global c,d — leave-one-oil-out
Log-MSE = 0.142664
R²_log  = 0.443304

LOO Log-MSE degradation relative to in sample
+23.154704 %
```

The milestone is considered complete because the production-reference reconstruction, statistical evaluation, diagnostic analysis, and current predictive-validation scope are now explicit and reproducible.

Remaining research questions are not blockers for Milestone 3.

They include:

```text
- identifying more transferable oil-property descriptors;
- evaluating alternative SSMD correlations;
- reducing dependence on condition-specific eta;
- determining whether momentum flux or another water-jet variable is the fundamental mechanical descriptor;
- constructing a fully independent SSDI + SSMD unseen-oil end-to-end validation;
- assessing full-scale transferability.
```

These belong to future research rather than to reconstruction of the existing SSMD pipeline.

---

## Subsequent Milestone

Milestone 3 is closed.

The droplet-size distribution workflow that followed this milestone has now been reconstructed and stabilized as:

```text
Milestone 4 — Droplet-Size Distribution Analysis
Status: Completed
```

The stable distribution implementation consumes `data/database/distributions.xlsx`, fits the Rosin–Rammler CDF at the original measured droplet diameters, persists `shape` and `scale`, and evaluates fit quality separately in `analysis/distributions/`.

Future SSMD correlation research remains separated from both the production SSMD workflow and the stable distribution workflow.
