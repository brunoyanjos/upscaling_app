# Distribution Research Goals

**Status:** Exploratory research — not part of the stable production workflow

## Purpose

This document records open research questions, diagnostic comparisons, alternative mathematical representations, and future correlation-development directions for droplet-size distributions.

Nothing in this document should silently replace the stable Rosin–Rammler fitting or experimental-analysis workflow documented in:

```text
MILESTONE_04_DISTRIBUTION_ANALYSIS_UPDATED.md
```

The stable reference remains:

```text
normalized experimental distributions
        ↓
experimental descriptors
        ↓
direct Rosin–Rammler CDF fit
        ↓
persisted k and lambda
```

---

## 1. Representation Problem

The measured distribution is discrete:

\[
\{d_i,w_i\},
\qquad
\sum_i w_i = 1.
\]

Before introducing alternative analytical models, it is necessary to distinguish:

```text
experimental discrete distribution
        ↓
representation / reconstruction error
        ↓
analytical-distribution fitting error
```

A poor analytical reconstruction may arise because:

1. the analytical family is inadequate; or
2. the discrete-to-continuous representation already modified the measured distribution.

These effects must not be conflated.

---

## 2. Stable Baseline

The stable analytical reference is the two-parameter Rosin–Rammler / Weibull CDF:

\[
F(d)
=
1-
\exp
\left[
-\left(
\frac{d}{\lambda}
\right)^k
\right].
\]

The median is:

\[
D_{50}
=
\lambda(\ln 2)^{1/k}.
\]

The current production-reference estimator is the direct CDF fit.

The current discrete-moment estimator is retained as a methodological reference.

---

## 3. Legacy Continuous-Height Reconstruction

A previous research script used a different representation before calculating moments.

The workflow was:

```text
measured discrete distribution
        ↓
select non-zero support
        ↓
backward-average diameter locations
        ↓
piecewise-constant continuous function
        ↓
normalize by integral
        ↓
continuous mean and variance
        ↓
Rosin–Rammler k and lambda
```

The piecewise function used the original discrete weight as an interval height:

\[
g_H(d)=w_i.
\]

After normalization:

\[
f_H(d)
=
\frac{g_H(d)}
{\int g_H(d)\,dd}.
\]

Therefore the effective probability mass associated with an interval becomes approximately:

\[
P_i
\propto
w_i \Delta d_i.
\]

Because the experimental diameter grid is logarithmically spaced, larger-diameter intervals have larger widths.

The legacy transformation therefore introduces an additional bin-width weighting and is not mathematically equivalent to the current discrete-moment estimator.

This method remains diagnostic only.

---

## 4. Legacy vs Current Moment Comparison

A dedicated diagnostic compares:

```text
current discrete-moment estimator
vs
legacy continuous-height estimator
```

for all experimental distributions.

The principal quantities are:

```text
k
lambda
D50
```

The comparison should report:

```text
mean absolute relative difference
median absolute relative difference
maximum absolute relative difference
```

and generate a parity plot for:

\[
D_{50,\mathrm{legacy}}
\quad\text{vs}\quad
D_{50,\mathrm{current}}.
\]

The result determines whether the current discrete-moment estimator can be considered numerically close to the historical method.

Until that assessment is complete, the two methods must remain explicitly distinguished.

---

## 5. Alternative Continuous Representations

### 5.1 Continuous-height representation

Historical approach:

\[
g_H(d)=w_i.
\]

This does not preserve the original bin probability mass when interval widths differ.

### 5.2 Mass-preserving continuous representation

A continuous piecewise-constant PDF can instead preserve each original bin mass:

\[
f_M(d)
=
\frac{w_i}{\Delta d_i}.
\]

Then:

\[
\int_{\mathrm{bin}\ i}
f_M(d)\,dd
=
w_i.
\]

For logarithmically spaced diameter centres, geometrically defined boundaries are natural candidates:

\[
b_{i+1/2}
=
\sqrt{d_i d_{i+1}}.
\]

This representation may be a more rigorous continuous benchmark, but it is not yet part of the stable workflow.

---

## 6. Direct CDF Fit as Reference Benchmark

The direct CDF fit minimizes:

\[
\min_{k,\lambda}
\sum_i
\left[
F_{\mathrm{RR}}(d_i;k,\lambda)
-
F_i
\right]^2.
\]

Its role is to determine how well a two-parameter Rosin–Rammler distribution can represent the measured cumulative distribution without an intermediate moment reconstruction.

This helps distinguish:

```text
inadequate Rosin–Rammler family
```

from:

```text
adequate Rosin–Rammler family
but inadequate parameter-estimation route
```

---

## 7. D50 Diagnostics

For any Rosin–Rammler parameter pair:

\[
D_{50}
=
\lambda(\ln 2)^{1/k}.
\]

Diagnostic comparisons may include:

```text
reported measured D50
distribution-reconstructed D50
direct-CDF-fit D50
discrete-moment D50
legacy continuous-height D50
```

These diagnostics must not modify `measured_d50` in the normalized experiment database.

---

## 8. Experimental D50 Anomalies

Most distributions reproduce the reported experimental \(D_{50}\) closely from the measured cumulative distribution.

A limited subset, mainly specific SSMD cases, shows substantial disagreement.

Relevant hypotheses include:

```text
selected experimental time windows
isolated large droplets
secondary large-droplet peaks
incomplete water jetting
measurement uncertainty
representative-value selection
```

These cases remain diagnostic.

No global filtering or database correction should be introduced without traceable evidence.

---

## 9. Distribution-Family Benchmark

Rosin–Rammler is the current reference family, but future work may compare:

```text
Rosin–Rammler / Weibull
Lognormal
Gamma
Generalized Gamma
mixture distributions
```

Evaluation should consider whether model preference depends on:

```text
Untreated
SSDI
SSMD
gas condition
oil identity
experimental regime
```

The purpose is not merely to minimize in-sample error, but to determine whether a physically useful and transferable family exists.

---

## 10. Shape Collapse

A future diagnostic may normalize diameter by the experimental median:

\[
x
=
\frac{d}{D_{50}}.
\]

The normalized CDF is:

\[
F(x)
=
F\left(
\frac{d}{D_{50}}
\right).
\]

The main question is how much distribution-shape information remains after removing the characteristic diameter scale.

Possible outcomes include:

```text
universal collapse
treatment-specific collapse
no useful collapse
```

Useful shape descriptors include:

\[
\frac{D_{10}}{D_{50}},
\qquad
\frac{D_{90}}{D_{50}},
\qquad
span.
\]

---

## 11. Future k Correlation

The existing SSDI and SSMD workflows already predict characteristic droplet diameter.

For a two-parameter Rosin–Rammler distribution:

\[
\lambda
=
\frac{D_{50}}
{(\ln 2)^{1/k}}.
\]

Therefore a natural future field-scale formulation is:

```text
predicted D50
+
predicted k
        ↓
lambda
        ↓
complete Rosin–Rammler distribution
```

The principal research target may therefore become:

\[
k
=
f(
\text{hydrodynamics},
\text{oil properties},
\text{treatment},
\text{gas},
\text{geometry}
).
\]

Candidate physical variables may include:

```text
Weber number
Capillary number
Reynolds number
Froude number
momentum amplification
gas condition
oil viscosity
interfacial tension
oil density
treatment type
```

This correlation-development stage is not yet production-ready.

---

## 12. Oil-Property Dependence

Systematic between-oil variation may depend on whole-crude properties such as:

```text
density / API gravity
viscosity
interfacial tension
asphaltenes
wax
TAN
sulfur
nitrogen
carbon residue
selected crude-assay descriptors
```

Only normalized oil-property databases should be used.

Raw crude-assay spreadsheets must remain confined to the database layer.

Because only ten oils are currently available, oil-property modelling must treat the oil as the independent statistical unit.

---

## 13. Scale and Gas Transfer

Existing diagnostics indicate that shape behavior may vary with:

```text
2 mm vs 3 mm nozzle
gas vs no-gas
dispersion mechanism
oil identity
SSMD treatment intensity
```

No universal scale or gas correction should be assumed without validation.

Future transfer tests should remain separate from the stable parameter-fitting workflow.

---

## 14. Number-Based Representation

The measured experimental distributions are volume-weighted.

A number-based representation may be constructed using:

\[
w_{N,i}
=
\frac{
w_{V,i}/d_i^3
}{
\sum_j w_{V,j}/d_j^3
}.
\]

This transformation strongly emphasizes the smallest resolved droplets.

It is therefore sensitive to:

```text
minimum measurable diameter
instrument detection limit
left truncation
binning convention
```

Any future number-based model must keep these limitations explicit.

This route is exploratory only.

---

## 15. Multimodal SSMD Distributions

Some SSMD distributions contain evidence of:

```text
primary droplet population
+
secondary large-droplet population
```

If these populations represent reproducible physics rather than measurement or operating artifacts, a single two-parameter Rosin–Rammler distribution may be insufficient.

Possible future extensions include mixture models:

\[
F(d)
=
\alpha F_1(d)
+
(1-\alpha)F_2(d).
\]

Mixture modelling should not begin before the large-droplet events are classified scientifically.

---

## 16. Validation Philosophy

Distribution modelling must preserve the distinction:

```text
fit quality
≠
sensitivity analysis
≠
predictive validation
```

A model may reproduce all current distributions in sample and still fail for a new oil.

Any future oil-transfer model should eventually use grouped validation by `oil_id`, for example:

```text
hold out one oil
        ↓
fit shape model using remaining oils
        ↓
predict held-out oil distribution
        ↓
compare predicted and measured CDFs
```

Distribution-level validation should use more than \(D_{50}\) alone.

---

## 17. Research Sequence

### Phase A — Representation diagnostics

Compare:

```text
discrete moments
legacy continuous-height representation
mass-preserving continuous representation
direct CDF fit
```

Evaluate:

```text
k
lambda
D50
CDF RMSE
maximum CDF deviation
```

### Phase B — Distribution-family benchmark

Compare alternative analytical families against the original measured CDF.

### Phase C — Shape modelling

Study normalized shape and identify candidate predictors for \(k\).

### Phase D — Oil-property dependence

Evaluate whole-crude descriptors using oil-level statistics.

### Phase E — Predictive validation

Use grouped validation by oil and assess scale/gas transfer.

### Phase F — Field-scale reconstruction

Combine predicted \(D_{50}\) and predicted \(k\) to reconstruct the field-scale Rosin–Rammler distribution for downstream use.

---

## Research Boundary

The content in this document is intentionally exploratory.

It should not be exposed as a stable CLI workflow or used as a production reference until the corresponding scientific question has been resolved and validation criteria have been established.
