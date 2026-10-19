# Project Context

## Purpose

The project develops a reproducible scientific Python workflow for processing, modelling, predicting, and analysing oil-dispersion experiments.

The main scientific components are:

- SSDI modelling;
- SSMD modelling;
- droplet-size distribution modelling;
- parameter estimation;
- statistical analysis, residual analysis, and predictive validation.

The application replaces isolated analysis scripts with normalized databases, reusable pipelines, explicit model versions, persisted results, and a project-wide command-line interface.

## Current status

```text
Milestone 1 — Data Architecture and CLI Foundation
Status: Completed

Milestone 2 — SSDI Pipeline Reconstruction
Status: Completed

Milestone 3 — SSMD Pipeline Reconstruction
Status: Completed

Milestone 4 — Droplet-Size Distribution Analysis
Status: Completed

Milestone 5 — Experimental Analysis
Status: Closed for the current project stage

Milestone 6 — SSDI Field-Scale Upscaling and GUI
Status: In progress; prototype implemented, verification and distributions open
```

The core reconstruction phase is now substantially stabilized. Distribution representation and fitting were explicitly reviewed before closure, including the coordinate convention used for the empirical CDF.

The next scientific work is research-oriented rather than reconstruction-oriented. Milestone 6 now has a D50-only PySide6 desktop prototype; its scientific field-scale validity is **not established**. For droplet distributions, the next open questions concern normalized shape behaviour and possible prediction of the Rosin–Rammler shape parameter `k`.

## Current architecture

The Python package follows a `src/` layout:

```text
upscaling_app/
├── configs/
├── data/
│   ├── raw/
│   ├── database/
│   └── results/
├── docs/
├── src/
│   └── upscaling_app/
│       ├── analysis/
│       │   ├── experimental/
│       │   ├── ssdi/
│       │   ├── ssmd/
│       │   └── distributions/
│       ├── database/
│       │   ├── build.py
│       │   └── utils/
│       ├── upscaling/
│       │   ├── ssdi/
│       │   ├── ssmd/
│       │   └── distributions/
│       ├── gui/               # SSDI PySide6 prototype and shared theme
│       ├── cli.py
│       └── paths.py
├── pyproject.toml
└── README.md
```

The application is installed in editable mode:

```bash
pip install -e .
```

The command-line entry point is:

```bash
upscaling
```

## Database design

Raw experimental spreadsheets are not consumed directly by scientific pipelines.

They are first converted into normalized databases:

```text
oil_properties
      1
      │
      N
experiments
      1
      │
      N
distributions
```

Current databases:

```text
data/database/
├── oil_properties.xlsx
├── experiments.xlsx
└── distributions.xlsx
```

### Oil properties

`oil_properties.xlsx` stores oil-level properties including identifiers, density, pour point, wax/asphaltene content, and reference viscosities.

### Experiments

`experiments.xlsx` stores normalized experimental conditions.

Typical fields include:

```text
experiment_id
oil_id
dispersion_kind
dispersion_tag
nozzle_diameter
has_gas
ift
oil_flow
gas_flow
water_jet_fraction
water_flow
water_nozzle_diameter
oil_viscosity
gas_density
oil_density
measured_d50
source_sheet
```

The 2 mm conditions with and without gas remain distinct experimental regimes.

### Droplet-size distributions

`distributions.xlsx` stores measured droplet-size distribution data in normalized form:

```text
experiment_id
droplet_diameter
volume_fraction
```

Each experiment has multiple distribution rows linked by deterministic `experiment_id`.

## Identifiers

`experiment_id` must remain deterministic.

The same experiment must receive the same identifier every time the database is rebuilt.

The database architecture uses UUID5-based deterministic identifiers shared between experiment and distribution builders.

## Units

Normalized databases use SI units whenever applicable:

```text
density              kg/m³
dynamic viscosity    Pa·s
diameter             m
volumetric flow      m³/s
interfacial tension  N/m
fractions             dimensionless
```

Temperature quantities such as pour point may remain in °C when that is the natural reporting unit.

## Architectural rules

1. Raw spreadsheets are parsed only in the database layer.
2. Modelling pipelines consume normalized databases.
3. Physical equations remain separate from data ingestion.
4. Calibration / fitting remain separate from statistical analysis.
5. Prediction or fitted-model outputs are persisted before downstream evaluation whenever practical.
6. Experimental identifiers remain stable across database rebuilds.
7. SI units are used internally whenever applicable.
8. Reusable logic belongs inside `src/upscaling_app/`.
9. Avoid numbered one-off scripts as the long-term execution path.
10. Exploratory models must remain distinguishable from production-reference models.

## SSDI status

Milestone 2 is completed.

The SSDI architecture separates:

```text
data selection
        ↓
derived physics
        ↓
physical correlation
        ↓
coefficient calibration
        ↓
prediction
        ↓
persistence
        ↓
statistical analysis
        ↓
sensitivity analysis
        ↓
predictive validation
```

The complete-population leave-one-oil-out workflow remains the principal cross-oil validation within the current campaign. Oil-wise calibrations and reduced-population studies remain diagnostic and must not be confused with external validation.

## Milestone 6 — SSDI field-scale prediction and desktop GUI (2026-10-19 checkpoint)

The desktop prototype is launched from the repository root with:

```bash
python -m upscaling_app.gui.ssdi_window
```

**Architecture observed in the latest shared source snapshot and reported development:**

```text
PySide6 view (gui/ssdi_window.py)
  -> normalized oil properties and optional IFT references (database-facing IO)
  -> persisted SSDI calibration loader (model_catalog.py)
  -> SI scenario normalization and validation at the presentation boundary
  -> upscaling.ssdi.prediction.predict_field_ssdi
       -> physics.derived_properties.add_ssdi_physics
       -> physics.model.calculate_d_pred (JAX)
  -> D50, D50/D, Re, We, Ca and applicability notice
```

- Supported calibration modes: `sintef_baseline`, `jax_baseline_all`, `jax_exclude_3016_4662_4665`, `jax_oil_wise`. Oil-wise coefficients are selected by joining persisted prediction `experiment_id` to normalized experiment `oil_id`. Custom oil cannot use the oil-wise mode.
- Oil properties: reference density and estimated stabilized-oil dynamic viscosity at 20/40/50 °C; temperature interpolation is optional. Estimates are **not gas-saturated PVT properties**. Oil density is not automatically made release-condition density.
- IFT: optional laboratory lookup for untreated, Corexit 9500A and Finasol IBC where references exist. Oils with unresolved reference discrepancies must not receive unsupported automatic IFT values. The user may enter appropriate field IFT manually.
- Scenario UI units: diameter mm, oil flow m³/day, local GOR m³/m³, density kg/m³, dynamic viscosity mPa·s, IFT mN/m. SI boundary: m, m³/s, kg/m³, Pa·s, N/m.
- Interactive presentation: 100/125/150% text scaling, oil selector, expandable property assistant, four calibration buttons, `Predict D50` with calculating state and `QThread`, dimensionless metrics, smooth scrolling, extrapolation warning.
- The GUI process currently requests the JAX CPU backend before scientific imports; this avoids unnecessary GPU VRAM preallocation for scalar inference.

**Scientific status:** D50 computation is available and the illustrative 3016-treated-field scenario has been visually checked by the developer at approximately `2.0030 mm` with global coefficients. This is a **numerical reproducibility fingerprint**, not field validation. The dataset's laboratory nozzle diameters are 2–3 mm; a 470 mm nozzle is a major extrapolation. Multivariate domain analysis, field-property provenance (including gas density/GOR) and independent field validation are outstanding.

**Technical status:** the ~1,900-line `ssdi_window.py` is a provisional UI/controller monolith. The last uploaded snapshot preceded a local correction of `_predict_d50` indentation, so it is not an independently runnable source baseline. The developer reports having corrected it. Before further features, obtain a fresh committed code snapshot, run smoke/regression tests, and implement worker-lifecycle protection (edits or rescaling while calculating, close during worker execution, stale results, deleted Qt objects). See `SSDI_GUI_REFACTORING_PLAN.md` and `CHECKPOINT_2026-10-19_SSDI_GUI_MVP.md`.

## SSMD status

Milestone 3 is completed.

The reconstructed SSMD reference preserves SINTEF Equation 5 and Equation 6, explicit model identities, persisted predictions, global and oil-wise diagnostics, and leave-one-oil-out validation of the global `c,d` calibration.

The global `c,d` formulation improves in-sample representation while `eta` remains condition dependent. No universal full-scale SSMD closure has been validated.

Exploratory full-scale correlation work remains separated in `RESEARCH_SSMD_UPSCALING_UPDATED.md`.

## Distribution status

Milestone 4 is completed.

### Stable data

```text
180 experimental distributions
52 diameter bins per distribution
10 oils
```

The normalized distribution representation is:

```text
experiment_id
droplet_diameter
volume_fraction
```

### Stable analytical model

The reference analytical distribution is the two-parameter Rosin–Rammler / Weibull CDF:

\[
F(d)=1-\exp[-(d/\lambda)^k].
\]

The production estimator is the direct CDF fit using the original measured `droplet_diameter` coordinates:

\[
\min_{k,\lambda}
\sum_i
\left[F_{RR}(d_i;k,\lambda)-F_i\right]^2.
\]

The stable fitting workflow does not shift the empirical CDF to geometric upper bin edges.

### Persisted distribution parameters

```text
experiment_id
shape
scale
```

The previous moment-based estimator was evaluated as a methodological alternative and removed from the stable production workflow after comparative analysis showed inferior behaviour for the selected objectives.

### Distribution analysis

Primary fit-quality diagnostics include:

```text
CDF RMSE
CDF maximum absolute error
fitted D50
reconstructed distribution D50
D50 agreement metrics
representative CDF / PDF figures
```

The fitted median is:

\[
D_{50,fit}=\lambda(\ln2)^{1/k}.
\]

The primary D50 fit reference is the median reconstructed directly from the measured distribution. Reported `measured_d50` remains a secondary diagnostic because a small subset of experiments shows substantial disagreement between the reported value and the stored distribution.

Current numerical fingerprints for fitted D50 versus distribution-reconstructed D50 are approximately:

```text
RMSE       = 0.025932 mm
MAE        = 0.016420 mm
MAPE       = 4.590485 %
R²         = 0.998529
Log-MSE    = 0.003792
R²_log     = 0.995474
```

The mean CDF RMSE across the 180 fitted distributions is approximately:

```text
0.017585
```

The PDF representation remains useful as a shape diagnostic, especially for multimodal or secondary-peak cases, but it is not the direct fitting objective.

### Distribution plotting convention

Experimental distributions use treatment-semantic colours from the shared project palette. Rosin–Rammler fits use neutral gray. CDF figures show experimental points and one continuous fitted curve. PDF figures are diagnostic and show the experimental binned representation together with the fitted Rosin–Rammler density.

## Experimental analysis status

Milestone 5 is closed for the current project stage.

The experimental layer provides:

```text
dataset structure
+
treatment effects
+
SSDI experimental diagnostics
+
SSMD experimental diagnostics
```

It consumes normalized databases and remains separate from model calibration and prediction.

## Stable CLI surface relevant to distributions

```bash
upscaling distributions fit
upscaling analyze distributions
```

The CLI remains a dispatcher; scientific calculations stay inside the corresponding package modules.

## Current research directions

The stable reconstruction phase should not be reopened without evidence. Open distribution research belongs to the exploratory layer and includes:

```text
shape collapse after D50 normalization
variation of Rosin–Rammler shape k
hydrodynamic / oil-property predictors for k
distribution-family comparison
scale and gas transfer
grouped validation by oil
field-scale distribution reconstruction
```

The intended long-term distribution reconstruction is:

```text
predicted D50
+
predicted k
        ↓
scale lambda
        ↓
complete Rosin–Rammler distribution
```

Research details are tracked in `DISTRIBUTIONS_RESEARCH_GOALS_UPDATED.md` and must remain separate from the stable fitting workflow.
