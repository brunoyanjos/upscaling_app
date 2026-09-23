# Research Plan — Oil Property Effects and Correlation Development

## Status

**Deferred research pipeline — not part of the current SSDI reconstruction milestone.**

This document records the scientific rationale, hypotheses, candidate data sources, and validation strategy for a future correlation-development pipeline. Implementation should begin only after the main modelling workflows are reconstructed and stabilized, including SSDI, SSMD, and droplet-distribution analysis.

The purpose of this document is to preserve the research direction without expanding the scope of the current reconstruction work.

---

## 1. Motivation

The reconstructed SSDI pipeline reproduces the existing correlation and allows its statistical behavior to be evaluated systematically.

The leave-one-oil-out analysis showed that the SSDI correlation has moderate global generalization performance, but the prediction error is strongly heterogeneous across oils. Some oils exhibit systematic overprediction or underprediction when they are excluded from calibration.

This suggests that the existing hydrodynamic correlation may not capture all oil-dependent effects.

The next scientific question is therefore not only:

> How well does the current SSDI correlation fit the available experiments?

but also:

> Which physicochemical properties of the oil explain the systematic prediction errors that remain after the hydrodynamic effects already represented by the model are accounted for?

---

## 2. Scope Boundary

This work must remain separate from the reconstruction of the existing production pipelines.

The current modelling milestones should continue to focus on:

- reproducing the existing SSDI workflow;
- reconstructing the SSMD workflow;
- reconstructing droplet-distribution analysis;
- preserving deterministic databases and model outputs;
- separating ingestion, physics, calibration, prediction, and statistical analysis.

The correlation-development study described here is a **future research pipeline**.

It must not modify the validated SSDI equations simply to improve fit.

---

## 3. Current Evidence

The SSDI leave-one-oil-out analysis provides the first evidence that oil-specific behavior may be relevant.

In leave-one-oil-out validation:

1. one oil is excluded completely from calibration;
2. the SSDI coefficients are calibrated using the remaining oils;
3. the excluded oil is predicted without having contributed to the calibration;
4. the process is repeated for every oil.

This produces out-of-oil predictions for the complete experimental dataset.

The pooled leave-one-oil-out metrics showed a moderate degradation relative to the in-sample baseline, indicating that the model retains part of its predictive capability for unseen oils but does not generalize uniformly across all oils.

More importantly, the oil-level results showed strong systematic differences in residual behavior.

The relevant diagnostic quantity is the logarithmic residual:

\[
r_{\log}
=
\log\left(
\frac{d_{50,\mathrm{exp}}}
     {d_{50,\mathrm{pred}}}
\right).
\]

Interpretation:

- \(r_{\log} > 0\): the model underpredicts \(d_{50}\);
- \(r_{\log} < 0\): the model overpredicts \(d_{50}\);
- \(r_{\log} \approx 0\): little systematic multiplicative bias.

The future research pipeline should use the **out-of-oil residuals**, rather than only the in-sample residuals, as the primary diagnostic target.

---

## 4. Central Research Hypothesis

A useful working hypothesis is to separate two sources of variation.

### 4.1 Within-oil variation

Variation among experiments performed with the same oil may be driven primarily by hydrodynamic and operating conditions, such as:

- Weber number;
- Capillary number;
- Reynolds number;
- Froude number;
- nozzle diameter;
- liquid flow rate;
- gas flow rate;
- dispersion method;
- other operating parameters.

Conceptually:

\[
\text{within-oil behavior}
\longleftrightarrow
\text{hydrodynamics and operating conditions}.
\]

### 4.2 Between-oil variation

Systematic displacement of the response between different oils may depend on physicochemical properties of the oil.

Candidate properties include:

- density;
- API gravity;
- viscosity;
- interfacial tension;
- asphaltene content;
- wax content;
- TAN;
- sulfur content;
- nitrogen content;
- carbon residue;
- selected compositional descriptors;
- selected crude-assay descriptors.

Conceptually:

\[
\text{between-oil behavior}
\longleftrightarrow
\text{oil physicochemical properties}.
\]

A future correlation may therefore need to combine these two levels rather than treating all experiments as fully independent observations.

---

## 5. Available Oil Characterization Data

Individual crude-assay spreadsheets are available for the oils.

These tables may contain information at different levels:

### Whole-crude properties

These are the highest-priority properties for the first analysis because the dispersion experiments use the complete oil.

Examples include:

- density;
- API gravity;
- viscosity at defined temperatures;
- asphaltenes;
- wax;
- sulfur;
- nitrogen;
- TAN;
- carbon residue;
- metals;
- other bulk crude descriptors.

### Distillation and yield information

Distillation curves should not be inserted directly as dozens or hundreds of independent predictors.

If they become relevant, they should first be converted into physically interpretable descriptors, for example:

- \(T_{10}\);
- \(T_{50}\);
- \(T_{90}\);
- light-fraction yield;
- heavy-fraction yield;
- selected boiling-range fractions.

### Cut-specific properties

Properties associated with individual atmospheric or vacuum cuts should not initially be treated as equivalent to whole-crude properties.

They may become useful later if a physically meaningful aggregate descriptor is defined.

---

## 6. Data Architecture

Raw crude-assay spreadsheets must not be read directly by the scientific correlation-development pipeline.

They should follow the same architectural principle already established for the rest of the project:

```text
raw crude-assay spreadsheets
        ↓
database ingestion
        ↓
normalized oil-characterization database
        ↓
scientific analysis
```

A future normalized table may conceptually contain:

```text
oil_characterization

oil_id
density
api
viscosity_20
viscosity_40
interfacial_tension
asphaltenes
wax
tan
sulfur
nitrogen
carbon_residue
...
```

The existing relationship remains:

```text
oil_properties / oil_characterization
              1
              │
              N
         experiments
```

The exact schema should be defined only after the available crude-assay spreadsheets have been inventoried.

---

## 7. Statistical Unit of Analysis

A critical distinction must be maintained between the number of experiments and the number of independent oils.

If multiple experiments share the same oil-specific property, those repeated experiments do not create additional independent observations of that oil property.

For example, if one oil has a fixed asphaltene concentration across 18 experiments, this represents:

- 18 experimental responses;
- but only 1 independent oil-level observation of asphaltene concentration.

Therefore:

- hydrodynamic effects can use the full experiment-level dataset;
- oil-property effects must account for clustering by `oil_id`;
- experiment-level random train/test splitting should not be used to evaluate generalization to new oils.

This avoids pseudoreplication and overly optimistic statistical conclusions.

---

## 8. First Exploratory Analysis

The first implementation should be diagnostic, not immediately predictive.

A future analysis dataset may contain:

```text
experiment_id
oil_id

d50
d50_D

weber
capillary
reynolds
froude
nozzle_diameter
oil_flow
gas_flow
...

baseline_prediction
loo_prediction
loo_log_residual

density
viscosity
api
interfacial_tension
asphaltenes
wax
tan
...
```

The first analyses should include:

1. distributions of relevant physical and chemical variables;
2. coverage of the experimental property space;
3. correlation structure among candidate variables;
4. scatter plots of \(d_{50}/D\) versus relevant hydrodynamic variables;
5. scatter plots of out-of-oil log residual versus oil properties;
6. oil-level summaries of residual mean, residual variance, Log-MSE, RMSE, and MAPE;
7. identification of variables associated with systematic model bias.

The goal is to identify missing physical structure before proposing a new equation.

---

## 9. Dimensionless-Group Dependence

Dimensionless groups must not be treated as statistically independent predictors without checking their definitions.

For example, under the classical definitions:

\[
We = \frac{\rho U^2 D}{\sigma},
\qquad
Re = \frac{\rho U D}{\mu},
\qquad
Ca = \frac{\mu U}{\sigma},
\]

which implies:

\[
We = Re\,Ca.
\]

Therefore, blindly including \(We\), \(Re\), and \(Ca\) in the same regression can introduce exact or near-exact multicollinearity.

Variable selection must be guided by both physics and statistics.

---

## 10. Candidate Correlation Strategies

The first candidate models should remain parsimonious.

### Strategy A — Extend the existing SSDI structure

Preserve the current hydrodynamic correlation and allow one coefficient to depend on oil properties.

For example:

\[
A = A(X_{\mathrm{oil}})
\]

or:

\[
B = B(X_{\mathrm{oil}}).
\]

A positive coefficient may be parameterized using a form such as:

\[
A(X)
=
A_0\exp(\gamma X).
\]

This approach preserves more of the original physical structure.

### Strategy B — Multiplicative correction factor

Introduce a physically motivated oil-property correction:

\[
\frac{d_{50}}{D}
=
f(We,Ca)
\,g(X_{\mathrm{oil}}).
\]

This may be useful if the residual analysis shows a systematic between-oil multiplicative shift.

### Strategy C — Generalized power-law model

A diagnostic alternative is:

\[
\frac{d_{50}}{D}
=
C
We^a
Ca^b
X_1^c
X_2^d.
\]

In logarithmic form:

\[
\log\left(\frac{d_{50}}{D}\right)
=
\log C
+
a\log We
+
b\log Ca
+
c\log X_1
+
d\log X_2.
\]

This is convenient for statistical exploration, but it should not automatically replace a physically motivated model.

---

## 11. Model Complexity

The number of candidate oil properties may be large, but the number of independent oils is comparatively small.

Therefore, the first models must use only a small number of additional oil-level predictors.

Complex models with many chemical descriptors may produce excellent in-sample fits while having poor generalization.

The preferred sequence is:

```text
physical hypothesis
        ↓
small number of candidate variables
        ↓
parsimonious model
        ↓
grouped validation
```

not:

```text
all available variables
        ↓
automated regression
        ↓
best in-sample score
```

---

## 12. Validation Strategy

All future models intended to generalize to new oils should be evaluated using grouped validation by `oil_id`.

The baseline validation strategy is leave-one-oil-out:

```text
for each oil:
    hold out oil
    calibrate using remaining oils
    predict held-out oil
```

Experiment-level random splitting is inappropriate for this objective because measurements from the same oil could appear in both training and test sets.

### Nested validation

If the future study uses the available oils to select:

- variables;
- model form;
- interaction terms;
- hyperparameters;

then a simple leave-one-oil-out score may become optimistic because the validation results themselves influenced model development.

A stronger final procedure should use nested grouped validation:

```text
outer loop:
    hold out one oil completely

    inner loop:
        use remaining oils to select
        model structure and parameters

    outer test:
        evaluate on untouched held-out oil
```

This should be considered the preferred validation strategy for the final correlation-development study.

---

## 13. Potential Role of SSMD and Distribution Data

Implementation should wait until the broader modelling pipeline is reconstructed.

SSMD and droplet-distribution data may contribute information that is not visible when only \(d_{50}\) is considered.

Possible future questions include:

- whether oil properties affect SSDI and SSMD differently;
- whether oil properties influence distribution width or shape in addition to median diameter;
- whether systematic SSDI residuals correspond to changes in the entire droplet-size distribution;
- whether a common oil-property correction can explain multiple dispersion regimes.

This is one reason the correlation-development pipeline should remain deferred until the core SSDI, SSMD, and distribution workflows are stable.

---

## 14. Proposed Future Pipeline

The future research pipeline should follow approximately:

```text
crude-assay ingestion
        ↓
normalized oil characterization
        ↓
merge with normalized experiments
        ↓
existing-model out-of-oil predictions
        ↓
residual-property exploratory analysis
        ↓
candidate physical hypotheses
        ↓
parsimonious correlation development
        ↓
grouped / nested validation
        ↓
model comparison
        ↓
final scientific interpretation
```

This pipeline should remain separate from the SSDI reconstruction workflow.

---

## 15. Activation Criteria

Implementation of this research pipeline should begin only after:

- SSDI reconstruction is complete and frozen;
- SSMD reconstruction is complete;
- droplet-distribution analysis is reconstructed;
- crude-assay files for the available oils have been inventoried;
- oil identifiers can be mapped deterministically between assay data and experiments;
- the set of oil properties to normalize has been defined.

At that point, this document should be reviewed and converted into a dedicated milestone or research plan.

---

## 16. Immediate Next Step

No implementation is required now.

The current priority remains completing the main application pipeline.

When the core modelling workflows are complete, the first task for this research line should be:

> Build and validate a normalized oil-characterization database from the available crude-assay spreadsheets.

Only after that database exists should residual-property analysis or new-correlation fitting begin.
