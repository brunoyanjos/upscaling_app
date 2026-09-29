# Milestone 2 — SSDI Pipeline Reconstruction

**Status:** Completed — architecture stabilized and validation extended

## Objective

Reconstruct the SSDI modelling workflow on top of the normalized database architecture established in Milestone 1 while preserving the validated physical formulation and explicitly separating:

```text
data selection
    ↓
derived physics
    ↓
physical model
    ↓
calibration
    ↓
prediction
    ↓
persistence
    ↓
statistical analysis
    ↓
sensitivity analysis
    ↓
predictive validation
```

The reconstructed SSDI workflow consumes only normalized databases and does not access the original raw experimental spreadsheets.

The milestone also establishes explicit model versions, reproducible persistence, modular statistical analyses, grouped predictive validation, and a stable CLI surface.

---

## 2.1 Current Architecture

### Modelling

The production SSDI implementation is organized under:

```text
src/upscaling_app/upscaling/ssdi/
├── calibration/
│   ├── __init__.py
│   ├── initial_guess.py
│   ├── optimization.py
│   ├── preparation.py
│   └── pipeline.py
├── io/
│   ├── __init__.py
│   ├── data.py
│   └── persistence.py
├── physics/
│   ├── __init__.py
│   ├── derived_properties.py
│   └── model.py
├── workflows/
│   ├── __init__.py
│   ├── baseline.py
│   └── oil_wise.py
├── datasets.py
├── prediction.py
├── reporting.py
├── results.py
└── versions.py
```

The production modelling layer therefore contains only genuine modelling workflows:

```text
baseline
oil-wise calibration
```

Outlier removal and oil-exclusion studies are no longer implemented as production modelling workflows. They belong to the statistical sensitivity-analysis layer.

### Statistical analysis

The SSDI analysis architecture is organized by scientific question:

```text
src/upscaling_app/analysis/ssdi/
├── comparison/
│   ├── analysis.py
│   ├── pipeline.py
│   ├── plotting.py
│   ├── persistence.py
│   └── reporting.py
├── io/
│   └── data.py
├── oil_wise/
│   ├── analysis.py
│   ├── pipeline.py
│   ├── plotting.py
│   ├── persistence.py
│   └── reporting.py
├── performance/
│   ├── analysis.py
│   ├── pipeline.py
│   ├── plotting.py
│   ├── persistence.py
│   └── reporting.py
├── sensitivity/
│   ├── analysis.py
│   ├── pipeline.py
│   ├── plotting.py
│   ├── persistence.py
│   └── reporting.py
├── validation/
│   ├── analysis.py
│   ├── pipeline.py
│   ├── plotting.py
│   ├── persistence.py
│   └── reporting.py
├── metrics.py
├── outliers.py
└── populations.py
```

The previous generic `evaluation/` layer and root-level SSDI plotting, reporting, and persistence modules were removed after their responsibilities were migrated into the question-specific analysis modules.

The analysis convention is:

```text
analysis.py
    scientific/statistical calculations

pipeline.py
    orchestration and result objects

plotting.py
    visualization only

persistence.py
    analysis-output persistence

reporting.py
    terminal presentation only

cli.py
    workflow dispatch only
```

---

## 2.2 Normalized Data Consumption

The SSDI workflow consumes normalized experiments from:

```text
data/database/experiments.xlsx
```

Dataset selection uses normalized fields including:

```text
experiment_id
oil_id
dispersion_kind
dispersion_tag
nozzle_diameter
has_gas
measured_d50
```

Raw spreadsheet naming conventions and unit conversion remain confined to the database layer.

The SSDI calibration population currently contains:

```text
10 oils
90 experiments
```

covering untreated and SSDI experiments at the selected 2 mm and 3 mm release conditions.

Internal physical quantities use SI units.

---

## 2.3 Shared SSDI Dataset Definitions

Shared SSDI population definitions are separated from individual workflows.

The production modelling population includes:

```text
3014
3015
3016
4661
4662
4663
4664
4665
4666
4667
```

The analysis layer additionally defines diagnostic populations for sensitivity and validation.

### Residual-sensitivity oils

```text
3016
4665
```

These oils contain the strongest systematic baseline residual anomalies and all baseline IQR outliers.

### Extended sensitivity oils

```text
3016
4662
4665
```

Oil `4662` was added after complementary diagnostics showed atypical behaviour despite the absence of baseline IQR outliers.

### Retained population

```text
3014
3015
4661
4663
4664
4666
4667
```

This seven-oil population is used for the extended oil sensitivity, conditional leave-one-oil-out validation, and excluded-oil challenge.

---

## 2.4 Derived Physical Properties

The SSDI physical preprocessing remains isolated in:

```text
upscaling/ssdi/physics/derived_properties.py
```

The reconstructed workflow evaluates the physical quantities required by the validated SSDI formulation, including:

```text
void fraction
mixed density
volumetric velocity
modified velocity
reduced gravity
Froude number
effective velocity
Reynolds number
Weber number
Capillary number
```

The physical preprocessing was not modified during the architectural reorganization.

---

## 2.5 SSDI Correlation

The iterative SSDI model remains implemented in:

```text
upscaling/ssdi/physics/model.py
```

The normalized droplet diameter is evaluated using the established Weber-Capillary formulation with fitted coefficients:

```text
A
B
```

The correlation is solved iteratively for:

```text
d50 / D
```

The physical formulation remains unchanged relative to the reconstructed reference workflow.

---

## 2.6 Calibration

Calibration remains separated into:

```text
preparation.py
    prepare experimental arrays

initial_guess.py
    grid search for A0 and B0

optimization.py
    objective and numerical optimization

pipeline.py
    calibration orchestration
```

The objective is:

```text
Log-MSE =
mean(
    [log(d50/D)_exp - log(d50/D)_pred]^2
)
```

The global baseline uses:

```text
JAX gradients
+
L-BFGS-B
```

The oil-wise workflow retains its dedicated numerical strategy where required.

Numerical solver and optimizer information are persisted with calibration results.

---

## 2.7 Prediction and Model Versions

Prediction remains separate from calibration.

Experiment-level prediction tables contain explicit model identities and quantities such as:

```text
experiment_id
model_version
a_coef
b_coef
d50_D_exp
d50_D_pred
d50_exp
d50_pred
```

Current SSDI model versions include:

```text
jax_baseline_all
sintef_baseline
jax_oil_wise
jax_filtered_iqr
jax_exclude_3016_4665
jax_exclude_3016_4662_4665
```

The explicit model identifier allows several calibration strategies to coexist in the same persisted prediction table.

---

## 2.8 Result Persistence

The SSDI result hierarchy is now:

```text
data/results/ssdi/
├── predictions.xlsx
├── calibrations.xlsx
├── performance/
│   ├── results.xlsx
│   └── figures/
├── sensitivity/
│   ├── results.xlsx
│   └── figures/
├── oil_wise/
│   ├── results.xlsx
│   └── figures/
├── comparison/
│   ├── results.xlsx
│   └── figures/
└── validation/
    ├── results.xlsx
    └── figures/
```

### Primary modelling outputs

```text
predictions.xlsx
calibrations.xlsx
```

These files represent the contract between modelling and downstream analysis.

Re-running a model version replaces records associated with that version rather than creating duplicate model records.

### Analysis outputs

Analysis results are partitioned by scientific workflow rather than written as unrelated Excel files in the root results directory.

Relevant tables are grouped into workbook sheets whenever they belong to the same scientific analysis.

---

## 2.9 Baseline Calibration

The complete 90-experiment SSDI population reproduces the validated baseline.

Reference result:

```text
experiments          90

initial A            29.000000
initial B             0.024865

optimized A          25.839498
optimized B           0.062071

Log-MSE               0.426986
```

SINTEF reference coefficients:

```text
A                     24.600000
B                      0.080000

Log-MSE                0.435997
```

The recalibrated baseline therefore reduces the calibration Log-MSE by approximately:

```text
2.07 %
```

relative to the reconstructed SINTEF coefficients.

This is an in-sample calibration comparison.

---

## 2.10 Oil-Wise Calibration

The oil-wise workflow independently calibrates `A,B` for each oil.

```text
10 oils
9 experiments per oil
90 predictions
```

Oil-wise calibrations and predictions are persisted using the same modelling contracts as the global baseline.

The analysis compares:

```text
global A,B
vs.
oil-specific A,B
```

and reports:

```text
oil-level coefficients
oil-level Log-MSE
global versus oil-wise error
coefficient variability
```

The oil-wise workflow is interpreted as a heterogeneity diagnostic.

Because coefficients are calibrated and evaluated using the same oil-specific observations, improved oil-wise performance does not constitute predictive validation.

---

## 2.11 Performance Analysis

Standard model performance is evaluated independently from calibration.

The performance workflow currently supports:

```text
global calibrated baseline
SINTEF reference
```

Metrics include:

```text
Log-MSE
R²
RMSE
MAPE
mean logarithmic residual
standard deviation of logarithmic residual
IQR outlier count
```

Oil-level diagnostics include:

```text
experiment count
Log-MSE
R²
RMSE
MAPE
mean logarithmic residual
standard deviation of logarithmic residual
outlier count
```

The logarithmic residual convention is:

```text
log_residual =
log(d50_exp) - log(d50_pred)
```

Therefore:

```text
log_residual > 0
    model underpredicts d50

log_residual < 0
    model overpredicts d50
```

---

## 2.12 Sensitivity Analysis

Sensitivity analyses are explicitly separated from production calibration and predictive validation.

Three progressively stronger diagnostic selections are evaluated.

### IQR sensitivity

Baseline residuals are screened with the standard IQR criterion:

```text
Q1 - 1.5 IQR
Q3 + 1.5 IQR
```

Six observations are removed.

Reference result:

```text
experiments          84

optimized A          27.999982
optimized B           0.053212

Log-MSE               0.242571
R²                     0.765864
RMSE                   0.406 mm
MAPE                  41.09 %
```

This answers:

> How strongly does the global calibration depend on individually extreme residual observations?

### Oil-residual sensitivity

Oils:

```text
3016
4665
```

are removed completely.

Reference population:

```text
72 experiments
8 oils
```

Reference result:

```text
optimized A          25.897184
optimized B           0.059223

Log-MSE               0.186215
R²                     0.806854
RMSE                   0.357 mm
MAPE                  36.01 %
```

This answers:

> How strongly does the global calibration depend on the oils containing the strongest systematic residual anomalies?

### Extended oil sensitivity

The exclusion is extended to:

```text
3016
4662
4665
```

leaving:

```text
7 oils
63 experiments
```

The retained-population calibration gives approximately:

```text
A                     26.044664
B                      0.062413
training Log-MSE       0.153634
```

This answers:

> How strongly does the calibration depend on the broader set of oils identified as atypical across multiple diagnostics?

All three studies remain in-sample sensitivity analyses.

A lower error after removing observations or oils must not be interpreted as evidence of improved generalization.

---

## 2.13 Model Comparison

A separate comparison workflow evaluates the persisted SSDI model versions through the same statistical implementation.

The comparison includes:

```text
SINTEF reference
global baseline
IQR sensitivity
oil-residual sensitivity
extended oil sensitivity
oil-wise calibration
```

The comparison records explicitly:

```text
model_version
analysis_type
population
n
Log-MSE
R²
RMSE
MAPE
mean logarithmic residual
standard deviation of logarithmic residual
```

Because several models are evaluated on different populations, the comparison is diagnostic rather than a model ranking.

---

## 2.14 Predictive Validation

Predictive validation remains separated from calibration and sensitivity analysis.

The validation module now contains three complementary workflows.

### LOO — complete population

For each of the ten oils:

```text
hold out 1 oil
        ↓
calibrate on remaining 9 oils
        ↓
predict held-out oil
        ↓
repeat for all oils
```

The validation contains:

```text
folds            10
predictions      90
```

Current pooled out-of-oil result:

```text
Log-MSE             0.482101
R²                   0.653092
RMSE                 0.4842 mm
MAPE                62.47 %
mean log residual   -0.000279
std log residual     0.698225
```

Representative difficult folds include:

```text
oil     test Log-MSE

3016        1.555200
4662        0.435411
4665        1.662991
```

The complete-population LOO remains the primary cross-oil validation of the reconstructed SSDI model within the current experimental campaign.

### LOO — retained population

A second grouped LOO analysis is performed only on:

```text
3014
3015
4661
4663
4664
4666
4667
```

For each fold:

```text
train = 6 retained oils
test  = 1 retained oil
```

The validation contains:

```text
folds            7
predictions      63
```

Current pooled result:

```text
Log-MSE             0.171652
R²                   0.890838
RMSE                 0.2497 mm
MAPE                33.40 %
mean log residual   -0.001354
std log residual     0.417635
```

The strong reduction in out-of-oil error relative to the complete population indicates that the SSDI correlation behaves considerably more consistently within the retained seven-oil population.

This result is interpreted as:

```text
conditional out-of-oil validation
```

because the retained population was defined after diagnostic inspection of the complete dataset.

It is not external validation.

### Excluded-oil challenge

The model is calibrated using the seven retained oils:

```text
training oils:
3014
3015
4661
4663
4664
4666
4667
```

and then applied to:

```text
challenge oils:
3016
4662
4665
```

Calibration:

```text
training n            63
challenge n           27

A                     26.044664
B                      0.062413
training Log-MSE       0.153634
```

Challenge performance:

```text
pooled Log-MSE         1.065281
R²                     0.209415
RMSE                   0.7586 mm
MAPE                 121.68 %
```

Oil-level challenge Log-MSE:

```text
3016        1.395997
4662        0.424261
4665        1.375585
```

The excluded-oil challenge demonstrates that coefficients calibrated on the retained population do not transfer well to the three diagnostically atypical oils.

This is a diagnostic challenge set rather than independent validation, because the challenge oils were selected using prior analysis of the same experimental campaign.

---

## 2.15 Validation Interpretation

The combined validation results establish a clearer separation between two behaviours.

```text
complete population
    LOO Log-MSE ≈ 0.482

retained population
    LOO Log-MSE ≈ 0.172

excluded-oil challenge
    Log-MSE ≈ 1.065
```

Therefore:

```text
1. The large improvement obtained after excluding the three atypical
   oils is not limited to in-sample calibration.

2. Cross-oil predictive performance also improves substantially within
   the retained seven-oil population.

3. The three excluded oils remain poorly represented when predicted
   from coefficients learned only from the retained oils.

4. Oil-dependent behaviour therefore remains an important unresolved
   component of the SSDI correlation.
```

These findings motivate future oil-property correlation research but do not modify the validated production SSDI formulation.

---

## 2.16 Validation Comparison

The validation module provides a dedicated comparison among:

```text
LOO — all oils
LOO — retained oils
excluded-oil challenge
```

The comparison records:

```text
evaluation type
population
n
Log-MSE
R²
RMSE
MAPE
mean logarithmic residual
standard deviation of logarithmic residual
```

The three results must not be interpreted as equivalent validation populations.

Their intended interpretations are:

```text
LOO all
    cross-oil generalization over the complete campaign

LOO retained
    conditional cross-oil generalization within the retained population

excluded challenge
    diagnostic transfer test to previously identified atypical oils
```

---

## 2.17 Plotting Convention

SSDI parity plots use a consistent scientific visual language.

Treatment is encoded by colour:

```text
Untreated       petroleum / dark neutral
C9500           orange
IBC             yellow
```

Nozzle diameter is encoded by marker:

```text
2 mm            circle
3 mm            square
```

The identity line is shown in light gray.

Parity plots:

```text
use logarithmic axes
use identical physical units
preserve y = x
omit figure titles intended for captions
```

Statistical/model-comparison plots use neutral gray tones rather than treatment colours.

---

## 2.18 CLI

The CLI is now based on hierarchical subcommands rather than mutually exclusive workflow flags.

### SSDI modelling

```bash
upscaling ssdi baseline
upscaling ssdi oil-wise
```

### SSDI performance

```bash
upscaling analyze ssdi performance baseline
upscaling analyze ssdi performance reference
```

### Sensitivity

```bash
upscaling analyze ssdi sensitivity iqr
upscaling analyze ssdi sensitivity oil-residual
upscaling analyze ssdi sensitivity oil-extended
```

### Oil-wise analysis

```bash
upscaling analyze ssdi oil-wise
```

### Model comparison

```bash
upscaling analyze ssdi compare
```

### Predictive validation

```bash
upscaling analyze ssdi validation loo-all
upscaling analyze ssdi validation loo-retained
upscaling analyze ssdi validation excluded-challenge
upscaling analyze ssdi validation compare
```

The CLI acts only as a dispatcher.

Scientific calculations, persistence, plotting, and reporting remain inside their corresponding modules.

---

## 2.19 Architectural Decisions

The finalized SSDI architecture follows these rules:

1. Raw spreadsheets are interpreted only by the database layer.
2. SSDI modelling consumes normalized databases.
3. Internal physical units remain SI whenever applicable.
4. SSDI physical equations remain separate from data access.
5. Calibration remains separate from prediction.
6. Modelling outputs are persisted before downstream statistical analysis.
7. `model_version` explicitly identifies persisted predictions.
8. Production modelling workflows contain only genuine modelling operations.
9. Observation removal and oil exclusion are sensitivity analyses.
10. Sensitivity analysis is distinct from predictive validation.
11. Oil-wise calibration is a heterogeneity diagnostic rather than predictive validation.
12. LOO validation uses complete oil groups rather than experiment-level random splitting.
13. Reduced-population LOO is interpreted conditionally because the population was selected from prior diagnostics.
14. The excluded-oil challenge is diagnostic rather than independent validation.
15. Statistical modules are organized by scientific question.
16. Plotting functions consume already-calculated results.
17. Reporting functions do not perform scientific calculations.
18. Persistence is partitioned by workflow.
19. CLI commands dispatch workflows but do not implement scientific logic.
20. Exploratory correlation development remains separated from the reconstructed SSDI production pipeline.

---

## 2.20 Known Limitations

The current SSDI workflow remains subject to the following limitations:

```text
- only ten oils are available;
- oil-level diagnostics therefore have limited sample size;
- no independent external experimental dataset is available;
- the retained seven-oil population was defined using diagnostics from
  the same campaign;
- LOO evaluates generalization to unseen oils within the campaign, not
  to arbitrary external oils;
- the three excluded oils cannot be treated as an independent test set
  because their selection was data informed;
- MAPE is sensitive to small experimental d50 values;
- dataset and optimizer settings are not yet fully externalized through
  configuration files;
- unexplained oil-dependent behaviour remains in the SSDI response.
```

Logarithmic error, RMSE, MAPE, residual direction, and oil-level heterogeneity should therefore be interpreted jointly.

---

## 2.21 Reproducibility Reference

The main numerical fingerprints of the finalized SSDI reconstruction are:

```text
Global baseline
    n           = 90
    A           = 25.839498
    B           = 0.062071
    Log-MSE     = 0.426986

SINTEF reference
    A           = 24.600000
    B           = 0.080000
    Log-MSE     = 0.435997

IQR sensitivity
    n           = 84
    Log-MSE     = 0.242571

Oil-residual sensitivity
    n           = 72
    Log-MSE     = 0.186215

Extended oil sensitivity
    n           = 63
    A           = 26.044664
    B           = 0.062413
    Log-MSE     = 0.153634

LOO — all oils
    folds       = 10
    n           = 90
    Log-MSE     = 0.482101
    R²          = 0.653092
    RMSE        = 0.4842 mm
    MAPE        = 62.47 %

LOO — retained oils
    folds       = 7
    n           = 63
    Log-MSE     = 0.171652
    R²          = 0.890838
    RMSE        = 0.2497 mm
    MAPE        = 33.40 %

Excluded-oil challenge
    n           = 27
    Log-MSE     = 1.065281
    R²          = 0.209415
    RMSE        = 0.7586 mm
    MAPE        = 121.68 %
```

These values should be used as regression fingerprints when future structural changes are introduced.

---

## 2.22 Result

The SSDI reconstruction is considered completed and architecturally stabilized.

The workflow now provides:

```text
normalized database consumption
        +
validated SSDI physical preprocessing
        +
reproducible global calibration
        +
explicit model versions
        +
persisted predictions and calibrations
        +
oil-wise calibration
        +
standard model performance analysis
        +
progressive sensitivity analysis
        +
model comparison
        +
complete-population LOO validation
        +
retained-population LOO validation
        +
excluded-oil challenge analysis
```

The reconstructed production model remains unchanged physically.

The extended validation results provide evidence that the current SSDI correlation is substantially more transferable within a seven-oil subpopulation, while oils `3016`, `4662`, and `4665` exhibit behaviour that is not adequately represented by coefficients calibrated on the remaining oils.

This unresolved oil dependence belongs to future correlation-development research rather than to the production SSDI reconstruction.

---

## Next Milestone

**Milestone 3 — SSMD Pipeline Reconstruction**

The SSMD workflow consumes persisted SSDI predictions where untreated reference predictions are required and remains architecturally separate from SSDI calibration and statistical analysis.
