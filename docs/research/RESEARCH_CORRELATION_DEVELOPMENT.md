# Research Plan — Oil Property Effects and Correlation Development

## Status

**Deferred research pipeline — core SSDI, SSMD, and droplet-distribution reconstruction prerequisites are now complete.**

This document records the scientific rationale, hypotheses, candidate data sources, and validation strategy for future correlation development.

The production SSDI, SSMD, and distribution workflows should remain stable while this research is developed separately.

---

## 1. Motivation

The reconstructed SSDI pipeline shows meaningful predictive capability but retains systematic oil-dependent residual structure under leave-one-oil-out validation.

The reconstructed SSMD workflow also retains oil dependence and no universal full-scale closure has been validated.

The droplet-distribution workflow is now stable and provides fitted Rosin–Rammler `shape` and `scale` parameters for each experimental distribution.

The broader research question is therefore:

> Which physicochemical properties of the oil explain systematic model behaviour that remains after the hydrodynamic effects already represented by the production models are accounted for?

A related distribution question is:

> Do oil properties explain reproducible variation in distribution shape after characteristic droplet-size scale is removed?

---

## 2. Scope Boundary

This research must remain separate from production reconstruction.

Stable production blocks now include:

```text
SSDI reconstruction and validation
SSMD reconstruction and validation
direct-CDF Rosin–Rammler distribution fitting
experimental analysis architecture
```

The research pipeline must not modify validated production equations or stable distribution representation solely to reduce in-sample error.

---

## 3. Current Evidence

### SSDI

Leave-one-oil-out validation shows moderate global transferability but important oil-specific residual structure.

The useful diagnostic quantity remains:

\[
r_{\log}
=
\log\left(
\frac{d_{50,exp}}
{d_{50,pred}}
\right).
\]

Interpretation:

```text
r_log > 0    model underpredicts d50
r_log < 0    model overpredicts d50
r_log ≈ 0    little systematic multiplicative bias
```

Out-of-oil residuals are more informative for transferable oil-property research than purely in-sample residuals.

### SSMD

The current SSMD campaign indicates systematic oil and gas dependence, but the experimental design cannot independently identify all candidate water-jet control variables.

### Droplet distributions

The stable direct CDF fit now provides one Rosin–Rammler parameter pair per experiment:

```text
experiment_id
shape
scale
```

Distribution-reconstructed D50 is the primary median reference for fit analysis, while reported `measured_d50` remains a secondary source-consistency diagnostic.

This makes distribution shape available as a separate research target rather than conflating all droplet-size information into D50 alone.

---

## 4. Central Research Hypothesis

A useful working hypothesis is to separate two sources of variation.

### 4.1 Within-oil variation

Variation among experiments performed with the same oil may be driven primarily by hydrodynamic and operating conditions:

```text
Weber number
Capillary number
Reynolds number
Froude number
nozzle diameter
liquid flow rate
gas flow rate
dispersion method
SSMD treatment intensity
```

Conceptually:

\[
\text{within-oil behaviour}
\longleftrightarrow
\text{hydrodynamics and operating conditions}.
\]

### 4.2 Between-oil variation

Systematic displacement between oils may depend on physicochemical properties:

```text
density
API gravity
viscosity
interfacial tension
asphaltenes
wax
TAN
sulfur
nitrogen
carbon residue
selected compositional descriptors
```

Conceptually:

\[
\text{between-oil behaviour}
\longleftrightarrow
\text{oil physicochemical properties}.
\]

A future model may need to combine experiment-level hydrodynamics with oil-level physicochemical structure.

---

## 5. Available Oil Characterization Data

Individual crude-assay spreadsheets are available for the oils.

Whole-crude properties are the highest-priority descriptors because the dispersion experiments use the complete oil.

Candidate groups include:

```text
whole-crude density / API
viscosity at defined temperatures
asphaltenes
wax
sulfur
nitrogen
TAN
carbon residue
selected distillation descriptors
```

Distillation curves should not initially be inserted as large sets of independent predictors. If used, they should first be reduced to physically interpretable descriptors such as `T10`, `T50`, `T90`, and selected yield fractions.

---

## 6. Data Architecture

Raw crude-assay spreadsheets must not be read directly by scientific correlation-development pipelines.

They should follow the established project architecture:

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
asphaltenes
wax
tan
sulfur
nitrogen
carbon_residue
...
```

The exact schema should be defined only after the available source files are inventoried.

---

## 7. Statistical Unit of Analysis

A critical distinction must be maintained between the number of experiments and the number of independent oils.

Repeated experiments sharing one oil-specific property do not create independent observations of that property.

Therefore:

```text
hydrodynamic effects
    may use experiment-level observations

oil-property effects
    must account for clustering by oil_id

new-oil generalization
    must not use random experiment-level splitting
```

This avoids pseudoreplication and overly optimistic conclusions.

---

## 8. First Exploratory Analysis

The first implementation should be diagnostic, not immediately predictive.

A future joined dataset may contain:

```text
experiment_id
oil_id

measured responses
model predictions
out-of-oil residuals

hydrodynamic quantities

oil properties

distribution shape
```

Candidate first analyses include:

1. coverage of the physical and chemical property space;
2. correlation structure among candidate variables;
3. SSDI out-of-oil residual versus oil properties;
4. SSMD response diagnostics versus oil properties;
5. fitted distribution `shape` versus hydrodynamics and treatment;
6. oil-level summaries of shape and prediction residuals;
7. identification of variables associated with systematic between-oil shifts.

The goal is to identify missing physical structure before proposing new equations.

---

## 9. Dimensionless-Group Dependence

Dimensionless groups must not be treated as independent predictors without checking their definitions.

For example:

\[
We=\frac{\rho U^2D}{\sigma},
\qquad
Re=\frac{\rho UD}{\mu},
\qquad
Ca=\frac{\mu U}{\sigma},
\]

which implies under the classical definitions:

\[
We=Re\,Ca.
\]

Variable selection must therefore be guided by both physics and statistical identifiability.

---

## 10. Candidate Correlation Strategies

The first candidate models should remain parsimonious.

### Strategy A — Extend an existing physical structure

Allow a limited production coefficient or correction factor to depend on one physically motivated oil property.

### Strategy B — Multiplicative oil-property correction

Use a form such as:

\[
Y=f(\text{hydrodynamics})\,g(X_{oil}).
\]

### Strategy C — Shape correlation

For distributions, treat Rosin–Rammler `shape` as the target:

\[
k=f(\text{hydrodynamics},X_{oil},\text{treatment},\text{gas},\text{geometry}).
\]

This should be attempted only after normalized-shape diagnostics show that a nontrivial predictive shape model is scientifically justified.

### Strategy D — Generalized power-law diagnostic

Log-linear power laws may be useful for screening but should not automatically replace physically motivated models.

---

## 11. Model Complexity

The number of candidate oil properties may be large, but only ten independent oils are currently available.

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

not automated selection of a large predictor set based on in-sample score.

---

## 12. Validation Strategy

Any future model intended to generalize to new oils should use grouped validation by `oil_id`.

Baseline strategy:

```text
for each oil:
    hold out oil
    fit using remaining oils
    predict held-out oil
```

If model structure, variables, interactions, or hyperparameters are selected using the same oils, the final study should use nested grouped validation.

Experiment-level random train/test splitting is inappropriate for the new-oil objective.

---

## 13. Role of Distribution Data

The distribution pipeline is no longer a missing prerequisite.

It now contributes experiment-level shape information that may reveal effects not visible in D50 alone.

Future questions include:

```text
Does treatment alter shape after D50 normalization?
Does gas alter shape systematically?
Are shape differences oil dependent?
Do SSDI residuals correspond to distribution-shape changes?
Can one oil-property descriptor explain both median and shape behaviour?
```

Distribution-level predictive validation should use the complete measured CDF rather than only fitted D50.

---

## 14. Proposed Future Pipeline

```text
crude-assay ingestion
        ↓
normalized oil characterization
        ↓
merge with normalized experiments and fitted distribution parameters
        ↓
existing-model out-of-oil predictions
        ↓
residual / shape exploratory analysis
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

This pipeline remains separate from production reconstruction.

---

## 15. Activation Criteria

The following prerequisites are now satisfied:

```text
[x] SSDI reconstruction complete and stabilized
[x] SSMD reconstruction complete
[x] droplet-distribution fitting and analysis stabilized
```

The main remaining prerequisites are:

```text
[ ] inventory crude-assay files
[ ] define deterministic oil-ID mapping for assay data
[ ] define normalized oil-characterization schema
[ ] select the first small set of oil properties to analyse
```

---

## 16. Immediate Next Step

No production-model change is required.

When this research line is activated, the first task should be:

> Build and validate a normalized oil-characterization database from the available crude-assay spreadsheets.

In parallel, distribution-specific research may begin with shape collapse and descriptive analysis of fitted `k`, because the stable distribution parameter database now exists.
