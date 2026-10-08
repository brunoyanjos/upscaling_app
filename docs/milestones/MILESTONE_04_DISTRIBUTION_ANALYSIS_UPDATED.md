# Milestone 4 — Droplet-Size Distribution Analysis

**Status:** Completed — stable direct-CDF Rosin–Rammler fitting and distribution analysis

## Objective

Establish a reproducible workflow for measured droplet-size distributions and Rosin–Rammler parameter estimation using only normalized project databases.

The final stable workflow is:

```text
normalized distributions
        ↓
empirical CDF at original droplet diameters
        ↓
direct Rosin–Rammler CDF fit
        ↓
persist shape and scale
        ↓
fit-quality and D50 analysis
        ↓
reports and figures
```

Raw experimental spreadsheets remain confined to the database layer.

---

## 4.1 Normalized Data

The workflow consumes:

```text
data/database/experiments.xlsx
data/database/distributions.xlsx
```

The distribution database contains:

```text
experiment_id
droplet_diameter
volume_fraction
```

Experimental metadata include fields such as:

```text
experiment_id
oil_id
dispersion_kind
dispersion_tag
nozzle_diameter
has_gas
measured_d50
source_sheet
```

Internal quantities use SI units:

```text
droplet_diameter    m
measured_d50        m
volume_fraction     dimensionless
```

The current dataset contains:

```text
180 experimental distributions
52 diameter bins per distribution
10 oils
```

Zero-valued bins remain in the normalized database.

---

## 4.2 Experimental CDF Representation

For each experiment, the volume fractions are normalized and accumulated as:

\[
F_i=\sum_{j\le i}w_j.
\]

The decisive representation convention is:

> The empirical CDF values are associated directly with the original measured `droplet_diameter` coordinates.

Therefore the stable fitting coordinates are:

\[
(d_i,F_i).
\]

The production workflow does **not** shift the CDF to geometric upper bin edges.

This convention was selected after an explicit coordinate study comparing original diameters with an upper-edge interpretation.

---

## 4.3 Rosin–Rammler Model

The analytical reference is the two-parameter Rosin–Rammler / Weibull distribution:

\[
F(d)
=
1-\exp\left[-\left(\frac{d}{\lambda}\right)^k\right].
\]

where:

```text
k         shape parameter
lambda    scale parameter
```

The corresponding median is:

\[
D_{50}
=
\lambda(\ln2)^{1/k}.
\]

---

## 4.4 Stable Parameter Estimation

The production estimator fits the Rosin–Rammler CDF directly to the empirical cumulative distribution:

\[
\min_{k,\lambda}
\sum_i
\left[
F_{RR}(d_i;k,\lambda)-F_i
\right]^2.
\]

The optimization imposes:

\[
k>0,
\qquad
\lambda>0.
\]

No intermediate continuous reconstruction is required before fitting.

The stable workflow returns one parameter pair per experiment.

---

## 4.5 Resolved Methodological Comparisons

Two questions were explicitly investigated before the milestone was closed.

### Coordinate convention

The direct fit was compared using:

```text
point
    original droplet diameters

upper
    geometric upper bin edges
```

Using the original diameters produced substantially better D50 agreement with both the reported experimental median and, more importantly, the median reconstructed directly from the stored distribution.

For fitted D50 versus distribution-reconstructed D50:

```text
point
    MAPE ≈ 4.59 %
    R²   ≈ 0.9985

upper
    MAPE ≈ 12.73 %
    R²   ≈ 0.9835
```

The stable convention is therefore `point`.

### Moment-based estimator

A discrete-moment Rosin–Rammler estimator was also evaluated as a methodological alternative.

It did not outperform the direct CDF fit for the selected reconstruction objectives, including D50 agreement and CDF fidelity.

It was therefore removed from the stable production workflow rather than retained as a second persisted estimator.

Historical or exploratory moment-based comparisons may remain in research material, but they are not part of the Milestone-4 contract.

---

## 4.6 Persisted Parameters

The fitting workflow persists one row per experiment with:

```text
experiment_id
shape
scale
```

The deterministic `experiment_id` preserves the relationship between fitted parameters and the normalized experimental condition.

No production columns named:

```text
cdf_shape
cdf_scale
moment_shape
moment_scale
```

are required by the stable contract.

---

## 4.7 Fit Evaluation

The fitted Rosin–Rammler CDF is evaluated against the original empirical CDF at the same original diameter coordinates used during fitting.

Principal fit diagnostics include:

```text
CDF RMSE
CDF maximum absolute error
fitted D50
D50 agreement metrics
representative CDF figures
representative PDF figures
```

Current mean CDF RMSE across the 180 distributions is approximately:

```text
0.017585
```

This metric is a fit-quality diagnostic. It is not predictive validation of an unseen experiment or oil.

---

## 4.8 D50 References

Three distinct median diameters must remain conceptually separate.

### Reported D50

```text
measured_d50
```

Stored in the normalized experiment database and used by the SSDI and SSMD modelling workflows.

### Distribution-reconstructed D50

Calculated directly from the measured cumulative distribution by interpolation on the original `droplet_diameter` coordinates.

This is the **primary reference for evaluating whether the Rosin–Rammler fit reproduces the stored distribution**.

### Fitted D50

Calculated from fitted parameters:

\[
D_{50,fit}=\lambda(\ln2)^{1/k}.
\]

Current agreement of fitted D50 against distribution-reconstructed D50 is approximately:

```text
n          = 180
RMSE       = 0.025932 mm
MAE        = 0.016420 mm
MAPE       = 4.590485 %
R²         = 0.998529
Log-MSE    = 0.003792
R²_log     = 0.995474
```

---

## 4.9 Reported-vs-Distribution D50 Diagnostic

The reported experimental median and the median reconstructed from the stored distribution agree closely for most experiments but not all.

Current source-consistency diagnostic:

```text
MAPE       ≈ 4.906453 %
Median APE ≈ 0.378740 %
Max APE    ≈ 191.524727 %
```

The very large maximum error comes from a limited subset of source inconsistencies, primarily in specific SSMD cases.

These differences remain diagnostic observations.

The workflow must not silently alter `measured_d50` or the normalized distributions to force agreement.

---

## 4.10 PDF and Bin Representation

The Rosin–Rammler model is fitted to the CDF, not to a PDF or bin-mass objective.

Geometric bin edges remain useful when a continuous or binned PDF representation is needed for visualization:

\[
b_{i+1/2}=\sqrt{d_i d_{i+1}}.
\]

These edges are not used to relocate the empirical CDF in the stable fitting workflow.

The PDF is therefore interpreted primarily as a shape diagnostic.

This distinction is important because a fitted CDF may be good while a local PDF view exposes secondary peaks, multimodality, or other shape structure that a two-parameter Rosin–Rammler distribution cannot reproduce exactly.

---

## 4.11 Representative Figures

Representative distributions are selected from the already-calculated fit evaluation.

The standard visual interpretation is:

```text
CDF
    experimental points at original diameters
    +
    continuous Rosin–Rammler fit

PDF
    experimental binned representation
    +
    continuous Rosin–Rammler density
```

Plotting uses the shared project visual language:

```text
Untreated       petroleum / dark neutral
SSMD            blue
SSDI C9500      orange
SSDI IBC        yellow
Rosin–Rammler   neutral gray
identity        light gray
```

The plotting layer performs presentation operations only and does not fit models or calculate scientific metrics.

---

## 4.12 Stable Package Structure

The stable modelling package contains the Rosin–Rammler formulation, empirical representation helpers, fitting, orchestration, persistence, and concise reporting.

```text
src/upscaling_app/upscaling/distributions/
├── __init__.py
├── rosin_rammler.py
├── representation.py
├── fitting.py
├── pipeline.py
├── persistence.py
└── reporting.py
```

The stable analysis package separates calculations from orchestration, plotting, persistence, and terminal reporting:

```text
src/upscaling_app/analysis/distributions/
├── __init__.py
├── analysis.py
├── metrics.py
├── pipeline.py
├── persistence.py
├── plotting.py
└── reporting.py
```

Responsibilities:

```text
upscaling/distributions
    analytical distribution formulation
    direct CDF parameter estimation
    parameter persistence
    fit-workflow reporting

analysis/distributions
    empirical distribution diagnostics
    fit-quality metrics
    D50 consistency analysis
    result persistence
    plotting and reporting
```

---

## 4.13 Stable Execution

The stable CLI surface is:

```bash
upscaling distributions fit
upscaling analyze distributions
```

`upscaling distributions fit`:

```text
load normalized distributions
        ↓
construct empirical CDFs
        ↓
fit Rosin–Rammler at original diameters
        ↓
persist shape and scale
        ↓
report execution summary
```

`upscaling analyze distributions`:

```text
load normalized distributions
        ↓
load persisted shape and scale
        ↓
evaluate fitted CDFs
        ↓
reconstruct distribution D50
        ↓
compare fitted and experimental medians
        ↓
generate reports and figures
```

The CLI remains a dispatcher and contains no scientific calculations.

---

## 4.14 Scope Boundary

The following topics are not part of the stable Milestone-4 workflow:

```text
upper-edge CDF fitting
moment-based production fitting
legacy continuous-height reconstruction
alternative analytical distribution families
number-based transformations
shape-parameter correlations
oil-property correlations
scale-transfer correlations
gas-transfer correlations
field-scale k prediction
mixture-distribution modelling
```

Resolved representation studies are retained as research history; open research questions remain documented separately in:

```text
DISTRIBUTIONS_RESEARCH_GOALS_UPDATED.md
```

They must not silently replace the stable reference implementation.

---

## Milestone Result

Milestone 4 is closed with the following stable foundation:

```text
normalized experimental distributions
+
original-diameter empirical CDF convention
+
direct Rosin–Rammler fitting
+
shape / scale persistence
+
CDF fit-quality evaluation
+
distribution-reconstructed D50 reference
+
reported-D50 source diagnostic
+
representative CDF / PDF visualization
```

Future distribution-correlation and scale-up research should build on this foundation without reopening the settled representation convention unless new traceable evidence requires it.
