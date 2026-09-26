# Experimental Analysis — Current Status

## Status

**Closed — architecture and standard experimental workflows stabilized**

The experimental-analysis layer operates on normalized Upscaling App databases and remains separate from SSDI/SSMD calibration, prediction, and model evaluation.

Its responsibilities are to:

- describe experimental coverage and completeness;
- quantify treatment effects relative to matched untreated conditions;
- analyse SSDI-specific experimental behaviour;
- analyse SSMD-specific experimental behaviour;
- generate reproducible terminal reports and figures;
- provide physically meaningful descriptive diagnostics without modifying validated model equations.

---

## 1. Current architecture

```text
src/upscaling_app/analysis/experimental/
├── __init__.py
├── data.py
├── summary/
│   ├── __init__.py
│   ├── analysis.py
│   ├── pipeline.py
│   ├── plotting.py
│   └── reporting.py
├── treatment_effect/
│   ├── __init__.py
│   ├── analysis.py
│   ├── pipeline.py
│   ├── plotting.py
│   └── reporting.py
├── ssdi/
│   ├── __init__.py
│   ├── analysis.py
│   ├── pipeline.py
│   ├── plotting.py
│   └── reporting.py
└── ssmd/
    ├── __init__.py
    ├── analysis.py
    ├── pipeline.py
    ├── plotting.py
    └── reporting.py
```

All four modules now follow the same internal organization.

The reusable convention is documented separately in:

```text
docs/ANALYSIS_MODULE_PATTERN.md
```

---

## 2. Data-flow rule

```text
raw spreadsheets
        ↓
database layer
        ↓
normalized databases
        ↓
experimental analysis
        ↓
result objects
        ↓
reporting + figures
```

Raw spreadsheet interpretation remains confined to the database layer.

Internal quantities remain in SI units whenever applicable. Conversions such as `m → mm` and `0.40 → 40 %` are presentation operations.

---

## 3. CLI

```bash
upscaling analyze experimental summary
upscaling analyze experimental treatment-effect
upscaling analyze experimental ssdi
upscaling analyze experimental ssmd
```

Summary also supports:

```bash
upscaling analyze experimental summary --kind all
upscaling analyze experimental summary --kind untreated
upscaling analyze experimental summary --kind ssdi
upscaling analyze experimental summary --kind ssmd
```

The CLI is a dispatcher only and calls the module workflow.

---

## 4. Summary module

### Purpose

Answer:

> What experimental data are available, how are they structured, and how complete is the normalized dataset?

### Main outputs

```text
dataset_summary
regime_summary
oil_coverage
oil_treatment_coverage
completeness
```

The module intentionally avoids generic correlation matrices, D50 histograms, and broad pairplots.

### Main figures

```text
experimental_regime_coverage.png
experimental_oil_coverage.png
```

---

## 5. Treatment-effect module

### Purpose

Answer:

> How much does each treatment reduce measured D50 relative to the corresponding untreated release condition, and how does that response vary between oils?

### Pairing

```text
oil_id
nozzle_diameter
has_gas
```

Multiple untreated references for the same pairing key are treated as a data-integrity error.

### Metrics

```text
d50_ratio =
    measured_d50 / untreated_d50

d50_reduction =
    untreated_d50 - measured_d50

d50_reduction_pct =
    100 * (1 - d50_ratio)
```

### Result object

```text
TreatmentEffectResult
├── effects
├── by_oil
└── by_method
```

`by_method` summarizes oil-level medians so that oils with more experimental conditions do not automatically receive greater weight.

### Main figures

```text
d50_reduction_by_method.png
d50_reduction_by_oil.png
```

The standard workflow no longer contains:

```text
best/worst ranking
IQR outlier ranking
water-jet-specific analysis
SSDI dispersant-specific analysis
```

Water-jet behaviour belongs to SSMD. C9500-vs-IBC analysis belongs to SSDI.

---

## 6. SSDI experimental module

### Scope

```text
C9500 vs IBC
hydrodynamic association with d50/D
d50/D vs We
d50/D vs Ca
modified-Weber consistency diagnostic
```

### Preparation

The prepared population is always:

```text
Untreated + SSDI
gas + no gas
```

There is no implicit gas exclusion.

The module reuses the validated SSDI physical preprocessing.

```text
d50_D = measured_d50 / nozzle_diameter
```

### Modified Weber

```text
modified_weber =
    weber
    /
    (
        1
        + B
        * capillary
        * d50_D^(1/3)
    )

B = 0.08
```

Because `modified_weber` contains `d50_D`, it is a consistency diagnostic rather than an independent predictor.

It is not included in independent hydrodynamic screening.

### Analyses

```text
C9500 vs IBC paired oil comparison

Spearman:
    pooled
    ssdi_only

log-log:
    pooled:
        We
        Ca
        We*

    ssdi_only:
        We
        Ca
```

Pooled and SSDI-only analyses remain explicit because pooled relationships can reflect between-regime separation.

### Result object

```text
SSDIExperimentalResult
├── data
├── ssdi_only
├── dispersant_comparison
├── relation_summary
└── spearman_summary
```

### Main figures

```text
ssdi_dispersant_comparison.png
ssdi_spearman_screening.png

pooled/
    d50D_vs_weber.png
    d50D_vs_capillary.png
    d50D_vs_modified_weber.png

ssdi_only/
    d50D_vs_weber.png
    d50D_vs_capillary.png
```

---

## 7. SSMD experimental module

### Scope

```text
water-jet response
experimental-regime dependence
monotonicity
paired gas effect
dR vs momentum amplification
```

SSMD experiments are paired to untreated references using:

```text
oil_id
nozzle_diameter
has_gas
```

The module reuses the production SSMD physical preprocessing.

```text
dR_measured =
    measured_d50 / untreated_d50_measured

d50_reduction_pct =
    100 * (1 - dR_measured)
```

The three regimes remain distinct:

```text
3 mm — no gas
2 mm — no gas
2 mm — gas
```

### Water-jet response

Summaries are evaluated by:

```text
regime
water_jet_fraction
```

using median and interquartile range.

Monotonicity is evaluated per:

```text
regime × oil_id
```

and then summarized by regime.

### Gas effect

The paired gas comparison is restricted to the 2 mm nozzle and preserves:

```text
same oil_id
same water_jet_fraction
```

The main ratio is:

```text
dR_gas_to_no_gas =
    dR_gas / dR_no_gas
```

Interpretation:

```text
ratio = 1
    same relative response

ratio > 1
    gas case retains larger relative droplets

ratio < 1
    gas case retains smaller relative droplets
```

### Momentum amplification

```text
A_M = (M_o + M_w) / M_o
```

The experimental diagnostic evaluates:

```text
dR_measured vs A_M
```

for the global dataset and the three experimental regimes.

Regression statistics are calculated in `analysis.py`, never inside plotting.

The global relation is a descriptive bridge to the reconstructed SSMD formulation, not an independently validated universal power law.

### Result object

```text
SSMDExperimentalResult
├── data
├── by_regime
├── by_fraction_regime
├── monotonicity
├── monotonicity_by_regime
├── gas_comparison
├── gas_comparison_summary
└── momentum_relation_summary
```

### Main figures

```text
ssmd_response_by_regime.png
ssmd_gas_effect.png
ssmd_dR_vs_momentum_amplification.png
```

The standard experimental workflow no longer contains model-specific `eta`, Equation-5-derived response, property-correction fitting, or predictive-validation metrics.

---

## 8. Scientific interpretation rules

### Association is not causation

Spearman coefficients and exploratory regressions describe association, not physical causality.

### Pooled effects require explicit interpretation

Pooled relationships may combine within-regime variation and between-regime separation.

### Oil-level properties require oil-level statistical care

Repeated experiments on one oil do not create independent observations of an oil property.

### Experimental analysis is not model modification

The experimental layer may diagnose variability, regime structure, unexplained behaviour, and candidate mechanisms.

It must not silently alter SSDI or SSMD production correlations.

---

## 9. Stable execution pattern

```text
analysis.py
    calculations

pipeline.py
    result dataclass
    run_*_analysis()
    run_*_workflow()

plotting.py
    visualization only

reporting.py
    terminal presentation only

cli.py
    workflow dispatch only
```

The detailed standard is defined in `ANALYSIS_MODULE_PATTERN.md`.

---

## 10. Closure

The experimental-analysis architecture is considered closed for the current project stage.

It now provides:

```text
dataset structure
        +
treatment effects
        +
SSDI experimental diagnostics
        +
SSMD experimental diagnostics
```

Future additions should be question-driven rather than exploratory accumulation.

The normalized databases remain the source of truth for experiment-level data.
