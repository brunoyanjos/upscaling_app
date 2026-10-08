# Milestone 4 — Droplet-Size Distribution Analysis

**Status:** Completed — experimental analysis and Rosin–Rammler fitting foundation

## Objective

Establish a reproducible workflow for experimental droplet-size distribution analysis and Rosin–Rammler parameter estimation using the normalized project databases.

The stable workflow is:

```text
normalized distributions
        ↓
experimental distribution analysis
        ↓
Rosin–Rammler parameter estimation
        ↓
fit-quality evaluation
        ↓
persisted distribution parameters
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

Experimental metadata include:

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

Zero-valued bins are retained in the normalized database.

---

## 4.2 Experimental Distribution Analysis

The stable experimental workflow evaluates each measured distribution directly, without introducing an analytical distribution model.

Calculated quantities include:

```text
D10
D50
D90
d_peak
volume-weighted mean diameter
volume-weighted standard deviation
span
volume-fraction sum
```

The span is defined as:

\[
span =
\frac{D_{90}-D_{10}}{D_{50}}.
\]

The experimental quantiles are reconstructed from the cumulative volume distribution.

For a target probability \(q\), with:

\[
F_0 < q \leq F_1,
\]

linear interpolation is used:

\[
d_q
=
d_0
+
\frac{q-F_0}{F_1-F_0}
(d_1-d_0).
\]

For the median:

\[
q=0.5.
\]

The reconstructed distribution \(D_{50}\) agrees closely with the reported experimental \(D_{50}\) for most experiments.

A limited subset of experiments exhibits substantial disagreement, primarily associated with specific SSMD cases. These cases remain diagnostic observations and do not modify the normalized database.

---

## 4.3 Rosin–Rammler Model

The analytical distribution adopted as the reference model is the two-parameter Rosin–Rammler distribution:

\[
F(d)
=
1 -
\exp
\left[
-\left(
\frac{d}{\lambda}
\right)^k
\right].
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
\lambda
(\ln 2)^{1/k}.
\]

Therefore:

\[
\lambda
=
\frac{D_{50}}
{(\ln 2)^{1/k}}.
\]

---

## 4.4 Direct CDF Parameter Estimation

The production-reference fitting method estimates \(k\) and \(\lambda\) directly from the measured cumulative volume distribution.

The experimental CDF is:

\[
F_i
=
\sum_{j \leq i} w_j.
\]

The parameters are obtained by minimizing:

\[
\min_{k,\lambda}
\sum_i
\left[
F_{\mathrm{RR}}(d_i;k,\lambda)
-
F_i
\right]^2.
\]

The optimization imposes:

\[
k > 0,
\qquad
\lambda > 0.
\]

This method avoids introducing an intermediate continuous representation of the measured discrete distribution.

The fitted parameters are stored as:

```text
cdf_shape
cdf_scale
```

---

## 4.5 Discrete-Moment Reference Estimator

A second estimator is retained as a methodological reference.

The measured volume fractions are normalized:

\[
w_i
=
\frac{v_i}
{\sum_j v_j}.
\]

The discrete mean and variance are:

\[
\mu
=
\sum_i w_i d_i,
\]

\[
\sigma^2
=
\sum_i
w_i(d_i-\mu)^2.
\]

For a Rosin–Rammler / Weibull distribution:

\[
CV^2
=
\frac{
\Gamma(1+2/k)
}{
\Gamma^2(1+1/k)
}
-1.
\]

The shape parameter is obtained numerically from this equation and the scale is subsequently calculated from:

\[
\lambda
=
\frac{\mu}
{\Gamma(1+1/k)}.
\]

The corresponding persisted parameters are:

```text
moment_shape
moment_scale
```

This method is retained as a reference estimator rather than the production fitting method.

---

## 4.6 Persisted Parameters

The distribution fitting workflow produces one row per experiment with:

```text
experiment_id
cdf_shape
cdf_scale
moment_shape
moment_scale
```

The deterministic `experiment_id` preserves the relationship between distribution parameters and experimental conditions.

---

## 4.7 Fit Evaluation

The analytical Rosin–Rammler distribution is evaluated against the original experimental cumulative distribution.

The principal diagnostics include:

```text
CDF RMSE
maximum CDF deviation
paired method comparison
comparison by dispersion regime
```

The direct CDF fit currently serves as the production-reference Rosin–Rammler parameterization.

The discrete-moment estimator remains available for methodological comparison.

---

## 4.8 D50 Consistency

For each fitted Rosin–Rammler model:

\[
D_{50,\mathrm{RR}}
=
\lambda
(\ln 2)^{1/k}.
\]

This allows direct comparison between:

```text
reported experimental D50
distribution-reconstructed D50
Rosin–Rammler fitted D50
```

The purpose of this comparison is diagnostic.

The experimentally reported `measured_d50` remains the experimental reference quantity used by the SSDI and SSMD modelling pipelines.

---

## 4.9 Stable Package Structure

```text
src/upscaling_app/upscaling/distributions/
├── rosin_rammler.py
├── fitting.py
├── pipeline.py
└── persistence.py

src/upscaling_app/analysis/distributions/
├── data.py
├── descriptive.py
├── validation.py
├── plotting.py
├── reporting.py
└── pipeline.py
```

Responsibilities remain separated:

```text
upscaling/distributions
    analytical distribution formulation
    parameter estimation
    parameter persistence

analysis/distributions
    measured-distribution analysis
    consistency diagnostics
    statistical evaluation
    plotting and reporting
```

---

## 4.10 CLI

Stable workflows should be exposed through:

```bash
upscaling distributions fit
upscaling analyze distributions
```

`upscaling distributions fit`:

```text
load normalized distributions
        ↓
fit Rosin–Rammler parameters
        ↓
persist parameters
```

`upscaling analyze distributions`:

```text
load normalized distributions
        ↓
calculate experimental descriptors
        ↓
validate D50 consistency
        ↓
generate reports and figures
```

The CLI remains a dispatcher and contains no scientific calculations.

---

## 4.11 Scope Boundary

The following topics are intentionally not part of the stable Milestone 4 production workflow:

```text
legacy continuous-height reconstruction
alternative continuous representations
distribution-family benchmarking
number-based transformations
shape-parameter correlations
oil-property correlations
scale-transfer correlations
gas-transfer correlations
field-scale k prediction
```

These remain research topics and are documented separately in:

```text
DISTRIBUTIONS_RESEARCH_GOALS_UPDATED.md
```

They must not replace the stable reference implementation until their scientific role and validation criteria are established.

---

## Milestone Result

The project now provides a reproducible experimental distribution analysis and Rosin–Rammler fitting workflow based exclusively on the normalized databases.

The stable foundation consists of:

```text
experimental distribution descriptors
+
D50 consistency analysis
+
direct Rosin–Rammler CDF fitting
+
discrete-moment reference fitting
+
persisted experiment-level parameters
+
fit-quality evaluation
```

Future distribution-correlation and upscaling research will build on this foundation without modifying the established normalized data or reference fitting workflow.
