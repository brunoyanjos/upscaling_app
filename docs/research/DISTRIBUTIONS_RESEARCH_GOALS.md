# Distribution Research Goals

## Status

**Research planning — active**

This document records the current scientific questions, hypotheses, methodological alternatives, and validation strategy for reconstructing and upscaling droplet-size distributions in the Upscaling App.

It is intentionally separate from the production modelling milestones.

The purpose is to preserve the research direction before committing to a definitive distribution-model architecture.

---

## 1. Scientific Objective

The central objective is to determine how experimentally measured droplet-size distributions can be represented, reconstructed, parameterized, and ultimately extrapolated consistently with the existing SSDI and SSMD upscaling pipelines.

The current SSDI and SSMD workflows already provide predictions of characteristic droplet size, particularly \(D_{50}\).

The unresolved question is:

> How should the complete droplet-size distribution be represented and predicted once the characteristic droplet scale has been extrapolated?

The distribution workflow should eventually provide a mapping of the form:

\[
\text{operating conditions}
\rightarrow
D_{50}
\rightarrow
\text{distribution shape}
\rightarrow
F(d)
\]

where \(F(d)\) is the predicted cumulative droplet-volume distribution.

A stronger future formulation may instead predict a small set of distribution parameters directly:

\[
\text{hydrodynamics + oil properties + treatment}
\rightarrow
\theta_{\text{distribution}}
\rightarrow
F(d).
\]

---

## 2. Current Experimental Distribution Data

The normalized distribution database currently stores:

```text
experiment_id
droplet_diameter
volume_fraction
```

The current dataset contains:

```text
180 distributions
52 diameter bins per distribution
common logarithmically spaced diameter grid
```

The measured distributions are volume-weighted.

Therefore, for each experiment:

\[
\sum_i w_i \approx 1,
\]

where \(w_i\) is the measured volume fraction associated with diameter bin \(i\).

The existing diagnostic workflow already reconstructs:

```text
D10
D50
D90
d_peak
volume-weighted mean
volume-weighted standard deviation
span
```

with:

\[
\text{span}
=
\frac{D_{90}-D_{10}}{D_{50}}.
\]

---

## 3. Reported \(D_{50}\) vs Distribution-Derived \(D_{50}\)

Most normalized distributions reproduce the experimentally reported \(D_{50}\) closely.

However, a small subset shows substantial disagreement between:

\[
D_{50,\mathrm{reported}}
\]

and

\[
D_{50,\mathrm{distribution}}.
\]

The suspicious cases are concentrated mainly in selected SSMD experiments, particularly low water-jetting conditions and oils that have also appeared as difficult cases in previous SSDI/SSMD analyses.

The current interpretation is:

```text
reported D50
≠
necessarily the D50 reconstructed from the delivered normalized distribution
```

Possible reasons include:

- selected experimental time windows;
- incomplete water jetting;
- large isolated droplets;
- secondary large-droplet peaks;
- measurement uncertainty;
- report-specific representative-value selection.

The normalized database must not be modified merely to enforce agreement.

A future sensitivity study may compare SSDI/SSMD results obtained using:

```text
reported D50
vs
distribution-derived D50
```

but this is currently lower priority because the discrepancy has little effect on the SSDI dataset and is concentrated mainly in specific SSMD cases.

---

## 4. Immediate Research Priority

The immediate priority is not to modify the upscaling models.

The first research question is:

> What mathematical representation of the measured discrete volume distribution provides the most faithful and useful basis for analytical distribution modelling?

The study should separate two distinct error sources:

```text
experimental discrete distribution
        ↓
representation / reconstruction error
        ↓
analytical-distribution fitting error
```

This distinction is essential.

A poor final fit can arise because:

1. the analytical family is inadequate; or
2. the discrete-to-continuous representation already distorted the experimental distribution.

---

# 5. Baseline Rosin–Rammler / Weibull Model

The initial analytical reference is the two-parameter Rosin–Rammler distribution, equivalent to a Weibull CDF:

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

Parameters:

```text
lambda    scale parameter
k         shape parameter
```

The corresponding PDF is:

\[
f(d)
=
\frac{k}{\lambda}
\left(
\frac{d}{\lambda}
\right)^{k-1}
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
\lambda
(\ln 2)^{1/k}.
\]

Therefore:

\[
\boxed{
\lambda
=
\frac{D_{50}}
{(\ln 2)^{1/k}}
}
\]

which has an important implication for future upscaling:

> If the existing SSDI or SSMD model predicts \(D_{50}\), only one additional independent shape descriptor may be required to reconstruct a two-parameter Rosin–Rammler distribution.

A natural candidate is \(k\).

---

## 6. Moment Relations

For the Weibull/Rosin–Rammler distribution:

\[
E[d^n]
=
\lambda^n
\Gamma
\left(
1+\frac{n}{k}
\right).
\]

Therefore:

\[
\mu
=
\lambda
\Gamma
\left(
1+\frac{1}{k}
\right)
\]

and:

\[
\sigma^2
=
\lambda^2
\left[
\Gamma
\left(
1+\frac{2}{k}
\right)
-
\Gamma^2
\left(
1+\frac{1}{k}
\right)
\right].
\]

The coefficient of variation satisfies:

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

Thus, \(k\) can be estimated numerically from the ratio between mean and standard deviation, followed by calculation of \(\lambda\).

This is the basis of the previous moment-matching implementation.

---

# 7. Distribution Representation Benchmark

Four baseline routes should be compared.

The benchmark should initially remain entirely in the **volume basis**.

---

## 7.1 Method A — Discrete Moments

The experimental distribution remains discrete:

\[
\{d_i,w_i\},
\qquad
\sum_iw_i=1.
\]

Moments are computed directly:

\[
M_n^{(D)}
=
\sum_i
w_i d_i^n.
\]

Therefore:

\[
\mu_D
=
\sum_i
w_i d_i
\]

and:

\[
\sigma_D^2
=
\sum_i
w_i
(d_i-\mu_D)^2.
\]

The Rosin–Rammler parameters are then obtained from these moments.

This method introduces no artificial continuous representation.

---

## 7.2 Method B — Continuous-Height Representation

This is the methodology used in the previous research script.

A piecewise-constant continuous function is constructed with height equal to the original discrete weight:

\[
g_H(d)=w_i
\]

over each interval.

The function is subsequently normalized:

\[
f_H(d)
=
\frac{g_H(d)}
{\int g_H(d)\,dd}.
\]

The effective probability mass associated with an interval therefore becomes:

\[
P_i
\propto
w_i\Delta d_i.
\]

Because the diameter grid is logarithmically spaced, larger-diameter bins have larger physical widths.

Therefore this transformation implicitly introduces an additional weighting by bin width.

This may change the experimental distribution substantially and must be treated as a modelling hypothesis rather than as a neutral interpolation.

The previous script also constructs intermediate diameters using arithmetic averaging:

\[
d_{i+1/2}
=
\frac{d_i+d_{i+1}}{2}.
\]

Because the experimental grid is logarithmic, a geometric alternative should also be evaluated:

\[
d_{i+1/2}
=
\sqrt{d_i d_{i+1}}.
\]

---

## 7.3 Method C — Mass-Preserving Continuous Representation

A continuous piecewise-constant PDF can instead be constructed while exactly preserving the original probability mass of each bin.

For bin \(i\):

\[
f_M(d)
=
\frac{w_i}
{\Delta d_i}.
\]

Then:

\[
\int_{b_{i-1/2}}^{b_{i+1/2}}
f_M(d)\,dd
=
w_i.
\]

Therefore:

\[
\int f_M(d)\,dd=1.
\]

This representation preserves the measured volume fraction exactly while allowing continuous integration.

For logarithmically spaced diameter centres, geometrically defined bin boundaries are natural candidates:

\[
b_{i+1/2}
=
\sqrt{d_i d_{i+1}}.
\]

This method should be considered the principal continuous baseline.

---

## 7.4 Method D — Direct CDF Fit

The experimental cumulative distribution is constructed directly:

\[
F_i
=
\sum_{j\le i} w_j.
\]

The Rosin–Rammler parameters are then determined by solving:

\[
\min_{k,\lambda}
\sum_i
\left[
F_{\mathrm{RR}}(d_i;k,\lambda)
-
F_i
\right]^2.
\]

This approach avoids estimating Rosin–Rammler parameters through moments.

Its role is important because it provides an approximate upper benchmark for the best fit achievable with a two-parameter Rosin–Rammler model.

It helps distinguish:

```text
poor Rosin–Rammler family
```

from:

```text
adequate Rosin–Rammler family
but poor parameter-estimation method
```

---

# 8. Error Decomposition

The benchmark must explicitly distinguish:

## Representation error

\[
E_{\mathrm{representation}}
=
\text{difference between the reconstructed representation and the original experimental CDF}.
\]

## Fitting error

\[
E_{\mathrm{fit}}
=
\text{difference between the fitted analytical model and the representation used for fitting}.
\]

## Total reconstruction error

\[
E_{\mathrm{total}}
=
\text{difference between the analytical model and the original experimental CDF}.
\]

This decomposition is necessary because the previous continuous-height method may produce:

```text
large discrete → continuous change
+
small continuous → Rosin–Rammler fitting error
```

which would otherwise appear simply as a poor Rosin–Rammler fit.

---

# 9. Benchmark Metrics

For every experiment and every modelling route, evaluate:

## CDF RMSE

\[
RMSE_F
=
\sqrt{
\frac{1}{N}
\sum_i
\left[
F_{\mathrm{model}}(d_i)
-
F_{\mathrm{exp}}(d_i)
\right]^2
}.
\]

## Maximum CDF deviation

\[
D_{\max}
=
\max_i
\left|
F_{\mathrm{model}}(d_i)
-
F_{\mathrm{exp}}(d_i)
\right|.
\]

This is conceptually similar to a Kolmogorov–Smirnov distance, although the current discrete weighted distributions are not necessarily being treated as classical random samples.

## Quantile errors

Evaluate:

\[
D_{10},
\qquad
D_{50},
\qquad
D_{90}.
\]

For each:

\[
\varepsilon_{D_q}
=
\frac{
D_{q,\mathrm{model}}
-
D_{q,\mathrm{exp}}
}{
D_{q,\mathrm{exp}}
}.
\]

## Moment errors

Compare:

\[
\mu,
\qquad
\sigma,
\qquad
CV.
\]

## Width / shape metrics

Compare:

\[
span
=
\frac{D_{90}-D_{10}}{D_{50}}.
\]

---

# 10. Initial Distribution Families

Rosin–Rammler should be the first reference model, but it should not be assumed a priori to be uniquely appropriate.

Candidate two-parameter families include:

```text
Rosin–Rammler / Weibull
Lognormal
Gamma
```

A later extension may include:

```text
Generalized Gamma
mixture distributions
```

The first scientific goal is not to select the distribution with the smallest in-sample error automatically.

The analysis should determine:

- whether one family represents all treatment regimes adequately;
- whether untreated, SSDI, and SSMD require different shape families;
- whether anomalous SSMD large-droplet peaks require multimodal models.

---

# 11. Shape Collapse

Before developing hydrodynamic correlations for distribution parameters, the distributions should be normalized by their median:

\[
x
=
\frac{d}{D_{50}}.
\]

The normalized cumulative distribution is then:

\[
F(x)
=
F
\left(
\frac{d}{D_{50}}
\right).
\]

The central question is:

> How much distribution-shape information remains after removing the characteristic diameter scale?

Possible outcomes:

## Universal collapse

\[
F(d)
\approx
F_0
\left(
\frac{d}{D_{50}}
\right).
\]

If this occurs, the existing \(D_{50}\) upscaling model may be almost sufficient to reconstruct the complete distribution.

## Treatment-specific collapse

Possible families:

```text
Untreated
SSDI
SSMD
```

or finer regime-dependent families.

## No useful collapse

Then an additional shape model is required.

Shape diagnostics should include:

\[
\frac{D_{10}}{D_{50}},
\qquad
\frac{D_{90}}{D_{50}},
\qquad
span,
\qquad
CV.
\]

---

# 12. Quantile-Based Reconstruction

A non-parametric alternative is to model the quantile function:

\[
Q(p)
=
F^{-1}(p).
\]

Normalize using:

\[
Q^*(p)
=
\frac{Q(p)}{D_{50}},
\]

so that:

\[
Q^*(0.5)=1.
\]

Candidate descriptors include:

\[
\frac{D_{10}}{D_{50}},
\qquad
\frac{D_{25}}{D_{50}},
\qquad
\frac{D_{75}}{D_{50}},
\qquad
\frac{D_{90}}{D_{50}}.
\]

This provides a useful non-parametric baseline against which analytical distributions can be judged.

Advantages:

- directly tied to the measured cumulative distribution;
- no assumption of a specific PDF family;
- preserves monotonicity;
- naturally compatible with the existing \(D_{50}\) upscaling framework.

---

# 13. Volume-Based vs Number-Based Distributions

The current experimental distributions are volume-weighted.

A second representation can be derived in terms of droplet number.

Assuming spherical droplets:

\[
V_i^{\mathrm{drop}}
=
\frac{\pi}{6}d_i^3.
\]

Therefore the number associated with a volume fraction is proportional to:

\[
N_i
\propto
\frac{w_{V,i}}{d_i^3}.
\]

The normalized number fraction is:

\[
\boxed{
w_{N,i}
=
\frac{
w_{V,i}/d_i^3
}{
\sum_j
w_{V,j}/d_j^3
}
}
\]

The inverse relation is:

\[
\boxed{
w_{V,i}
=
\frac{
w_{N,i}d_i^3
}{
\sum_j
w_{N,j}d_j^3
}
}
\]

This opens a second modelling route:

```text
measured volume distribution
        ↓
number distribution
        ↓
analytical model
        ↓
predicted number distribution
        ↓
reconstructed volume distribution
```

This may be useful because large droplets dominate volume-based distributions, whereas small droplets dominate number-based distributions.

It may therefore provide a clearer view of the primary droplet population when large isolated droplets strongly distort the volume distribution.

---

# 14. Important Limitation of Number-Based Reconstruction

The number transformation contains:

\[
d^{-3}.
\]

Therefore it strongly emphasizes the smallest resolved droplets.

This makes number-based statistics highly sensitive to:

```text
minimum measurable diameter
instrument detection limit
left truncation
binning convention
```

The experimental distribution does not represent droplets down to \(d=0\).

Therefore the correct interpretation is a truncated distribution:

\[
F_N(d\mid d\ge d_{\min}).
\]

Any number-based model must keep the instrumental lower cutoff explicit.

Number-based \(D_{50}\), moments, or fitted parameters should not be interpreted as unrestricted population quantities unless sub-resolution droplets are independently modelled.

---

# 15. Number-Based Rosin–Rammler and Return to Volume

If a Weibull/Rosin–Rammler model is assumed in the number basis:

\[
f_N(d)
=
\frac{k}{\lambda}
\left(
\frac{d}{\lambda}
\right)^{k-1}
\exp
\left[
-\left(
\frac{d}{\lambda}
\right)^k
\right],
\]

then conversion to a volume-weighted PDF gives:

\[
f_V(d)
=
\frac{
d^3 f_N(d)
}{
E_N[d^3]
}.
\]

Since:

\[
E_N[d^3]
=
\lambda^3
\Gamma
\left(
1+\frac{3}{k}
\right),
\]

the resulting volume PDF becomes:

\[
f_V(d)
=
\frac{
k
}{
\lambda^{k+3}
\Gamma(1+3/k)
}
d^{k+2}
\exp
\left[
-\left(
\frac{d}{\lambda}
\right)^k
\right].
\]

This is not another two-parameter Weibull distribution in the volume basis.

It has the form of a generalized-gamma distribution.

This suggests an important future hypothesis:

> A simple parametric model in the number basis may generate a more flexible and physically useful volume distribution after transformation.

This should be tested rather than assumed.

---

# 16. Multimodal SSMD Distributions

Some suspicious SSMD distributions contain:

```text
primary droplet population
+
secondary large-droplet population
```

Possible physical/procedural causes include:

- incomplete water-jet treatment;
- jet misalignment;
- intermittent large droplets;
- oil-flow instability;
- selected experimental windows.

A single two-parameter Rosin–Rammler distribution is fundamentally unimodal.

If the secondary populations represent genuine reproducible physics, later models may require mixtures such as:

\[
F(d)
=
\alpha F_1(d)
+
(1-\alpha)F_2(d).
\]

However, mixture modelling should not begin before determining whether the large-droplet populations should be considered part of the representative treatment distribution.

---

# 17. Relation to Existing Upscaling Models

The existing SSDI and SSMD workflows already provide characteristic droplet-size predictions.

A natural future formulation is therefore:

\[
D_{50,\mathrm{pred}}
+
k_{\mathrm{pred}}
\rightarrow
\lambda_{\mathrm{pred}}
\rightarrow
F(d).
\]

For a Weibull/Rosin–Rammler model:

\[
\lambda
=
\frac{
D_{50}
}{
(\ln2)^{1/k}
}.
\]

Thus the main new modelling task may reduce to predicting one shape parameter:

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

Candidate variables may include:

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

This analysis should begin only after the representation problem is resolved.

---

# 18. Modified-Weber Circularity Risk

The current modified-Weber diagnostic contains \(D_{50}/D\):

\[
We^*
=
\frac{
We
}{
1
+
B\,Ca
\left(
D_{50}/D
\right)^{1/3}
}.
\]

Therefore:

```text
modified Weber
is not independent of D50
```

A correlation such as:

\[
\lambda=f(We^*)
\]

may become circular if experimental \(D_{50}\) is used inside \(We^*\) and \(\lambda\) is itself strongly determined by \(D_{50}\).

This does not mean that modified Weber is unusable.

It means that future correlation development must distinguish:

```text
consistency diagnostics
```

from:

```text
independent predictive inputs
```

A shape parameter such as \(k\), or dimensionless ratios such as:

\[
\frac{D_{90}}{D_{50}},
\qquad
\frac{D_{10}}{D_{50}},
\]

may be more appropriate initial response variables.

---

# 19. Validation Philosophy

Distribution modelling must preserve the same distinction already adopted in SSDI and SSMD:

```text
fit quality
≠
sensitivity analysis
≠
predictive validation
```

A model may reproduce all 180 measured distributions well in sample and still fail for a new oil.

Eventually, any model intended to transfer across oils should use grouped validation by `oil_id`.

A future validation loop may be:

```text
hold out one oil
        ↓
fit distribution-shape model using remaining oils
        ↓
predict held-out oil distribution
        ↓
compare complete predicted and measured CDFs
```

Evaluation should use distribution-level metrics rather than only \(D_{50}\).

---

# 20. Proposed Research Sequence

## Phase A — Volume-Distribution Representation Benchmark

**Current priority**

Compare:

```text
A. discrete moments
B. continuous-height representation
C. mass-preserving continuous representation
D. direct CDF fit
```

using Rosin–Rammler as the first analytical family.

Evaluate all 180 distributions.

Outputs:

```text
k
lambda
CDF RMSE
maximum CDF deviation
D10 error
D50 error
D90 error
mean error
standard-deviation error
span error
```

Generate detailed diagnostic plots for representative:

```text
Untreated
SSDI
SSMD
anomalous SSMD cases
```

Do not modify the production database.

---

## Phase B — Distribution-Family Benchmark

Compare at least:

```text
Rosin–Rammler / Weibull
Lognormal
Gamma
```

against the original experimental CDF.

Evaluate whether model preference depends on:

```text
Untreated
SSDI
SSMD
gas condition
SSMD regime
oil identity
```

Consider generalized gamma only if simpler models are insufficient.

---

## Phase C — Shape-Collapse Analysis

Normalize:

\[
d^*
=
\frac{d}{D_{50}}.
\]

Evaluate whether distributions collapse:

```text
globally
by treatment
by regime
by oil
```

Analyze:

\[
D_{10}/D_{50},
\quad
D_{90}/D_{50},
\quad
span,
\quad
CV.
\]

Determine whether predicting \(D_{50}\) alone is nearly sufficient or whether a shape model is necessary.

---

## Phase D — Number-Basis Analysis

Convert the measured volume distribution to a number-weighted representation:

\[
w_N
\propto
w_V/d^3.
\]

Compare:

```text
volume PDF/CDF
number PDF/CDF
```

for typical and anomalous distributions.

Study:

```text
D10_N
D50_N
D90_N
span_N
instrument-cutoff sensitivity
```

Keep the minimum measurable diameter explicit.

---

## Phase E — Number-Basis Parametric Reconstruction

Test:

```text
volume experimental
        ↓
number conversion
        ↓
Rosin–Rammler / alternative model in number basis
        ↓
volume reconstruction
```

Compare the reconstructed volume distribution against the original measured volume distribution.

This phase directly tests whether fitting in number space produces a better volume-space reconstruction.

---

## Phase F — Distribution-Shape Upscaling

Once the best representation/model is established, investigate correlations for shape.

Potential target:

\[
k
\]

or a non-parametric equivalent such as:

\[
D_{90}/D_{50}.
\]

Investigate hydrodynamic and oil-property dependence.

Maintain explicit separation between:

```text
SSDI shape model
SSMD shape model
Untreated reference shape
```

unless evidence supports a shared formulation.

---

## Phase G — Predictive Validation

Use grouped validation by oil.

Primary target:

```text
complete predicted distribution
```

not only characteristic diameters.

Metrics should include:

```text
CDF RMSE
maximum CDF deviation
D10 error
D50 error
D90 error
shape-parameter error
```

---

## Phase H — Production Architecture

Only after the research questions above are sufficiently resolved should the production package be reorganized around the selected methodology.

A possible future architecture may contain:

```text
upscaling/distributions/
    models/
    fitting/
    prediction/

analysis/distributions/
    consistency/
    representation/
    model_comparison/
    shape/
    validation/
```

This structure is intentionally deferred.

The research should determine the architecture, rather than forcing the research into a premature architecture.

---

# 21. Immediate Next Study

The immediate next task is:

> Benchmark the four volume-based Rosin–Rammler reconstruction routes using the 180 normalized experimental distributions.

Specifically:

```text
1. implement discrete-moment RR estimation
2. reproduce the existing continuous-height method
3. implement mass-preserving continuous reconstruction
4. implement direct CDF fitting
5. evaluate all four against the original experimental CDF
6. separate representation error from fitting error
7. compare D10, D50, D90, moments and span
8. inspect representative and anomalous distributions visually
```

No SSDI/SSMD structural changes are required for this stage.

No number-based reconstruction should replace the volume benchmark before the latter is understood.

---

# 22. Current Working Principle

The distribution study should proceed in the following order:

```text
understand the measured distribution
        ↓
understand discrete vs continuous representation
        ↓
understand analytical-family adequacy
        ↓
understand volume vs number representation
        ↓
identify stable shape descriptors
        ↓
develop shape-upscaling hypotheses
        ↓
perform predictive validation
        ↓
stabilize production architecture
```

The immediate research goal is therefore methodological rather than architectural.

