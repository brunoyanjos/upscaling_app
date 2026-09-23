# Research Plan — SSMD Upscaling and Full-Scale Correlation Development

## Status

**Exploratory research — separated from the reconstructed SSMD production pipeline.**

This document records the scientific questions, hypotheses, diagnostic experiments, negative results, and promising directions identified while reconstructing the SSMD workflow.

The purpose is to preserve the research path without allowing exploratory formulations to modify the validated SINTEF baseline used by the production application.

---

## 1. Central Research Question

The reconstructed SINTEF SSMD model predicts:

```text
dR = d50_treated / d50_untreated
```

The production SINTEF correlation uses:

```text
dR = (eta A_M)^(-3/5) * (c + d mu/sigma)
```

The practical full-scale problem is that:

```text
eta
c
d
```

are empirical coefficients rather than quantities that can currently be computed directly from an arbitrary full-scale release.

Central question:

> Can the SSMD droplet-size reduction be reformulated using measurable physical quantities so that prediction does not require condition-specific empirical coefficients?

---

## 2. Why the Existing SINTEF Formulation Does Not Fully Close the Scale-Up Problem

The SINTEF momentum amplification is:

```text
A_M = (M_o + M_w) / M_o
```

The effective momentum is represented through:

```text
M_E = eta (M_o + M_w)
```

The efficiency factor conceptually accounts for incomplete water-jet entrainment caused by:

```text
multiple-water-jet interaction
jet misalignment
cavitation
practical nozzle effects
other entrainment losses
```

The report uses different empirical parameter sets for:

```text
3 mm — no gas
2 mm — no gas
2 mm — gas
```

Therefore the existing formulation does not yet provide a universal mapping:

```text
full-scale operating conditions
        ↓
eta, c, d
        ↓
dR
```

---

## 3. Reconstructed SINTEF Reference

### Equation 5

```text
dR = (eta A_M)^(-3/5)
```

Current SINTEF values:

```text
eta no gas = 0.85
eta gas    = 0.68
Log-MSE    = 0.7167120356
```

### Equation 6

```text
dR = (eta A_M)^(-3/5) * (c + d mu/sigma)
```

Reference reconstruction:

```text
Log-MSE = 0.1287225708
```

---

## 4. Eta Alone Cannot Repair Equation 5 Physically

Allowing separate no-gas and gas efficiencies while preserving the -3/5 exponent produced:

```text
eta no gas = 3.895524
eta gas    = 1.438594
Log-MSE    = 0.0931491922
```

If eta is interpreted as momentum-transfer efficiency, values above one are not physically admissible.

Conclusion:

> Missing SSMD structure cannot be represented only by a physically bounded eta.

---

## 5. Free Momentum Exponent

Diagnostic model:

```text
dR = (eta_g A_M)^n
```

with:

```text
0 < eta <= 1
```

Result:

```text
eta no gas = 1.000000
eta gas    = 0.578041
n          = -0.899785
Log-MSE    = 0.0912343510
```

Residual correlations after this fit were approximately:

```text
kinetic_power_ratio       +0.024
water_velocity            -0.008
water_momentum_flux       +0.052
momentum_amplification    +0.013
untreated_d50_pred        +0.090
oil_viscosity             +0.236
untreated_ift             -0.289
has_gas                   +0.001
```

This showed that a stronger hydrodynamic response than -3/5 removes most of the water-jet and gas structure from the residuals.

However, the exponent was empirical.

---

## 6. Untreated-Scale Correction

A multiplicative untreated-scale correction gave:

```text
eta no gas = 1.000000
eta gas    = 1.000000
alpha      = -0.269152
S_ref      = 1.682496e-03 m
Log-MSE    = 0.5482720607
```

Conclusion:

> Untreated droplet scale alone does not explain the missing SSMD response.

---

## 7. Ohnesorge Correction

The dimensionless group:

```text
Oh = mu / sqrt(rho sigma d50_untreated)
```

was tested through:

```text
dR =
    (eta_g A_M)^n
    (Oh / Oh_ref)^beta
```

In-sample result:

```text
eta no gas = 1.000000
eta gas    = 0.607448
n          = -0.893488
beta       = +0.071456
Oh_ref     = 1.042182e-01
Log-MSE    = 0.0853350507
```

### Leave-one-oil-out

```text
fitted exponent             Log-MSE = 0.105831
fitted exponent + Ohnesorge Log-MSE = 0.107966
```

The Ohnesorge model improved 7 of 10 held-out oils but worsened global generalization, mainly because of oil 4665.

Conclusion:

> Oh improves in-sample fitting but is not currently supported as a generalization improvement.

---

## 8. Wang–Calabrese / Johansen Physical Route

A physical route was explored based on a breakup balance of the form:

```text
E_disruptive ~ E_IFT + E_viscous
```

and the Johansen-style characteristic droplet relation:

```text
d50/D =
    A We^(-3/5)
    [1 + B Vi (d50/D)^(1/3)]^(3/5)
```

with:

```text
Vi = mu U / sigma
```

This provides a physically motivated coupling between viscosity and IFT.

---

## 9. Relative Wang–Calabrese SSMD Hypothesis

Define:

```text
x_U = d50_untreated / D
x_T = dR x_U
G   = We_treated / We_untreated
```

Initial SSMD hypothesis:

```text
G = 1 + eta (A_M - 1)
```

Dividing treated and untreated Wang–Calabrese relations removes coefficient A.

### Important correction

An initial assumption:

```text
Vi_T = Vi_U sqrt(G)
```

was rejected because it interprets the added water-jet action as an increase in oil nozzle exit velocity.

The corrected diagnostic assumption was:

```text
Vi_T = Vi_U
```

---

## 10. Sensitivity to B

With:

```text
eta = 1
Vi_T = Vi_U
```

the sensitivity was:

```text
B = 0.0000000    Log-MSE = 0.5527896843
B = 0.0620713    Log-MSE = 0.5232156486
B = 0.0800000    Log-MSE = 0.5163970478
B = 0.8000000    Log-MSE = 0.3972026631
```

A broader logarithmic sweep showed monotonic improvement as B increased.

The objective approached an asymptotic limit instead of identifying a finite optimum.

---

## 11. Wang–Calabrese Viscous Limit

For:

```text
B -> infinity
```

the relative model reduces analytically to:

```text
dR = G^(-3/4)
```

With:

```text
eta = 1
G = A_M
```

this becomes:

```text
dR = A_M^(-3/4)
```

Reference result:

```text
exponent = -0.750000
Log-MSE  = 0.2088209306
```

This explains part of the empirical shift from -0.60 toward approximately -0.90, but not all of it.

---

## 12. Residual Structure of the Viscous Limit

For:

```text
dR = A_M^(-3/4)
```

residual correlations were:

```text
momentum_amplification    -0.488028
water_momentum_flux       -0.545637
kinetic_power_ratio       -0.519920
oil_viscosity             +0.363708
untreated_ift             -0.224806
untreated_d50_pred        -0.148395
has_gas                   +0.647674
```

Separate residual slopes:

```text
no gas:
effective exponent = -0.842420

gas:
effective exponent = -0.909039
```

Conclusion:

> Gas modifies more than the overall water-jet intensity represented by A_M.

---

## 13. Global Momentum and Kinetic-Power Regression

### Momentum amplification

```text
all:
R² = 0.531096

2 mm — no gas:
R² = 0.301935

3 mm — no gas:
R² = 0.106541

2 mm — gas:
R² = 0.168691
```

### Kinetic-power ratio

```text
all:
R² = 0.561719

2 mm — no gas:
R² = 0.309994

3 mm — no gas:
R² = 0.077034

2 mm — gas:
R² = 0.135488
```

The stronger global relationships are partly produced by separation among experimental regimes rather than by a universal within-regime law.

---

## 14. Within-Group Analysis

Data were centered within:

```text
oil_id
nozzle_diameter
has_gas
```

using:

```text
delta log X =
    log X - mean_group(log X)

delta log dR =
    log dR - mean_group(log dR)
```

Results:

```text
momentum_amplification
slope = -0.828340
R²    = 0.600321

water_momentum_flux
slope = -0.760904
R²    = 0.598645

water_kinetic_power
slope = -0.507270
R²    = 0.598645

kinetic_power_ratio
slope = -0.507962
R²    = 0.597052

water_velocity
slope = -1.521809
R²    = 0.598645

water_flow
slope = -1.521809
R²    = 0.598645
```

---

## 15. Experimental Identifiability Limitation

Within a fixed oil / nozzle / gas condition:

```text
U_w proportional to Q_w
M_w proportional to Q_w²
P_w proportional to Q_w³
```

The fitted exponents confirm this:

```text
water_flow slope          = -1.521809
water_velocity slope      = -1.521809
water_momentum slope      = -0.760904
                           ≈ -1.521809 / 2
water kinetic power slope = -0.507270
                           ≈ -1.521809 / 3
```

Therefore the current campaign cannot statistically distinguish whether the controlling treatment variable is fundamentally:

```text
water flow
water velocity
water momentum
water kinetic power
```

because these variables were not varied independently.

This is a central limitation for full-scale correlation development.

---

## 16. Current Scientific Interpretation

### Supported

1. Increasing water-jet intensity reduces relative droplet size within a fixed oil / geometry / gas regime.
2. The response is substantial and approximately monotonic.
3. Oil / gas / geometry create systematic offsets between regimes.
4. The surface-controlled -3/5 scaling is too weak for the current multi-oil SSMD dataset.
5. The Wang–Calabrese viscous limit -3/4 explains part, but not all, of the stronger response.
6. Gas-containing experiments behave systematically differently from no-gas experiments.
7. Viscosity and IFT remain physically relevant.

### Not yet identifiable

The current data do not uniquely determine whether the fundamental treatment-intensity variable should be:

```text
A_M
M_w
P_w
Q_w
U_w
```

The current data also do not identify a universal full-scale relationship for:

```text
eta
c
d
```

or an equivalent new coefficient set.

---

---

## 17. Fixed-Nozzle Eta Diagnostic

To reduce geometric confounding, a diagnostic was performed using only the 2 mm oil-nozzle experiments.

The comparison used:

```text
2 mm — no gas
2 mm — gas
```

while preserving the original water-jet fractions.

### Equation 5

Fitting only \(\eta\) in:

\[
d_R = (\eta A_M)^{-3/5}
\]

gave:

```text
no gas:
eta     = 4.057656
Log-MSE = 0.0802691551

gas:
eta     = 1.438562
Log-MSE = 0.1172179409

eta_gas / eta_no_gas = 0.354530
```

The fitted efficiencies are not physically admissible if \(\eta\) is interpreted as a transfer efficiency bounded by one.

### Equation 6 with SINTEF c and d

Keeping the SINTEF oil-property correction and fitting only \(\eta\) gave:

```text
no gas:
eta     = 1.401769
Log-MSE = 0.1060019867

gas:
eta     = 0.813193
Log-MSE = 0.0841622080

eta_gas / eta_no_gas = 0.580120
```

The SINTEF reference ratio is:

```text
0.68 / 0.85 = 0.800000
```

Using the published SINTEF efficiencies on the same 2 mm subsets gave:

```text
no gas Log-MSE = 0.1960933618
gas    Log-MSE = 0.0956810149
```

Conclusion:

> Fixing the oil-nozzle diameter at 2 mm does not recover the SINTEF gas/no-gas efficiency ratio.

This reinforces the interpretation that \(\eta\), \(c\), and \(d\) act as condition-dependent empirical parameters rather than independently transferable physical constants.

---

## 18. Paired 2 mm Gas / No-Gas Analysis

A more controlled comparison was then constructed by pairing experiments with:

```text
same oil_id
same 2 mm oil-nozzle diameter
same nominal water-jet fraction
```

for the gas and no-gas cases.

This produced:

```text
10 oils
3 water-jet fractions per oil
30 matched pairs
```

The direct gas-response factor was defined as:

\[
G_{\mathrm{gas}}
=
\frac{d_{R,\mathrm{gas}}}
{d_{R,\mathrm{no\ gas}}}.
\]

A value greater than one means that, for the matched condition, the gas case retains a larger relative droplet diameter and SSMD is therefore less effective.

The corresponding Equation-5-implied efficiency ratio is:

\[
\frac{\eta_g}{\eta_n}
=
\frac{A_{M,n}}{A_{M,g}}
\left(
\frac{d_{R,g}}{d_{R,n}}
\right)^{-5/3}.
\]

### Global paired result

The paired analysis gave:

```text
number of pairs        = 30

mean dR gas/no-gas     = 2.535915
median dR gas/no-gas   = 2.176210
std dR gas/no-gas      = 1.116119

mean eta gas/no-gas    = 0.484732
median eta gas/no-gas  = 0.386178
std eta gas/no-gas     = 0.441232

SINTEF eta ratio       = 0.800000
```

Therefore a universal SINTEF-like gas factor was not recovered.

### By water-jet fraction

The implied efficiency ratio was:

```text
40%:
mean   = 0.553207
median = 0.390023

45%:
mean   = 0.547287
median = 0.386178

50%:
mean   = 0.353700
median = 0.292495
```

The gas effect is therefore neither close to the SINTEF ratio of 0.8 nor constant across treatment intensity.

---

## 19. Oil Dependence of the Gas Effect

The paired results showed that the gas response varies strongly among oils.

A single representative value per oil was defined as:

\[
G_{\mathrm{gas,oil}}
=
\operatorname{median}_{40,45,50\%}
\left(
\frac{d_{R,g}}{d_{R,n}}
\right).
\]

The resulting factors were:

```text
oil    median gas factor

3014   1.966084
3015   2.163655
3016   4.586469
4661   2.398404
4662   3.481991
4663   1.301073
4664   1.730806
4665   0.853226
4666   3.780385
4667   2.439912
```

The range:

```text
0.853226 to 4.586469
```

is too large to support a single oil-independent multiplicative gas correction.

Oil 4665 is especially distinct: for the 40% and 45% pairs, the gas case had a smaller \(d_R\) than the corresponding no-gas case.

### Univariate oil-property associations

Using the per-oil median gas factor as the target gave:

```text
oil_viscosity:
R²       = 0.402382
Pearson  = 0.634336
Spearman = 0.696970

oil_density:
R²       = 0.465999
Pearson  = 0.682641
Spearman = 0.660606

untreated_ift:
R²       = 0.112644
Pearson  = -0.335625
Spearman = -0.175758

untreated_d50_measured:
R²       = 0.254029
Pearson  = 0.504013
Spearman = 0.689037

untreated_d50_pred:
R²       = 0.077220
Pearson  = -0.277885
Spearman = -0.127273

Ohnesorge:
R²       = 0.349752
Pearson  = 0.591399
Spearman = 0.418182
```

Density and viscosity were therefore the strongest simple associations among the tested variables.

However, they must not yet be interpreted as independently causal because the available oil properties are themselves correlated across the small set of ten oils.

---

## 20. Leave-One-Oil-Out Robustness of the Gas-Property Associations

A leave-one-oil-out correlation sensitivity test was performed by repeatedly removing one oil and recomputing the association between the gas factor and each oil property.

### Oil viscosity

```text
R²:
min  = 0.233870
max  = 0.498834
mean = 0.402493

Pearson:
min  = 0.483601
max  = 0.706282
mean = 0.631400

Spearman:
min  = 0.583333
max  = 0.816667
mean = 0.691667
```

The sign remained positive for every omitted oil.

### Oil density

```text
R²:
min  = 0.319510
max  = 0.510459
mean = 0.470429

Pearson:
min  = 0.565252
max  = 0.714464
mean = 0.684590

Spearman:
min  = 0.566667
max  = 0.800000
mean = 0.653333
```

Density showed the most stable univariate linear association in log space.

### Ohnesorge number

```text
R²:
min  = 0.127596
max  = 0.450521
mean = 0.348121

Pearson:
min  = 0.357206
max  = 0.671208
mean = 0.583634

Spearman:
min  = 0.200000
max  = 0.533333
mean = 0.415000
```

The Ohnesorge association remained positive but was weaker and less rank-stable.

### IFT and untreated predicted d50

These variables did not show robust associations across leave-one-oil-out sensitivity tests.

The measured untreated \(d_{50}\) showed a stronger monotonic association than its global \(R^2\) suggests, but its leave-one-oil-out \(R^2\) was highly sensitive to oil 4665.

---

## 21. Predictive Gas-Factor Models

To determine whether density and viscosity carry transferable information rather than only in-sample correlation, three parsimonious models were compared:

\[
M_1:
\log G_{\mathrm{gas}}
=
a + b\log\mu,
\]

\[
M_2:
\log G_{\mathrm{gas}}
=
a + b\log\rho,
\]

and:

\[
M_3:
\log G_{\mathrm{gas}}
=
a + b\log\mu + c\log\rho.
\]

Each model was evaluated using leave-one-oil-out prediction: nine oils were used to fit the model and the omitted oil was predicted.

### Full-data fits

```text
viscosity:
R² = 0.402382
slope = 0.344553

density:
R² = 0.465999
slope = 9.794143

viscosity + density:
R² = 0.480209
viscosity slope = 0.116866
density slope   = 7.224319
```

The very large density exponent must not be interpreted as a validated physical power law. Density spans a relatively narrow range in the present database, while the gas factor varies substantially.

### Leave-one-oil-out prediction

```text
model                 Log-MSE      Log-RMSE

density               0.19058994   0.43656608
viscosity             0.21643318   0.46522380
viscosity + density   0.25056220   0.50056188
```

Therefore:

```text
combined - viscosity = +0.03412902
combined - density   = +0.05997225
```

Adding viscosity to the density model improved the in-sample \(R^2\) but degraded out-of-oil prediction.

Conclusion:

> Density was the strongest univariate predictor of the oil-dependent gas factor among the tested properties, with viscosity also carrying reproducible information. Combining both variables was not supported by leave-one-oil-out validation.

This result should be treated as an exploratory oil-property association, not as a validated physical closure.

---

## 22. Updated Scientific Interpretation

### Supported by the current exploratory analysis

1. Increasing water-jet intensity reduces relative droplet size within a fixed oil / geometry / gas regime.
2. The response is approximately monotonic but the current experimental design cannot distinguish water flow, velocity, momentum, and power as independent controlling variables.
3. The surface-controlled \(-3/5\) momentum scaling is too weak for the present multi-oil SSMD dataset.
4. The Wang–Calabrese viscous limit \(-3/4\) provides a physically motivated part of the stronger observed response.
5. Gas-containing and no-gas experiments cannot be collapsed through a single universal efficiency ratio.
6. The magnitude of the gas effect depends strongly on oil identity.
7. Oil density and viscosity show robust exploratory associations with the oil-dependent gas response.
8. A two-property density-viscosity model is not supported by out-of-oil validation.
9. The available data do not yet identify a universal full-scale gas-correction law.

### Not yet identifiable

The current data do not uniquely determine:

```text
- the fundamental water-jet intensity variable;
- a universal eta;
- a universal gas/no-gas efficiency ratio;
- a physically validated density exponent;
- an independent density effect versus correlated oil-property effects;
- a closed full-scale gas-response correlation.
```

---

## 23. Full-Scale Closure Problem

A predictive full-scale model should ideally have the form:

```text
dR =
    F(
        water-jet intensity,
        oil properties,
        gas,
        geometry
    )
```

where every input can be evaluated for an unseen release.

The current evidence suggests that the gas correction is itself oil dependent:

```text
gas response =
    G_gas(oil properties, gas condition, geometry)
```

rather than a universal constant.

The unresolved closure therefore includes both:

```text
water-jet treatment efficiency
gas / liquid interaction efficiency
```

and their dependence on oil properties and geometry.

A conceptual future representation could involve variables such as:

```text
rho_w U_w² / (rho_o U_o²)
D_w / D_o
gas fraction
oil density
oil viscosity
number of jets
jet angle
jet spacing
```

but the current campaign does not vary enough of these quantities independently to calibrate such a model robustly.

---

## 24. Recommended Future Experimental Design and Validation

A future campaign intended for correlation development should vary candidate controls independently.

High-value variables include:

```text
water nozzle diameter
water flow
water velocity
number of water jets
jet angle
water-jet / oil-jet spacing
oil nozzle diameter
oil flow
gas fraction
oil viscosity
oil density
interfacial tension
```

Independent variation of water-nozzle diameter, water flow, gas fraction, and oil properties would help separate:

```text
flow-rate effects
velocity effects
momentum effects
power effects
gas effects
oil-property effects
```

Any future model intended to generalize to unseen oils should be validated by `oil_id`.

Minimum requirement:

```text
leave-one-oil-out
```

If model structure, variables, or hyperparameters are selected using the available oils, the final study should use:

```text
nested grouped validation
```

Experiment-level random splitting is not appropriate for evaluating generalization to new oils.

---

## 25. Research Boundary and Current Status

The exploratory phase has now reached a useful stopping point.

The production SSMD pipeline must preserve:

```text
SINTEF reference equations
explicit model versions
reproducible reference results
```

The exploratory findings must not replace the reconstructed baseline solely because they reduce in-sample error.

The current research findings can be summarized as:

```text
- clear within-condition SSMD response;
- strong experimental-regime dependence;
- incomplete surface-controlled momentum scaling;
- partial physical explanation through the viscous breakup limit;
- no universal SINTEF-like gas efficiency ratio;
- strong oil dependence of the gas effect;
- exploratory density and viscosity associations with gas response;
- density gives the best tested univariate LOO gas-factor prediction;
- adding viscosity to density worsens LOO prediction;
- insufficient independent experimental variation for physical closure;
- no validated universal full-scale SSMD parameterization yet.
```

No additional empirical term should be added solely to improve fit at this stage.

---

## 26. Next Research Step

Research should resume only after the production SSMD reconstruction is completed and frozen.

Recommended sequence:

```text
1. Treat the reconstructed SINTEF model as the reference.
2. Define the exact full-scale prediction target and available inputs.
3. Map which SINTEF terms are directly computable and which remain unclosed.
4. Treat the gas effect as potentially oil dependent rather than as a fixed efficiency ratio.
5. Revisit treatment efficiency from jet-interaction and gas-liquid interaction physics.
6. Inventory external experimental datasets with independently varied
   water-jet geometry, gas fraction, and oil properties.
7. Test whether the observed density / viscosity associations persist
   outside the current ten-oil dataset.
8. Only then propose a parsimonious new scale-up correlation.
9. Validate with grouped / nested cross-validation.
```

The main unresolved scientific question is no longer:

> Which empirical regression gives the smallest error?

It is:

> Which measurable physical variables explain both treatment efficiency and the oil-dependent gas response strongly enough to support full-scale SSMD extrapolation?
