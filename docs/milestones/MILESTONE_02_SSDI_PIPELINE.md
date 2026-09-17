# Milestone 2 — SSDI Pipeline Reconstruction

**Status:** Completed

## Objective

Reconstruct the SSDI modelling workflow on top of the normalized database architecture established in Milestone 1, preserving the validated physical formulation while separating data access, derived physical properties, calibration, prediction, persistence, statistical analysis, and predictive validation.

## Completed work

### SSDI package architecture

The SSDI implementation was moved into reusable package modules under:

```text
src/upscaling_app/
├── upscaling/
│   └── ssdi/
│       ├── calibration/
│       │   ├── initial_guess.py
│       │   ├── optimization.py
│       │   ├── preparation.py
│       │   └── pipeline.py
│       ├── io/
│       │   ├── data.py
│       │   └── persistence.py
│       ├── physics/
│       │   ├── derived_properties.py
│       │   └── model.py
│       ├── workflows/
│       │   ├── baseline.py
│       │   ├── filtered.py
│       │   └── oil_sensitivity.py
│       ├── prediction.py
│       ├── reporting.py
│       ├── results.py
│       └── versions.py
│
└── analysis/
    └── ssdi/
        ├── evaluation/
        │   ├── comparison.py
        │   ├── leave_one_oil_out.py
        │   └── oil_analysis.py
        ├── io/
        │   ├── data.py
        │   └── persistence.py
        ├── metrics.py
        ├── outliers.py
        ├── pipeline.py
        ├── plotting.py
        └── reporting.py
```

The implementation no longer depends on numbered analysis scripts to execute the SSDI workflow.

### Normalized data consumption

The SSDI pipeline reads experimental conditions from the normalized experiment database rather than from the original raw spreadsheets.

Dataset selection is based on normalized fields such as:

```text
oil_id
nozzle_diameter
dispersion_kind
experiment_id
```

Raw naming conventions and unit conversions therefore remain confined to the database layer.

### Derived physical properties

The physical preprocessing required by the SSDI correlation was isolated in `physics/derived_properties.py`.

The reconstructed workflow evaluates the same derived quantities used by the validated legacy implementation, including:

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

The existing physical formulation was preserved during the reconstruction.

### SSDI correlation

The iterative SSDI correlation is implemented in `physics/model.py` using JAX.

The model evaluates the normalized droplet diameter through the existing iterative formulation based on Weber and Capillary numbers and the fitted coefficients `A` and `B`.

JAX-specific model logic remains inside the scientific layer rather than the CLI.

### Calibration pipeline

Calibration is separated into four responsibilities:

```text
preparation.py       experimental arrays used by the optimizer
initial_guess.py     grid search for initial A and B
optimization.py      objective function and L-BFGS-B optimization
pipeline.py          calibration orchestration
```

The calibration objective is the mean squared logarithmic error:

```text
mean((log(d50/D)_exp - log(d50/D)_pred)^2)
```

Gradient evaluation uses JAX through `jax.value_and_grad`, while the final coefficient optimization uses L-BFGS-B.

The legacy grid-search strategy for the initial coefficients was preserved so that the reconstructed implementation could be checked against the previous results.

### Prediction pipeline

Prediction is separated from calibration.

`prediction.py` produces experiment-level outputs including:

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

This allows the same statistical analysis pipeline to operate on multiple SSDI calibration strategies.

### Model versions

Named model versions are centralized in `versions.py`.

Current versions include:

```text
jax_baseline_all
jax_filtered_iqr
jax_exclude_3016_4665
sintef_baseline
```

The model identifier is persisted with each prediction so that analyses do not depend on implicit file context.

### Baseline workflow

The baseline SSDI workflow uses the complete selected dataset and reproduces the previous validated calibration.

Reference result:

```text
experiments          90
initial A            29.000000
initial B             0.0248649
optimized A          25.839500
optimized B           0.0620713
Log-MSE               0.426986
```

The SINTEF reference coefficients are also evaluated through the same objective function:

```text
A                     24.6
B                      0.08
Log-MSE                0.435997
```

The optimized baseline therefore reproduces the legacy implementation while slightly reducing the calibration objective relative to the reference coefficients.

### IQR-filtered workflow

Residual analysis is performed using the directional logarithmic residual:

```text
log(d50_exp) - log(d50_pred)
```

Outliers are identified using the standard IQR rule:

```text
Q1 - 1.5 IQR
Q3 + 1.5 IQR
```

The filtered workflow removes baseline IQR outliers by deterministic `experiment_id` and recalibrates the model on the remaining experiments.

Reference result:

```text
experiments          84
optimized A          27.999982
optimized B           0.053212
Log-MSE               0.242571
R²                     0.765864
RMSE                   4.06e-04 m
MAPE                  41.09 %
```

This workflow is treated as an outlier-sensitivity calibration rather than independent predictive validation.

### Oil-level sensitivity workflow

Oil-level residual diagnostics identified oils `3016` and `4665` as having pronounced systematic disagreement with the baseline correlation.

A dedicated sensitivity workflow recalibrates the model after excluding both oils.

Reference result:

```text
experiments          72
optimized A          25.897184
optimized B           0.059223
Log-MSE               0.186215
R²                     0.806854
RMSE                   3.57e-04 m
MAPE                  36.01 %
```

The result is explicitly interpreted as a subset sensitivity study. Improved in-sample metrics after removing oils are not treated as independent evidence of improved predictive performance.

### Statistical analysis

Statistical analysis is isolated under `analysis/ssdi/`.

The standard model-analysis pipeline calculates:

```text
R²
RMSE
MAPE
absolute percentage error
logarithmic residual
IQR outlier status
```

The previous metric labelled `AAD` was replaced by `MAPE` because the implemented expression is the mean absolute percentage error.

Oil-level diagnostic statistics include:

```text
number of experiments
MAPE
RMSE
mean logarithmic residual
standard deviation of logarithmic residual
outlier count
```

The sign convention is:

```text
log residual > 0    model underpredicts d50
log residual < 0    model overpredicts d50
```

### Leave-one-oil-out validation

A grouped leave-one-oil-out validation was implemented to distinguish calibration fit from generalization to unseen oils.

For each oil:

```text
train = all remaining oils
test  = held-out oil
```

With ten oils, ten independent calibration folds are evaluated. Each held-out prediction therefore comes from a calibration that has never seen that oil.

The pooled validation contains all 90 experiments exactly once as out-of-oil predictions.

Global leave-one-oil-out result:

```text
predictions            90
Log-MSE                 0.482962
R²                       0.654276
RMSE                     4.834131e-04 m
MAPE                    62.71 %
mean log residual       -0.002310
std. log residual        0.698844
```

The near-zero pooled mean residual does not imply uniformly small errors. Positive and negative oil-specific biases partially cancel in the aggregate.

The validation identified particularly weak generalization for oils `3016` and `4665`, with reduced performance also observed for `4662`.

Representative held-out results include:

```text
oil    test Log-MSE    R²        RMSE [m]    MAPE [%]
3016      1.563816    -0.241490   9.44e-04      258.61
4662      0.435412    -0.024709   8.02e-04       78.43
4665      1.662951     0.457302   6.07e-04       63.51
```

For oil `3016`, the negative held-out `R²` indicates that the correlation performs worse on those nine observations than a constant predictor based on their experimental mean.

### Calibration versus validation

A separate evaluation comparison is generated so that fundamentally different analyses are not conflated.

Current reference comparison:

```text
model/version             evaluation    n    Log-MSE    R²        MAPE [%]
jax_baseline_all          in_sample     90   0.426986    0.685533   57.96
jax_filtered_iqr          in_sample     84   0.242571    0.765864   41.09
jax_exclude_3016_4665     in_sample     72   0.186215    0.806854   36.01
leave_one_oil_out         out_of_oil    90   0.482962    0.654276   62.71
```

The `evaluation` field is retained explicitly because the filtered and oil-sensitivity workflows are evaluated on their calibration subsets, whereas leave-one-oil-out is predictive validation on held-out oils.

### Plotting

A shared plotting style was introduced under:

```text
src/upscaling_app/plotting/style.py
```

SSDI analysis figures use this common scientific style rather than project-specific plotting fragments.

Current SSDI figures include:

```text
parity plots
leave-one-oil-out Log-MSE by oil
leave-one-oil-out MAPE by oil
leave-one-oil-out mean log residual by oil
```

Parity figures are square, use logarithmic axes where appropriate, omit figure titles intended to be supplied by article captions, and preserve the identity line `y = x`.

### Result persistence

SSDI modelling and analysis outputs are written under:

```text
data/results/
```

Current outputs include:

```text
ssdi_results.xlsx
ssdi_analysis_<model_version>.xlsx
ssdi_oil_metrics_<model_version>.xlsx
ssdi_model_comparison.xlsx
ssdi_leave_one_oil_out.xlsx
ssdi_evaluation_comparison.xlsx
```

The leave-one-oil-out workbook contains separate sheets for:

```text
folds
predictions
global_metrics
```

Generated figures are stored under:

```text
data/results/figures/
```

SSDI result persistence replaces rows belonging to a model version before appending the new result, avoiding duplicated model records when a workflow is rerun.

### JAX memory configuration

JAX GPU preallocation caused unnecessary device-memory allocation during CLI workflows.

The CLI now configures:

```text
XLA_PYTHON_CLIENT_PREALLOCATE=false
```

before importing SSDI/JAX-dependent modules for both modelling and analysis commands.

This disables JAX's default large memory preallocation without changing the SSDI numerical formulation.

### Command-line interface

The SSDI modelling workflows are available through:

```bash
upscaling ssdi
upscaling ssdi baseline
upscaling ssdi filtered
upscaling ssdi oil-sensitivity
```

`upscaling ssdi` defaults to the baseline workflow.

Individual analyses are available through:

```bash
upscaling analyze ssdi
upscaling analyze ssdi --model baseline
upscaling analyze ssdi --model filtered
upscaling analyze ssdi --model reference
upscaling analyze ssdi --model oil-sensitivity
```

The baseline model is used when no explicit model is supplied.

Additional analysis modes are:

```bash
upscaling analyze ssdi --compare
upscaling analyze ssdi --loo
```

`--model`, `--compare`, and `--loo` are mutually exclusive CLI options so that incompatible analysis modes cannot be requested simultaneously.

## Architectural decisions

The following principles were reinforced during this milestone:

1. SSDI workflows consume only normalized databases.
2. Derived physical properties remain separate from data access.
3. The physical SSDI correlation remains separate from calibration logic.
4. Initial-guess search and numerical optimization remain separate operations.
5. Prediction remains separate from coefficient calibration.
6. Statistical analysis does not modify the calibrated physical model.
7. Outlier filtering is treated as sensitivity analysis rather than predictive validation.
8. Oil-level exclusion is treated as sensitivity analysis rather than evidence of generalization.
9. Leave-one-oil-out is used when evaluating generalization to unseen oils.
10. Model versions are explicit and persisted with predictions.
11. Analysis outputs and modelling outputs remain separate responsibilities.
12. JAX-specific implementation details remain outside the CLI.
13. Reusable plotting conventions are shared across scientific analyses.
14. Workflow orchestration is separated from low-level physics and calibration modules.

## Validation against the legacy implementation

The reconstructed baseline reproduces the legacy SSDI workflow for the selected 90 experiments, including:

```text
grid-search initial coefficients
optimized coefficients
logarithmic calibration objective
reference SINTEF coefficients
prediction structure
residual formulation
IQR-based outlier detection
```

This provided the numerical reference required to continue development without changing the validated SSDI formulation during the architectural migration.

## Known limitations and deferred work

The current SSDI architecture is stable, but several improvements remain intentionally deferred:

- experimental selections are still defined by workflow constants rather than configuration files;
- optimizer and grid-search settings are not yet externally configurable;
- no independent external experimental dataset is currently available for validation;
- leave-one-oil-out evaluates generalization across the oils present in the normalized database, not generalization outside the experimental campaign;
- MAPE remains sensitive to experiments with relatively small measured droplet diameters and should therefore be interpreted together with logarithmic error and RMSE.

These limitations do not block completion of the SSDI reconstruction milestone.

## Result

The SSDI workflow has been reconstructed as a reproducible modelling and analysis pipeline built on the normalized database architecture.

The application now provides explicit separation between:

```text
data selection
physical preprocessing
SSDI physics
calibration
prediction
persistence
statistical diagnostics
outlier sensitivity
oil-level sensitivity
predictive validation
```

The baseline legacy result is reproducible, multiple calibration strategies can be compared without overwriting their identity, and leave-one-oil-out validation provides a separate measure of cross-oil generalization.

## Next milestone

**Milestone 3 — SSMD Pipeline Reconstruction**

The next phase should reconstruct the SSMD workflow using the same architectural principles established for SSDI:

```text
normalized database input
data selection
derived physical properties
physical model
calibration
prediction
result persistence
statistical analysis
validation
```

The SSDI implementation should serve as the architectural reference, while SSMD-specific physics and calibration logic remain isolated from the SSDI modules.
