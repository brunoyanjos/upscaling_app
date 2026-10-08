# Distribution Research Goals

**Status:** Exploratory research — stable representation and fitting questions resolved; shape and transfer research remain open

## Purpose

This document records open research questions, resolved methodological studies, and future correlation-development directions for droplet-size distributions.

Nothing here should silently replace the stable workflow documented in:

```text
MILESTONE_04_DISTRIBUTION_ANALYSIS_UPDATED.md
```

The stable reference is now:

```text
normalized experimental distributions
        ↓
empirical CDF at original droplet diameters
        ↓
direct Rosin–Rammler CDF fit
        ↓
shape + scale
        ↓
fit-quality and D50 diagnostics
```

---

## 1. Resolved Representation Decision

The measured distribution is discrete:

\[
\{d_i,w_i\},
\qquad
\sum_i w_i=1.
\]

A key ambiguity was whether the cumulative fraction should be associated with:

```text
point
    original measured diameter d_i

upper
    geometric upper bin edge
```

For logarithmically spaced diameter coordinates, the upper-edge interpretation shifts the CDF horizontally by an approximately constant scale factor.

A dedicated study fitted both conventions independently and evaluated their D50 agreement.

Against the distribution-reconstructed D50:

```text
point
    MAPE ≈ 4.59 %
    R²   ≈ 0.9985

upper
    MAPE ≈ 12.73 %
    R²   ≈ 0.9835
```

Against the reported experimental D50, the original-diameter convention also performed better.

### Decision

The stable empirical CDF is associated with the original `droplet_diameter` coordinates.

Geometric bin edges remain useful for PDF/bin visualization, but not for shifting the empirical CDF used in production fitting.

---

## 2. Resolved Estimator Decision

The direct CDF estimator minimizes:

\[
\min_{k,\lambda}
\sum_i
\left[
F_{RR}(d_i;k,\lambda)-F_i
\right]^2.
\]

A discrete-moment estimator was also investigated.

The moment route did not outperform direct CDF fitting for the selected objectives and was removed from the stable production workflow.

Therefore:

```text
direct CDF fit
    stable production estimator

moment estimator
    retired methodological diagnostic
```

The moment method should not be reintroduced into persisted production parameters without a new explicit scientific reason.

---

## 3. Stable D50 Interpretation

For a fitted Rosin–Rammler distribution:

\[
D_{50,fit}
=
\lambda(\ln2)^{1/k}.
\]

Three median quantities remain distinct:

```text
reported measured D50
distribution-reconstructed D50
Rosin–Rammler fitted D50
```

The distribution-reconstructed D50 is the primary reference for evaluating whether the analytical fit reproduces the stored distribution.

The reported `measured_d50` remains important because it is the experimental quantity used by SSDI and SSMD, but discrepancies between the two source representations must remain explicit rather than being silently corrected.

Current fitted-D50 agreement against distribution D50 is approximately:

```text
RMSE       = 0.025932 mm
MAE        = 0.016420 mm
MAPE       = 4.590485 %
R²         = 0.998529
Log-MSE    = 0.003792
R²_log     = 0.995474
```

---

## 4. Remaining Representation Limitation

The stable fit operates on the empirical CDF.

A PDF reconstruction is useful for inspecting local distribution shape, but it is not the fitting objective.

A good CDF fit can coexist with local PDF mismatch when the measured distribution contains:

```text
secondary peaks
broad tails
multimodality
isolated large-droplet populations
```

This distinction should remain explicit in future model-family comparisons.

---

## 5. Distribution-Family Benchmark

Rosin–Rammler is the stable reference family.

Future research may compare it with:

```text
Lognormal
Gamma
Generalized Gamma
mixture distributions
```

Evaluation should consider more than one metric:

```text
CDF RMSE
maximum CDF deviation
D50 error
shape / tail behaviour
regime dependence
```

Alternative families should be evaluated against the original measured CDF and should not replace Rosin–Rammler solely because they reduce an in-sample metric.

---

## 6. Shape Collapse

The next direct distribution question is whether most scale variation disappears after normalization by the experimental median:

\[
x=\frac{d}{D_{50}}.
\]

The normalized cumulative representation is:

\[
F(x)=F\left(\frac{d}{D_{50}}\right).
\]

The central question is:

> After removing characteristic droplet-size scale, how much systematic shape variation remains?

Possible outcomes include:

```text
near-universal collapse
treatment-specific collapse
regime-specific collapse
strong oil dependence
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

This diagnostic should precede any complicated `k` correlation.

---

## 7. Shape Parameter k

For the stable Rosin–Rammler fit, `k` controls distribution shape while `lambda` controls scale.

The next modelling question is whether fitted `k` behaves systematically with:

```text
dispersion mechanism
nozzle diameter
gas condition
SSMD treatment intensity
oil identity
```

The first stage should be descriptive rather than predictive.

Recommended diagnostics include:

```text
k distributions by regime
k by oil
k by gas condition
k by nozzle size
k vs normalized shape descriptors
```

---

## 8. Future k Correlation

The existing SSDI and SSMD workflows already provide characteristic droplet-size predictions.

For Rosin–Rammler:

\[
\lambda
=
\frac{D_{50}}
{(\ln2)^{1/k}}.
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

The principal future research target may become:

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

Candidate physical variables include:

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

## 9. Oil-Property Dependence

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

Because only ten oils are currently available, oil-property modelling must treat oil identity as the independent statistical unit rather than treating every experiment as an independent oil-property observation.

---

## 10. Scale and Gas Transfer

Shape behaviour may vary with:

```text
2 mm vs 3 mm nozzle
gas vs no gas
dispersion mechanism
oil identity
SSMD treatment intensity
```

No universal scale or gas correction should be assumed without validation.

Any predictive transfer model should remain separate from stable in-sample fitting.

---

## 11. Number-Based Representation

The measured distributions are volume-weighted.

A number-based representation may be constructed as:

\[
w_{N,i}
=
\frac{w_{V,i}/d_i^3}
{\sum_j w_{V,j}/d_j^3}.
\]

This transformation strongly emphasizes the smallest resolved droplets and is sensitive to:

```text
minimum measurable diameter
instrument detection limit
left truncation
binning convention
```

This route remains exploratory only.

---

## 12. Multimodal SSMD Distributions

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

Mixture modelling should not begin before large-droplet events are classified scientifically.

---

## 13. Validation Philosophy

Distribution modelling must preserve the distinction:

```text
fit quality
≠
sensitivity analysis
≠
predictive validation
```

The current direct-CDF result is an in-sample analytical representation of measured distributions.

A future transferable shape model should eventually use grouped validation by `oil_id`:

```text
hold out one oil
        ↓
fit shape model using remaining oils
        ↓
predict held-out oil distribution
        ↓
compare predicted and measured CDFs
```

Distribution-level validation should use more than D50 alone.

---

## 14. Updated Research Sequence

### Phase A — Stable representation

**Resolved.**

```text
original diameter coordinates selected
upper-edge CDF fitting rejected for production
moment estimator removed from stable workflow
direct CDF fit retained
```

### Phase B — Shape collapse

Study normalized distributions after removing D50 scale.

### Phase C — Shape parameter analysis

Characterize fitted `k` across treatments, oils, geometry, and gas condition.

### Phase D — Distribution-family benchmark

Compare alternative analytical families only if the stable Rosin–Rammler limitations justify it.

### Phase E — k correlation development

Identify parsimonious physical predictors for `k`.

### Phase F — Oil-property dependence

Evaluate whole-crude descriptors using oil-level statistics.

### Phase G — Predictive validation

Use grouped validation by oil and assess scale/gas transfer.

### Phase H — Field-scale reconstruction

Combine predicted D50 and predicted `k` to reconstruct the complete field-scale distribution.

---

## Research Boundary

The stable representation and fitting decisions are now closed.

Future research should build on them rather than repeatedly revisiting the point-versus-edge or direct-CDF-versus-moment questions without new evidence.

Open research remains exploratory until its scientific role and validation criteria are established.
