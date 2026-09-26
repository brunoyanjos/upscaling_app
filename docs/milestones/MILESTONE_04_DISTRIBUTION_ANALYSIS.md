# Milestone 4 — Droplet-Size Distribution Analysis

**Status:** In progress — diagnostic validation stage

## Objective

Reconstruct and validate the droplet-size distribution analysis workflow using the normalized database architecture established in Milestone 1.

The immediate goal is to verify that the normalized `distributions.xlsx` data reproduce the experimentally reported droplet-size descriptors before any analytical distribution fitting, parameter estimation, or upscaling model is introduced.

The workflow must preserve the project architecture:

```text
data selection
        ↓
descriptive distribution analysis
        ↓
consistency diagnostics
        ↓
statistical evaluation
        ↓
future distribution modelling / fitting
```

Raw spreadsheets remain confined to the database layer. The distribution analysis consumes only normalized databases.

---

## 4.1 Normalized Distribution Data

**Status:** Completed for the first diagnostic workflow

The normalized distribution database has the form:

```text
experiment_id
droplet_diameter
volume_fraction
```

Each distribution is linked to exactly one experiment through the deterministic `experiment_id`.

The corresponding experimental metadata are loaded from `experiments.xlsx`, including at least:

```text
experiment_id
oil_id
dispersion_tag
nozzle_diameter
has_gas
measured_d50
source_sheet
```

Internal units remain SI:

```text
droplet_diameter    m
measured_d50        m
volume_fraction     dimensionless
```

Current database inspection showed:

```text
180 distributions
52 diameter bins per distribution
common droplet-diameter grid across experiments
volume fractions approximately normalized to 1.0
```

Zero-valued bins are retained in the normalized database. They are not globally removed during analysis.

---

## 4.2 Current Package Structure

The current distribution-analysis workflow is organized under:

```text
src/upscaling_app/analysis/distributions/
├── __init__.py
├── data.py
├── descriptive.py
├── validation.py
├── reporting.py
├── plotting.py
└── pipeline.py
```

Responsibilities are separated as follows:

```text
data.py
    normalized database loading

descriptive.py
    distribution descriptors and quantiles

validation.py
    comparison against experiment-level reference values

reporting.py
    terminal diagnostics

plotting.py
    distribution and CDF diagnostics

pipeline.py
    workflow orchestration only
```

The CLI entry point is:

```bash
upscaling analyze distributions
```

---

## 4.3 Descriptive Distribution Metrics

**Status:** Implemented

For each `experiment_id`, the analysis currently evaluates:

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

```text
span = (D90 - D10) / D50
```

The current `d_peak` is defined directly from the normalized volume distribution:

```text
d_peak = droplet_diameter[argmax(volume_fraction)]
```

The weighted mean is:

```text
mean_diameter = sum(volume_fraction_i * diameter_i)
```

after normalization of the volume fractions.

---

## 4.4 Quantile Reconstruction

**Status:** Reconstructed and validated for most experiments

The experimentally reported `D50` is reconstructed from the cumulative volume distribution.

For a target quantile `q`, identify the two cumulative-distribution points surrounding the target:

```text
F0 < q <= F1
```

with corresponding diameters:

```text
d0, d1
```

The quantile is obtained by linear interpolation:

```text
dq = d0 + (q - F0) / (F1 - F0) * (d1 - d0)
```

For `D50`:

```text
q = 0.5
```

This method reproduces the reported `measured_d50` closely for the large majority of the dataset, usually with errors around or below approximately 1–2%.

This result is important because it validates:

```text
database loading
+
experiment_id linkage
+
diameter ordering
+
volume normalization
+
cumulative distribution construction
+
linear D50 interpolation
```

---

## 4.5 D50 Consistency Check

**Status:** Implemented

The analysis compares:

```text
measured_d50
vs.
D50 reconstructed from distributions.xlsx
```

The terminal report includes:

```text
oil_id
dispersion_tag
nozzle_mm
gas
measured_d50_mm
distribution_d50_mm
error_pct
d_peak_mm
d_peak_error_pct
source_sheet
```

where:

```text
error_pct =
    (distribution_d50 - measured_d50)
    / measured_d50 * 100
```

and:

```text
d_peak_error_pct =
    (d_peak - measured_d50)
    / measured_d50 * 100
```

The `d_peak_error_pct` is diagnostic only. It does not imply that `d_peak` should replace `D50`.

---

## 4.6 Current Suspicious Cases

A threshold of approximately 5% relative D50 error is currently used to flag cases for manual inspection.

The current suspicious set is:

```text
oil   tag             nozzle  gas   measured   calculated   error      d_peak
3016  WJ-40%          2 mm    no    0.1738     0.3512      +102.06%   0.8922 mm
3016  WJ-40%          2 mm    yes   0.4719     0.9893      +109.64%   1.2422 mm
4661  WJ-40%          2 mm    no    0.2277     0.6638      +191.52%   0.7561 mm
4662  WJ-40%          2 mm    no    0.2343     0.1885       -19.56%   0.1705 mm
4662  Untreated       2 mm    no    2.4080     2.7799       +15.45%   3.3535 mm
4662  SSDI-C9500      3 mm    no    0.7830     0.7388        -5.65%   1.7297 mm
4663  WJ-40%          2 mm    no    0.2519     0.6332      +151.39%   0.8922 mm
4665  WJ-40%          2 mm    no    0.3179     0.5397       +69.76%   0.6407 mm
4665  WJ-50%          3 mm    no    0.2664     0.6218      +133.45%   1.2422 mm
```

Most non-suspicious cases reproduce the reported D50 closely.

The concentration of severe discrepancies in selected SSMD cases, especially some `WJ-40%` experiments, indicates that the problem is not a systematic error in the reconstructed D50 algorithm.

---

## 4.7 Dpeak Diagnostic

**Status:** Tested — simple substitution hypothesis not supported

The SINTEF report states that, in some cases, large individual droplets can strongly influence the volume distribution and the calculated D50. It also states that when such droplets are associated with incomplete water jetting, the maximum peak of the distribution may be selected to represent the distribution.

A first diagnostic therefore compared the reported `measured_d50` with the current distribution `d_peak`.

The simple hypothesis:

```text
reported D50 ≈ d_peak
```

is not supported by the current suspicious cases.

For example:

```text
3016 WJ-40% no gas
measured D50 = 0.1738 mm
d_peak       = 0.8922 mm

4661 WJ-40% no gas
measured D50 = 0.2277 mm
d_peak       = 0.7561 mm

4665 WJ-40% no gas
measured D50 = 0.3179 mm
d_peak       = 0.6407 mm
```

Therefore, the report's reference to the maximum peak cannot currently be interpreted as a direct replacement of `D50` by `argmax(volume_fraction)` in the normalized distribution delivered to UDESC.

---

## 4.8 Diagnostic Plots

**Status:** Implemented for suspicious cases

The plotting workflow generates one diagnostic figure per suspicious experiment containing:

```text
1. measured volume distribution
2. cumulative volume distribution (CDF)
3. measured D50
4. reconstructed D50
5. d_peak
6. interpolation points used for D50
```

The diagnostic plots revealed that several discrepant SSMD distributions contain isolated or secondary peaks at large diameters capable of strongly shifting the cumulative volume distribution.

These plots are currently used for audit only and do not modify the underlying data.

---

## 4.9 Relevant SINTEF Methodology and Caveats

Review of the final SINTEF Wave Basin report identified several statements directly relevant to the suspicious distributions.

### Time-window selection

The SilCam workflow first evaluates image-level `d50` and total oil concentration. Time intervals are then selected for construction of representative average droplet-size distributions.

Therefore, the final distribution is already the result of a selected measurement window rather than a direct aggregation of every frame from the experiment.

### Large droplets in SSMD

SINTEF reports that some SSMD experiments contain large oil droplets, probably associated with oil-flow instability or incomplete water-jet treatment caused by jet misalignment.

Because the distribution is volume-weighted, a single large droplet can generate a significant peak.

The report states that these events are observed more frequently at lower water-jetting ratios.

### Treatment of large-droplet events

The report states that D50 was usually used to characterize the volume distribution, but that single large droplets could strongly influence the calculated D50.

For cases interpreted as incomplete water jetting, the maximum peak of the distribution could instead be selected to represent the distribution.

The report does not document an IQR-based filtering procedure or another explicit statistical outlier-removal algorithm.

### Challenging oils

The report also identifies oils such as 4662 and 4665 as experimentally challenging in some contexts and discusses measurement uncertainty for these oils.

These statements justify dedicated diagnostics but do not justify modifying the normalized data without traceable evidence.

---

## 4.10 Important Current Interpretation

The current evidence supports the following:

```text
1. The reconstructed D50 algorithm is correct for most experiments.

2. The large discrepancies are localized rather than systematic.

3. Several severe discrepancies occur in SSMD distributions with large secondary peaks.

4. Lower water-jetting conditions are explicitly identified by SINTEF as more susceptible to large-droplet events.

5. Direct substitution of measured D50 by the current d_peak does not reproduce the suspicious reported values.

6. No evidence has yet been found for an IQR-based filtering procedure.

7. The normalized database must remain unchanged while the discrepancy is investigated.
```

---

## 4.11 Next Diagnostic — CDF at Reported D50

**Status:** Next immediate task

The next diagnostic should evaluate the cumulative volume fraction at the SINTEF-reported `measured_d50`:

```text
p_reported = CDF(measured_d50)
```

For a fully consistent distribution:

```text
CDF(measured_d50) ≈ 0.50
```

For a suspicious case, this diagnostic will reveal which percentile the reported value actually represents in the normalized distribution.

Example interpretation:

```text
measured_d50 = 0.318 mm
CDF(0.318 mm) = 0.17
```

would mean that the reported value behaves approximately as a `D17` in the delivered distribution rather than a `D50`.

The analysis should add at least:

```text
cdf_at_measured_d50
reported_percentile
percentile_error = cdf_at_measured_d50 - 0.5
```

These fields should be included in both the suspicious-case terminal report and diagnostic plots.

---

## 4.12 Deferred Outlier Analysis

Outlier removal should not be introduced before the CDF diagnostic is completed.

If the discrepancy remains unexplained, the next investigation may include controlled sensitivity analyses such as:

```text
- removal of one large-diameter bin at a time;
- removal of combinations of a small number of bins;
- renormalization of the remaining volume fractions;
- recalculation of D50;
- comparison against measured_d50;
- IQR-based peak detection as a diagnostic only.
```

Any such operation must be treated as a diagnostic transformation, not as a modification of `distributions.xlsx`.

The purpose is to determine whether a reproducible data-treatment rule can explain the reported SINTEF D50 values.

---

## 4.13 Do Not Do Yet

Until the consistency issue is resolved:

```text
- do not delete zero bins from the normalized database;
- do not remove suspected outliers globally;
- do not overwrite measured_d50;
- do not overwrite reconstructed D50 with d_peak;
- do not alter experiment_id relationships;
- do not introduce a fitted analytical distribution as a workaround;
- do not use raw SINTEF spreadsheets directly inside the analysis pipeline.
```

---

## 4.14 Planned Continuation

When work resumes, continue in this order:

```text
1. Implement CDF(measured_d50).
2. Add the equivalent reported percentile to validation/reporting.
3. Re-run all 180 distributions.
4. Inspect suspicious cases, especially WJ-40% cases.
5. Compare results with SINTEF figures and source experiment metadata.
6. If necessary, perform controlled bin-removal sensitivity analysis.
7. Establish a documented policy for anomalous distributions.
8. Only after the database/distribution consistency audit is closed, reconstruct the analytical distribution model and fitting workflow.
```

The future modelling stage should remain separate from this experimental-data validation stage.

---

## Current Milestone Result

The normalized droplet-size distributions can now be loaded, summarized, plotted, and linked reproducibly to the experimental database.

The reconstructed cumulative-volume D50 agrees closely with the reported SINTEF value for most experiments, demonstrating that the normalized database and interpolation workflow are fundamentally correct.

A small subset of experiments shows major inconsistencies. The SINTEF report documents physical and procedural mechanisms that could explain at least part of this behavior, particularly large droplets from incomplete water jetting and measurement-window selection. However, the exact procedure used to obtain the reported D50 for the anomalous cases has not yet been reconstructed.

The next milestone action is therefore diagnostic rather than modelling: determine where each reported D50 lies on the delivered cumulative distribution before considering any outlier-removal or fitting strategy.
