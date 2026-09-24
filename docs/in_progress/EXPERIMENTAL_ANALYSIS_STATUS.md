# Experimental Analysis — Current Status

## Status

**Active exploratory-analysis layer**

This document records the experimental-analysis workflow being developed on top of the normalized Upscaling App databases.

The analysis is intentionally separated from the SSDI and SSMD modelling pipelines.

Its objectives are to:

- characterize the experimental dataset;
- quantify treatment effects;
- compare treatment methods;
- identify variability across oils;
- explore hydrodynamic structure;
- provide physically meaningful motivation for the modelling pipelines;
- generate reproducible figures for technical presentations and future scientific analysis.

It must not modify the validated SSDI or SSMD model equations.

---

# Architecture

Current package:

```text
src/upscaling_app/
└── analysis/
    └── experimental/
        ├── data.py
        ├── descriptive.py
        ├── ssdi.py
        ├── treatment_effect.py
        ├── plotting.py
        ├── pipeline.py
        └── reporting.py
```

Execution is integrated with the application CLI rather than through independent analysis scripts.

The raw spreadsheets remain outside the scientific-analysis layer.

Conceptual data flow:

```text
raw spreadsheets
        ↓
database ingestion
        ↓
normalized databases
        ↓
experimental analysis
        ↓
tables / figures / reports
```

---

# 1. General descriptive analysis

The general experimental pipeline supports selection by:

```text
all
Untreated
SSDI
SSMD
```

Current outputs include:

```text
dataset summary
variable summary
oil summary
experimental-regime summary
Pearson correlation matrix
Spearman correlation matrix
```

The general descriptive layer is useful for dataset inspection but should not replace treatment-specific physical analysis.

---

# 2. Treatment-effect analysis

## Definition

Treatment effectiveness is evaluated by pairing a treated experiment with the corresponding untreated experiment under the same experimental release condition.

The reduction metric is:

```text
reduction_pct =
100 * (1 - measured_d50 / untreated_d50_measured)
```

The pairing structure preserves the appropriate release condition.

---

## Current outputs

The treatment-effect pipeline currently provides:

```text
effects
by_oil
by_method

best
worst

flagged_by_oil
outliers
outlier_diagnostics

water_jet_by_oil
water_jet_by_fraction
water_jet_monotonicity

ssdi_comparison
```

---

## Treatment summary

Observed median reductions by treatment method:

```text
WJ55        ≈ 92.41 %
WJ50        ≈ 90.61 %
SSDI-C9500  ≈ 89.02 %
WJ45        ≈ 89.00 %
WJ40        ≈ 83.72 %
SSDI-IBC    ≈ 83.03 %
```

These are descriptive results for the current experimental campaign.

They should not be interpreted as universal rankings across arbitrary release conditions.

---

## Variability across oils

The treatment analysis shows that response varies substantially between oils.

Important low-response cases identified during the current analysis include:

```text
oil 4662 — SSDI-C9500
oil 4662 — SSDI-IBC
oil 4665 — SSDI-IBC
```

The strongest case is oil `4662` under IBC, where the response is markedly lower than the remainder of the IBC observations.

This variability motivates later model evaluation at the oil level.

---

# 3. Water-jet response

Current water-jet summary:

```text
fraction    median reduction
40 %        ≈ 83.72 %
45 %        ≈ 89.00 %
50 %        ≈ 90.61 %
55 %        ≈ 92.41 %
```

Observed monotonic increase:

```text
7 / 10 oils
```

Current figure:

```text
d50_reduction_water_jet_intensity.png
```

The plot contains:

- individual-oil responses in gray;
- median response across oils as the main line.

## Interpretation

The observed median response increases with water-jet fraction.

However, this should currently be treated as a descriptive result.

Before making a strong causal statement about water-jet intensity, the release-regime structure should be considered because experimental operating conditions may not be fully interchangeable across all fractions.

---

# 4. SSDI dispersant comparison

The current analysis compares:

```text
C9500
IBC
```

on a paired oil basis.

For each oil, the plotted values summarize the response across the tested release conditions.

Current figure:

```text
d50_reduction_ssdi_comparison.png
```

Observed result:

```text
C9500 higher reduction: 10 / 10 oils
```

Examples:

```text
oil 4662:
C9500 ≈ 72.04 %
IBC   ≈ 43.50 %

oil 4665:
C9500 ≈ 81.11 %
IBC   ≈ 71.40 %
```

The dumbbell plot should be interpreted as a paired C9500-vs-IBC comparison, not simply as a best-vs-worst plot.

---

# 5. SSDI experimental physics

The experimental SSDI analysis now reuses the same physical preprocessing used by the validated SSDI modelling workflow.

This was an important correction.

The initial exploratory implementation had used:

```text
velocity = oil_flow / nozzle_area
```

which did not match the reconstructed SSDI model.

The corrected analysis calls the validated SSDI physical preprocessing.

Derived quantities include:

```text
void_fraction
mixed_density
volumetric_velocity
modified_velocity
reduced_gravity
froude
effective_velocity
reynolds
weber
capillary
```

The physical chain is:

```text
oil + gas flow
        ↓
mixture properties
        ↓
volumetric velocity
        ↓
modified velocity
        ↓
reduced gravity
        ↓
Froude number
        ↓
effective velocity
        ↓
Re / We / Ca
```

This ensures that experimental diagnostics and production SSDI modelling use consistent physical definitions.

---

# 6. Normalized droplet diameter

The primary dimensionless response is:

```text
d50_D = measured_d50 / nozzle_diameter
```

This response is used in:

- hydrodynamic scatter plots;
- log-log exploratory regression;
- Spearman screening;
- the SSDI model-analysis narrative.

---

# 7. Modified Weber diagnostic

Current experimental definition:

```text
modified_weber =
weber /
(
    1
    + B
    * capillary
    * d50_D^(1/3)
)
```

with:

```text
B = 0.08
```

`B = 0.08` is the SINTEF reference coefficient.

## Important limitation

`modified_weber` contains `d50_D` in its own definition.

Therefore:

- it is useful for examining consistency with the established correlation structure;
- it is not an independent predictor of `d50_D`;
- correlation between `modified_weber` and `d50_D` must not be presented as independent predictive evidence;
- it must not be included in the hydrodynamic variable-screening ranking used to select independent candidate quantities.

---

# 8. Log-log exploratory relations

The analysis currently supports:

```text
d50/D vs Weber
d50/D vs Capillary
d50/D vs modified Weber
```

for:

```text
pooled
SSDI-only
```

Regression outputs:

```text
n
slope
intercept
R²_log
```

## Previous diagnostic result

A previous run showed substantially stronger relationships when `Untreated` and `SSDI` experiments were pooled than within SSDI alone.

That result demonstrated the importance of separating:

```text
between-regime contrast
```

from:

```text
within-SSDI variation
```

However, those values should no longer be treated as final because the exploratory preparation was subsequently found to exclude gas cases.

---

# 9. Important dataset correction

The previous experimental preparation function contained:

```python
include_gas=False
```

and therefore filtered:

```text
has_gas == False
```

before generating the exploratory plots.

Consequently, the previous:

```text
pooled log-log plots
SSDI-only log-log plots
Spearman screening
```

did not use the intended complete dataset.

This is currently the main pending correction.

## Required change

The experimental preparation step should no longer silently exclude gas cases.

Preferred design:

```python
prepare_ssdi_experimental_data(data)
```

should perform only:

```text
Untreated + SSDI selection
physical preprocessing
d50/D calculation
modified-Weber diagnostic calculation
```

If a future analysis specifically requires `no_gas`, that filter should be applied explicitly in the analysis pipeline.

This avoids hidden scientific selection criteria.

---

# 10. Spearman hydrodynamic screening

A dedicated screening function has been introduced.

Candidate variables:

```text
volumetric_velocity
modified_velocity
effective_velocity
froude
reynolds
weber
capillary
```

Response:

```text
d50/D
```

Statistic:

```text
Spearman rank correlation, rho_s
```

The function reports:

```text
variable
n
spearman_rho
abs_spearman_rho
```

and sorts the variables by absolute Spearman correlation.

## Intended use

The screening is exploratory.

It should answer:

> Which hydrodynamic quantities show the strongest marginal monotonic association with the measured normalized droplet diameter?

It should not be interpreted as:

> Which variable causes the droplet-size response?

Hydrodynamic quantities are mathematically and physically coupled.

For example:

```text
We = Re * Ca
```

under their classical definitions.

Therefore, marginal correlation coefficients cannot be treated as independent effect sizes.

---

## Current implementation decision

The latest intended version of the Spearman screening uses all records supplied to the function rather than internally applying:

```text
dispersion_kind == SSDI
```

This permits screening of the complete prepared:

```text
Untreated + SSDI
```

dataset.

The exact scope must always be stated in the presentation or report.

If pooled data are used, the resulting correlation can reflect both:

- variation within a treatment regime;
- separation between Untreated and SSDI regimes.

---

# 11. Current experimental figures

Treatment-effect figures:

```text
d50_reduction_by_method.png
d50_reduction_variability.png
d50_reduction_extremes.png
d50_reduction_water_jet_intensity.png
d50_reduction_ssdi_comparison.png
```

SSDI exploratory figures:

```text
ssdi_spearman_screening.png

pooled/
    d50D_vs_weber.png
    d50D_vs_capillary.png
    d50D_vs_modified_weber.png

ssdi_only/
    d50D_vs_weber.png
    d50D_vs_capillary.png
    d50D_vs_modified_weber.png
```

The SSDI exploratory figures must be regenerated after correcting the gas-selection behaviour.

---

# 12. Current pipeline result objects

## General analysis

```python
ExperimentalAnalysisResult
```

contains:

```text
data
dataset_summary
variable_summary
oil_summary
regime_summary
pearson
spearman
```

## SSDI experimental analysis

```python
SSDIExperimentalResult
```

contains:

```text
pooled
ssdi_only
relation_summary
spearman_summary
```

## Treatment-effect analysis

```python
TreatmentEffectResult
```

contains:

```text
effects
by_oil
by_method

best
worst

flagged_by_oil
outliers
outlier_diagnostics

water_jet_by_oil
water_jet_by_fraction
water_jet_monotonicity

ssdi_comparison
```

---

# 13. Reporting

The reporting layer prints the experimental outputs in separate sections.

For SSDI experimental analysis:

```text
SSDI EXPERIMENTAL ANALYSIS

Modified Weber reference coefficient
Experiments
Hydrodynamic Spearman screening
Log-log relations
```

For treatment-effect analysis:

```text
BY METHOD
TOP 5 RESPONSES
BOTTOM 5 RESPONSES
OUTLIERS
OUTLIER DIAGNOSTICS
WATER-JET RESPONSE
SSDI DISPERSANT COMPARISON
```

---

# 14. Scientific interpretation rules

The following distinctions should be preserved as the analysis grows.

## Association is not causation

Spearman, Pearson, and univariate regressions describe statistical association.

They do not independently establish physical causality.

---

## Pooled effects can reflect regime separation

Combining:

```text
Untreated + SSDI
```

can produce strong correlations simply because the two regimes occupy different regions of the experimental space.

Therefore, pooled analyses should be described as global experimental structure rather than within-SSDI effects.

---

## Modified Weber is not independent

Because the current experimental `modified_weber` contains `d50/D`, it cannot be used as an independent validation variable.

---

## Oil-level properties require oil-level statistical care

Repeated experiments on one oil do not create independent observations of an oil property.

Future analyses of viscosity, composition, wax, asphaltenes, etc. must account for clustering by `oil_id`.

---

## Experimental analysis must remain separate from model modification

This package may identify:

- unexplained variation;
- systematic residual behaviour;
- candidate physical mechanisms.

It should not silently modify the validated SSDI or SSMD equations.

Correlation-development work remains a separate future research pipeline.

---

# Next-session action plan

## 1. Correct the SSDI experimental preparation

Remove the implicit gas exclusion.

Confirm that the prepared dataset contains the intended:

```text
Untreated
SSDI
gas
no-gas
```

records.

Print counts before running analyses.

---

## 2. Regenerate Spearman screening

Generate the corrected table:

```text
variable
n
spearman_rho
```

Check:

- total `n`;
- signs;
- ranking;
- whether strong coefficients are driven by pooled regime separation.

---

## 3. Regenerate log-log plots

Recompute:

```text
pooled
SSDI-only
```

for:

```text
We
Ca
We*
```

These are diagnostic outputs.

Only plots that directly support the presentation narrative should be retained in the main slide deck.

---

## 4. Decide presentation usage

Likely presentation flow:

```text
treatment-effect observations
        ↓
hydrodynamic screening
        ↓
established SSDI physical formulation
```

The Spearman figure may replace several individual exploratory scatter plots if it communicates the motivation more clearly.

---

## 5. Optional persistence improvement

Consider persisting compact numerical summaries such as:

```text
relation_summary
spearman_summary
```

under:

```text
data/results/
```

rather than persisting reconstructed intermediate DataFrames.

The normalized database remains the source of truth for experiment-level data.

---

# Overall assessment

The experimental-analysis layer is becoming a useful independent component of Upscaling App.

It now provides three complementary levels of information:

```text
descriptive dataset structure
        +
treatment-effect comparisons
        +
physics-informed exploratory diagnostics
```

The immediate priority is not adding more analyses.

The priority is to:

1. correct the gas-selection issue;
2. rerun the existing diagnostics consistently;
3. decide which results materially improve the scientific narrative;
4. then return to the SSDI methodology and validation section of the presentation.
