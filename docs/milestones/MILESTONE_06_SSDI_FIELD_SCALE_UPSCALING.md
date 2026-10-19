# Milestone 6 — SSDI Field-Scale Upscaling

**Status:** In progress — D50/GUI prototype assembled; scientific validation and distribution research open  
**Created:** 2026-10-13  
**Scope:** Field-scale SSDI median-droplet prediction, exploratory distribution upscaling, and a PySide6 D50 desktop interface.  
**Development strategy:** Initially isolated end-to-end reference script (2026-10-13); a PySide6 D50 prototype was subsequently integrated on 2026-10-19. The resulting software remains a prototype until regression, lifecycle and applicability checks are completed. Historical plans and decisions are retained below.

## 1. Motivation and objectives

Milestones 1–5 stabilised the normalized databases, SSDI and SSMD physical/modelling pipelines, direct-CDF Rosin–Rammler fitting, experimental analysis, and grouped validation. Milestone 6 starts a new research/application phase; it does **not** replace the production SSDI formulation.

**Main objective:** Predict the characteristic droplet diameter `D50` for user-defined field-scale release conditions using the existing SSDI models, and assess whether a complete droplet-size distribution can also be transferred or reconstructed.

**The three work packages are:**

1. **Part 1 (required):** SSDI field-scale `D50` prediction, scenario definition, physical preprocessing, model selection, and extrapolation diagnostics.
2. **Part 2 (exploratory, non-blocking):** Assess the upscaling of both Rosin–Rammler parameters `shape = k` and `scale = lambda`, including complete-distribution reconstruction and grouped validation.
3. **Part 3 (prototype implemented; incomplete):** PySide6 user interface for scenario input, D50 execution and numerical results. Structured output export, robust lifecycle handling, and production readiness remain future work.

Failure to establish a transferable distribution model must not block field-scale `D50` prediction or a future D50-only interface.

## 2. Non-negotiable project contracts

- The stable Python package is under `src/upscaling_app/` and the stable CLI entry point is `upscaling`.
- **Only the database layer** processes raw source spreadsheets. Prototypes and production scientific workflows consume normalized databases and persisted model coefficients.
- The database relationship is `oil_properties (1:N) experiments (1:N) distributions` with deterministic `experiment_id`.
- SI units internally, with unit conversions confined to input normalization and reporting boundaries.
- Keep data access, derived physics, calibration, prediction, analysis, plotting, persistence, and presentation logically distinct even inside the temporary script.
- **Reuse existing validated physical functions** wherever possible; do not duplicate or adjust the SSDI correlation merely to improve a field-scale estimate.
- Model versions, assumptions, source coefficients, input provenance, and calibration/validation status must be explicit.
- The prototype is a **temporary research artefact**, not a new permanent numbered or parallel production workflow.

### Existing sources of truth

- `README.md`, `AGENTS.md`, `docs/PROJECT_CONTEXT.md`.
- `docs/MILESTONE_02_SSDI_PIPELINE_UPDATED.md` — SSDI formula, coefficients, predictions, and validation.
- `docs/MILESTONE_04_DISTRIBUTION_ANALYSIS_UPDATED.md` — stable Rosin–Rammler fitting convention.
- `docs/DISTRIBUTIONS_RESEARCH_GOALS_UPDATED.md` — open distribution-shape and transfer questions.
- `docs/ANALYSIS_MODULE_PATTERN.md` — separation of scientific calculations, workflows, reports and figures.

Consult the actual source code before introducing new interfaces or paths.

## 3. Part 1 — Field-scale `D50` prediction

### 3.1 Scientific question

Can the established SSDI Weber–Capillary correlation provide useful `D50` estimates for a user-defined release at field scale? What is the distance between that release and the laboratory calibration domain in both dimensional and dimensionless terms?

**Important:** A successfully computed field-scale prediction is **not** a validation of scale-up. The current laboratory data span oil-nozzle diameters of 2 and 3 mm. The application must flag extrapolation and avoid claims of externally validated field-scale accuracy.

### 3.2 Existing reference model

The stable SSDI numerical model iteratively solves for `d50/D` using the existing Weber–Capillary formulation and coefficients `A`, `B` (`upscaling/ssdi/physics/model.py`). Physical preprocessing is implemented in `upscaling/ssdi/physics/derived_properties.py`.

Documented baseline fingerprint:

| Model / population | Quantity | Value |
|---|---|---:|
| Global baseline / 90 laboratory observations | `A` | 25.839498 |
| Global baseline / 90 laboratory observations | `B` | 0.062071 |
| Global baseline / in-sample calibration | Log-MSE | 0.426986 |
| Global baseline / complete leave-one-oil-out | Log-MSE | 0.482101 |
| Global baseline / complete leave-one-oil-out | RMSE | 0.4842 mm |
| Global baseline / complete leave-one-oil-out | MAPE | 62.47% |

These are reproducibility reference values, **not** predicted field-scale accuracy or uncertainty bounds.

The **global baseline** can be applied to an unseen oil as a transfer hypothesis. **Oil-wise** coefficients are calibrated using a particular known oil and may only be used directly for a corresponding calibrated oil; they do not independently predict coefficients for an arbitrary new oil. A new-oil oil-wise extension would require a separately developed and validated coefficient-prediction method.

### 3.3 Input contract — to confirm against existing functions

The complete input schema will be derived from `derived_properties.py` and `model.py` rather than invented ahead of code inspection. Candidate fields include:

| Domain | Candidate inputs | Internal units / convention |
|---|---|---|
| Release geometry | Oil-nozzle diameter | m |
| Oil operating conditions | Oil volumetric flow | m³/s |
| Gas operating conditions | Gas volumetric flow; gas-present flag | m³/s; boolean |
| Oil properties | Density; dynamic viscosity | kg/m³; Pa·s |
| Gas properties | Gas density when required | kg/m³ |
| Oil–water interface | Interfacial tension relevant to the treatment/scenario | N/m |
| Ambient medium | Density and any further quantities the existing formulation requires | SI |
| Treatment | Untreated, C9500, IBC or explicit supported treatment descriptor | normalized categorical field |
| Prediction | `model_version`; known `oil_id` if oil-wise | explicit |

Determine which fields are required, derivable, optional, or model-specific after code inspection. Do not silently infer unavailable field properties or claim that an untested dispersant is equivalent to a calibrated one.

### 3.4 Single-script prototype: first implementation

**Initial working artefact (suggested):** `prototypes/ssdi_field_scale.py`, outside the production package, with no permanent CLI integration. Final location should comply with the existing repository layout when the real files are inspected.

The script must implement the **entire initial field-prediction flow**, not only isolated equation calls:

```text
user-specified field scenario
    -> explicit units and required-input validation
    -> physical-property preparation using existing functions
    -> derived hydrodynamic and dimensionless quantities
    -> explicit model/coefficient selection (baseline or eligible oil-wise)
    -> iterative SSDI d50/D solution
    -> dimensional d50 prediction
    -> experimental-domain / extrapolation diagnostics
    -> structured scenario and result output
    -> concise numerical report and essential diagnostic figures
    -> optional distribution reconstruction (only once Part 2 is justified)
```

Prototype principles:

- Keep clear small functions/sections rather than a monolithic block of repeated scientific equations.
- Import existing package physics, solver, and persisted parameters where possible.
- Do not modify normalized experimental databases or overwrite calibration records.
- Use reproducible named scenarios with explicit provenance and modelling assumptions.
- Save structured outputs (`JSON`/`CSV`, as suitable) and figures only after calculation.
- Explicitly report numerical non-convergence, invalid inputs, and out-of-domain scenarios.

**Transition criterion:** Only after the prototype reproduces known reference predictions, produces a repeatable field scenario, and passes scientific/numerical checks should functionality move into modular stable production workflows and the CLI. Retire or archive the temporary prototype to avoid a divergent second implementation.

### 3.5 Applicability and numerical checks

The first field study must:

1. Confirm that the refactored/reused prediction reproduces the persisted laboratory baseline at selected known experiments.
2. Compare field inputs and derived groups against calibration ranges; do not assume simple proximity in a single variable proves interpolation in multidimensional feature space.
3. Record whether individual descriptors are interpolated or extrapolated and flag large regime/geometry shifts.
4. Check iterative solver convergence, positivity of `D50`, and physical unit consistency.
5. Assess sensitivity to uncertain field input values and the selected model coefficients, without presenting this as a calibrated predictive interval.
6. Clearly distinguish **laboratory out-of-oil cross-validation** from **field-scale validation**, which requires independent field data.

### 3.6 Statistical metrics and interpretation

The SSDI calibration uses natural logarithms:

\[
\mathrm{LogMSE} = \frac{1}{N}\sum_i
\left[\ln\left(\frac{d_{50,i}^{exp}/D_i}{d_{50,i}^{pred}/D_i}\right)\right]^2
= \frac{1}{N}\sum_i\left[\ln\left(\frac{d_{50,i}^{exp}}{d_{50,i}^{pred}}\right)\right]^2.
\]

`Log-MSE` is dimensionless and invariant when **both** predictions and experimental values are consistently converted between physical length units. The illustrative multiplicative scale is `exp(sqrt(Log-MSE))`; it is not a percentage error, MAPE, or a universal factor applying to every sample.

\[
\mathrm{RMSE} = \sqrt{\frac{1}{N}\sum_i(d_{50,i}^{pred}-d_{50,i}^{exp})^2}.
\]

`RMSE` has length units: `RMSE [µm] = 1000 × RMSE [mm]`. Ordinary `MSE` instead scales with the **square** of the length conversion. Changing units alone does not change model quality.

Use error metrics with their proper experimental/calibration/validation populations, including pooled and per-oil summaries as appropriate; avoid confusing training fit with predictive generalization. Do not infer field-scale error magnitudes from laboratory metrics.

### 3.7 Part 1 deliverables / exit criteria

- [x] Inspect existing source functions, persisted coefficient loading, and initial scenario data requirements (first prototype; see updates dated 2026-10-13 and 2026-10-19).
- [ ] Define the complete field scenario input/output schema in SI.
- [x] Build the initial isolated single-script end-to-end research prototype (`ssdi_field_scale_prototype.py`; see 2026-10-13 update).
- [ ] Validate its numerical agreement with stable persisted SSDI predictions.
- [x] Produce at least one explicitly defined illustrative field scenario (oil 3016; 470 mm; recorded assumptions).
- [ ] Report dimensionless operating state and experimental-domain departures.
- [x] Document known limitations and unresolved physical assumptions (still unresolved; no external field validation).
- [ ] Decide whether/when to migrate tested functionality to the stable package.

## 4. Part 2 — Exploratory distribution upscaling: `k` AND `lambda`

### 4.1 Current stable distribution reference

The stable workflow fits the volume-based Rosin–Rammler CDF directly at the **original measured diameter coordinates**, not at upper bin edges:

\[
F(d) = 1-\exp[-(d/\lambda)^k],\quad k>0,\ \lambda>0.
\]

- `k` (`shape`) is dimensionless and controls shape/spread.
- `lambda` (`scale`) is a characteristic droplet length (m internally).
- `D50 = lambda (ln 2)^(1/k)`.
- The distribution-reconstructed `D50` is the **primary** median reference for assessing fitted distributions; the `measured_d50` in experiments is a separate quantity used in SSDI/SSMD modelling and a secondary consistency diagnostic for distribution fitting.
- Do not overwrite either quantity to force agreement.

### 4.2 Why investigate lambda explicitly?

Because `lambda` has units of length, it is intrinsically sensitive to droplet-size scale and may exhibit clear changes from laboratory to field conditions. However, its relationship to the predicted median and shape is exact:

\[
\lambda = \frac{D_{50}}{(\ln 2)^{1/k}},\qquad
\frac{\lambda_f}{\lambda_l} = \frac{D_{50,f}}{D_{50,l}}(\ln 2)^{1/k_l-1/k_f}.
\]

When `k_f = k_l`, `lambda_f/lambda_l = D50_f/D50_l`. Otherwise, lambda's transfer reflects both changing median scale and changing shape. A strong `lambda`–`D50` association alone is partly algebraic and does **not** establish an independent physical upscaling law.

For a dimensionless descriptive view:

\[
\frac{\lambda}{D_{50}}=(\ln 2)^{-1/k}.
\]

This ratio contains no independent information beyond `k`; do not treat it as a separate independent predictor.

### 4.3 Competing reconstruction strategies

**Strategy A — SSDI median + predicted shape (preferred initial hypothesis)**

```text
SSDI field inputs -> predicted D50
hydrodynamics / oil / gas / treatment -> k hypothesis/prediction
predicted D50 + predicted k -> lambda = D50/(ln 2)^(1/k)
-> Rosin–Rammler CDF/PDF
```

Benefits: maintains internal consistency between the SSDI median and reconstructed distribution. Challenges: predictive `k` must generalize to unseen oils/scales; field-scale transfer is not yet established.

**Strategy B — Direct correlations for `k` and `lambda` (exploratory alternative)**

```text
hydrodynamics / oil / gas / treatment -> predicted k
hydrodynamics / oil / gas / treatment -> predicted lambda
-> Rosin–Rammler CDF/PDF and implied D50
```

Benefits: might expose scale dependence of `lambda` not captured by existing SSDI median prediction. Challenges: implied `D50` can disagree with the separately predicted SSDI median, creating a competing median model; must quantify this discrepancy and validate it independently.

**Strategy C — Constant or regime-specific shape (minimal baseline)**

If supported by the data, use a representative `k` (global or conditioned on a well-defined regime) and predict `lambda` from SSDI `D50`. Treat the associated CDF as a conditional or illustrative reconstruction unless predictive validation demonstrates transferability.

### 4.4 Research sequence and decision gates

1. **Shape-collapse diagnostic:** compare empirical CDFs in coordinates `d/D50`, retaining the stable original-coordinate convention and using distribution-reconstructed `D50` for distribution analysis.
2. **Parameter characterization:** assess `k`, `lambda`, `lambda/D50`, `D10/D50`, `D90/D50`, and span by oil, nozzle diameter, gas, treatment, and hydrodynamic regime. Separate scale variation from shape variation.
3. **Physical hypotheses:** test a small physically motivated set of dimensionless predictors; distinguish correlated identities among Weber, Reynolds and Capillary definitions.
4. **Simple reference models:** constant `k`, regime-specific `k`, and optionally parsimonious predictors. Avoid high-dimensional models with only ten independent oils.
5. **Competing strategies:** assess A versus B for predicted CDF fidelity, D50 consistency, tails, and robustness; don't rank only by in-sample `k` or `lambda` fit error.
6. **Predictive validation:** grouped leave-one-oil-out, including all tuning/feature-selection operations inside training folds. If model selection is extensive, use nested grouped validation. Explore geometry-regime holdouts only as limited diagnostics; current 2–3 mm data cannot validate large field scales.
7. **Decision:** validated transferable shape correlation; limited representative shape; or no defensible distribution reconstruction. Negative findings are valid research outcomes and do not block Part 1.

**Distribution comparison metrics:** CDF RMSE, maximum CDF deviation, reconstructed/fitted/predicted D50 consistency, relevant quantile/tail errors, per-oil and per-regime error summaries. Assess differences between fitting fidelity and truly predictive performance.

### 4.5 Part 2 deliverables / exit criteria

- [ ] Establish descriptive `k` and `lambda` distributions and normalized-shape diagnostics.
- [ ] Test whether `k` is approximately conserved across known experimental regimes.
- [ ] Study `lambda` scaling and whether it contains information beyond predicted `D50` + `k`.
- [ ] Compare strategies A, B and the simplest defensible shape baseline.
- [ ] Implement grouped predictive validation and full-CDF diagnostics for promising candidates.
- [ ] Document positive **or** negative conclusions and the supported operational limits.
- [ ] Only then decide whether a distribution predictor belongs in the stable application.

## 5. Part 3 — PySide6 desktop user interface (prototype)

**Status as of 2026-10-19:** An SSDI D50 desktop prototype exists. The originally deferred interface has progressed earlier than anticipated; this does **not** imply that scientific Part 1 validation or Part 2 distribution upscaling is complete.

Implemented/reported in the desktop prototype:

- Oil selection (registered and `Custom oil`); manual release-condition property entry; optional viscosity estimation and laboratory IFT reference assistant.
- Four calibration choices: SINTEF reference, global 10-oil, retained 7-oil and registered-oil-specific oil-wise. Oil-wise coefficients are read from persisted predictions mapped through normalized experiments.
- Input validation and conversion to SI; reuse of established SSDI physics and the JAX equation solver through a single-scenario prediction function.
- `D50` result, `D50/D`, `Re`, `We`, `Ca`, calibration identity/coefficients, and a nozzle-range extrapolation notice.
- PySide6 styling, user text scales, smooth scroll transitions, and an asynchronous `QThread` computing/loading state (recent, not yet subjected to lifecycle tests).
- CPU selection for JAX in the GUI process to avoid CUDA preallocation for one-scenario evaluation.

Not yet established: automatically persisted/exports of scenario and predictions; robust tests of worker completion after input/model changes, rescaling or closure; automatic multivariate domain screening; external field-scale validation; full droplet-size distribution prediction. **Do not duplicate physics in Qt code.**

For details and an explicit restart checklist see `CHECKPOINT_2026-10-19_SSDI_GUI_MVP.md`; for structural improvements see `SSDI_GUI_REFACTORING_PLAN.md`.

## 6. From proof of concept to stable software

**Stage 0 — Research prototype:** One end-to-end script, reusing existing core scientific functions. It proves scientific and numerical behaviour and is explicitly temporary.

**Stage 1 — Scientific review:** Verify physical assumptions, applicability of lab-to-field extrapolation, metric interpretation, solver convergence, reproducibility, and input contract.

**Stage 2 — Stable integration:** Migrate responsibilities to existing appropriate `src/upscaling_app/upscaling/ssdi/`, `analysis/ssdi/`, configuration, paths, and CLI architecture **only after checking the real source tree**. Reuse stable modelling functions; do not create duplicate model equations or unnecessary layers.

**Stage 3 — Interface:** An early PySide6 presentation prototype was assembled by 2026-10-19, ahead of completion of the full Stage 1–2 scientific/technical checks. It must continue to rely on a separate prediction contract; GUI completion must not be mistaken for scientific closure.

## 7. Open decisions / questions

- [ ] Which exact field quantities are available, measured or assumed (geometry, oil/gas flow, densities, viscosity, IFT, ambient properties, treatment)?
- [ ] How are field gas conditions, environmental properties and IFT defined consistently with the existing physical formulation?
- [ ] Which oils should be supported by the oil-wise option; how are their coefficients selected and traced?
- [ ] What is the first illustrative full-scale case, and which properties are uncertain?
- [ ] Which model/domain applicability checks can be made rigorously from persisted laboratory inputs and derived groups?
- [ ] Does `k` collapse after normalizing diameter by distribution-reconstructed D50?
- [ ] Is `lambda` transfer better understood as predicted D50 plus shape or as an independent predictive scale correlation?
- [ ] Is there independent field-scale experimental data suitable for external validation?
- [ ] What stable API and CLI surface should be introduced after prototype acceptance?

## 8. Decisions log

| Date | Decision | Rationale / status |
|---|---|---|
| 2026-10-13 | Start Milestone 6 as new research/application phase | Existing Milestones 1–5 remain stable |
| 2026-10-13 | Implement complete flow first in a single isolated prototype script | Test numerical and scientific coherence before permanent refactoring |
| 2026-10-13 | Maintain global baseline and known-oil oil-wise as distinct modes | Oil-wise coefficients are not directly transferable to unseen oils |
| 2026-10-13 | Investigate both `k` and `lambda` | Shape and dimensional scale have different, coupled physical roles |
| 2026-10-13 | Prefer predicted-D50 + predicted-k as the first reconstruction hypothesis; compare with direct lambda modelling | Preserve median consistency while testing alternative scale physics |
| 2026-10-13 | Part 2 is optional/non-blocking; Part 3 deferred | An inconclusive distribution correlation must not stop D50 application |
| 2026-10-13 | Separate laboratory validation from field extrapolation | No field-scale predictive skill has yet been established |
| 2026-10-19 | Adopt PySide6 GUI prototype for single-scenario D50 | Four calibration modes, property assistant, dimensionless metrics and explicit extrapolation messaging |
| 2026-10-19 | Keep one scientific solver and keep scalar GUI inference on CPU | Reuse existing SSDI physics/JAX without VRAM preallocation for desktop operation |
| 2026-10-19 | Postpone GUI decomposition until after checkpoint | Preserve behaviour first; split monolithic widgets/controller incrementally with regression tests |
| 2026-10-19 | Leave distribution upscaling in this milestone Part 2 | Avoid creating an overlapping Milestone 7 before research outcomes warrant it |

## 9. Update template

Append dated entries when the project advances:

```markdown
### YYYY-MM-DD — <change title>

**Question / objective:** ...

**Code / data inspected:** ...

**Method:** ...

**Results / diagnostics:** ...

**Scientific interpretation:** ...

**Decisions:** ...

**Next step:** ...
```

Keep this document in `docs/MILESTONE_06_SSDI_FIELD_SCALE_UPSCALING.md` in the repository and update it as the methodology evolves. Do not represent planned work as implemented or validated.

## 10. Update — 2026-10-13: field reference cases, unit audit, and retained-population option

**Sources inspected:** `build.py`, `derived_properties.py`, `model.py`, `prediction.py`, original `SINTEF datasheet.xlsx` (`Data-3mm`, `Data-2mm`, `Data-2mm-gas`, `Parameters`), field-scale SINTEF report screenshots, and leave-one-oil-out validation output.

**Selected first scenario:** 1800 m water depth; release diameter `0.47 m`; oil flow `12,000 m³/day` (`0.1388889 m³/s`); in-situ volumetric GOR `0.9`, provisionally giving gas flow `0.125 m³/s`; oil densities `937/871 kg/m³`, viscosities `0.005/0.001 Pa·s`; untreated IFT `0.0142/0.0215 N/m`; treated IFT `0.00140/0.000020 N/m` for oils `3016/4661`. Gas density `1.58 kg/m³` is copied as a **provisional reference-spreadsheet assumption**; its physical consistency at 1800 m is unresolved. Referenced SINTEF predictions: `3016 untreated 5.5 mm`, `3016 SSDI 2.0 mm`, `4661 untreated 5.1 mm`, `4661 SSDI 0.2 mm`. These are published **model outputs**, not measured field observations. Water-jet/SSMD spreadsheet results must not be mixed into the SSDI benchmark.

**Database-unit audit:** Raw Excel inputs are normalized only by the database layer. `nozzle_diameter` is already in metres; `oil_flow` and `gas_flow` convert L/min -> m³/s by dividing by 60,000; IFT mN/m -> N/m and viscosity mPa·s -> Pa·s by multiplying by 1e-3; oil density kg/L -> kg/m³ by multiplying by 1000; gas density is already kg/m³; `measured_d50` mm -> m by multiplying by 1e-3. Original measured-distribution diameter µm -> m by multiplying by 1e-6. `derived_properties.py` receives SI data without unit conversion.

**Initial three coefficient modes:** `sintef_reference` (`A=24.6`, `B=0.08`), `global_10_oils` (`A=25.839498`, `B=0.062071`), `retained_7_oils` (`A=26.044664`, `B=0.062413`). A fourth `oil_wise` mode is available only when oil-specific calibrated coefficients can be traced to persisted `jax_oil_wise` predictions joined with normalized `experiment_id` and `oil_id`.

**Retained-population option:** The seven oils are `3014,3015,4661,4663,4664,4666,4667`; oils `3016,4662,4665` are excluded from this calibration. LOO within the seven-oil population gave Log-MSE `0.171652` and RMSE `0.2497 mm`, compared with all-ten LOO Log-MSE `0.482101` and RMSE `0.4842 mm`. These test sets differ and the seven-oil selection is diagnostically data-informed; neither result establishes that this calibration is appropriate for arbitrary unknown field oils. Flag oil `3016` explicitly as an excluded-oil challenge when evaluated with retained coefficients. A future UI label should be `Retained population` or `Selected-oil calibration`, **not** a scientifically unqualified `ideal oils` class.

**Prototype numerical fingerprint** (reusing existing SSDI physics and solver, gas density 1.58 kg/m³, millimetres):

| Oil | Treatment | SINTEF coefficients | Global 10 oils | Retained 7 oils | Report field reference |
|---|---|---:|---:|---:|---:|
| 3016 | Untreated | 7.3312 | 7.6826 | 7.7442 | 5.5 |
| 3016 | SSDI 1% | 1.9342 | 2.0031 | 2.0199 | 2.0 |
| 4661 | Untreated | 9.5164 | 9.9924 | 10.0719 | 5.1 |
| 4661 | SSDI 1% | 0.2066 | 0.2033 | 0.2053 | 0.2 |

The untreated discrepancy is unresolved and requires comparison of all assumptions, source formulas and the original field-scale reference; similarity of treated values is *not* field validation. The field nozzle diameter is 0.47/0.003 ≈ 157 times the largest laboratory nozzle diameter, so all results are extrapolations.

**Implementation convention:** First create and audit the stand-alone research prototype `ssdi_field_scale_prototype.py`; it imports existing `add_ssdi_physics` and `calculate_d_pred` directly, reads only normalized data/persisted results when loading oil-wise coefficients, enables JAX double precision, checks SI inputs, and writes a separate provisional CSV. Do not move it into the stable production package until the benchmark and source-property issues have been reviewed.

**Next checks:** obtain `data/results/ssdi/predictions.xlsx` for oil-wise audit; verify assumptions behind 1800 m gas density/GOR; investigate untreated benchmark discrepancy; compare field `We`, `Ca`, `Fr`, `Re` against actual normalized lab ranges for each training population; validate solver convergence and applicability bounds.

---

## 11. Update — 2026-10-19: SSDI PySide6 D50 MVP checkpoint

**Question / objective:** Is the current D50 application prototype sufficiently functional to pause development, preserve decisions, and resume later with distribution-shape research without losing the implementation context?

**Sources inspected:** current documentation (`README`, `AGENTS`, project context, Milestones 1–6, stable distribution goals, UI guidelines) and shared Python snapshots (`ssdi_window(4).py`, `model_catalog.py`, `prediction.py`, `derived_properties.py`, `model.py`, `theme.py`, `paths.py`). The provided GUI code snapshot has 1,887 physical lines and preceded the developer's local indentation correction to `_predict_d50`. Current on-disk code in the developer's repository must be checked again before treating this snapshot as authoritative.

### 11.1 Implemented in the prototype / reported working

| Area | State and contract |
| --- | --- |
| Source inputs | Registered oil selection plus `Custom oil`; density, viscosity, IFT; oil/gas flow, GOR, nozzle diameter, gas density. |
| Oil-property helpers | Optional stabilized-oil viscosity interpolation over 20–50 °C; optional treatment-specific laboratory IFT references. No dissolved-gas PVT correction. |
| Calibrations | `sintef_baseline`, `jax_baseline_all`, `jax_exclude_3016_4662_4665`, and `jax_oil_wise` (eligible registered oil only). Load persisted coefficients, no recalibration in GUI. |
| Physics | SI scenario normalization; `add_ssdi_physics` and `calculate_d_pred` reused via `predict_field_ssdi`. |
| Results | D50 in mm, D50/nozzle diameter, Reynolds, Weber and Capillary numbers, model/parameter provenance. |
| Applicability | Explicit 2–3 mm laboratory nozzle warning for field-scale geometry; not a multivariate out-of-domain check. |
| Desktop interaction | PySide6 `ssdi_window.py`, shared `theme.py`, 100/125/150% text, property assistant, oil selector, loading state using `PredictionWorker(QThread)`, scrolling and result cards. |
| Compute backend | GUI process configures JAX CPU before scientific imports to avoid `CUDA_ERROR_OUT_OF_MEMORY` from default GPU preallocation. CLI GPU workflows are unaffected. |

### 11.2 Representative numerical fingerprint

Reference illustration, **not field validation**: oil `3016`, global 10-oil calibration, diameter 470 mm, oil flow 12,000 m³/day, local GOR 0.9, gas density 1.58 kg/m³, oil density 937 kg/m³, dynamic viscosity 5 mPa·s, IFT 1.4 mN/m gives approximately `D50 = 2.0030 mm` (see source screenshot/developer-run checkpoint); reference derived values `Re ~ 2.33e5`, `We ~ 2.21e6`, `Ca ~ 9.46`. The field gas-density/GOR physical assumptions, especially deep-water application, require independent review. These numbers are **regression fingerprints**, not measured field outcomes or uncertainty bounds.

### 11.3 Completion boundary

**Feature-complete D50 GUI prototype** is distinct from **scientifically validated field-scale model** and **production-ready application**. Keep Milestone 6 open until the following are reviewed:

- [ ] Capture the corrected, version-controlled GUI and new `model_catalog.py` and `prediction.py` implementations; run import/launch smoke tests.
- [ ] Compare selected experimental cases directly against persisted laboratory SSDI predictions and check numerical convergence.
- [ ] Add test coverage for invalid, zero-gas, missing density, negative coefficients (oil-wise B), and nonfinite physical states.
- [ ] Guard worker lifecycle against changing inputs, changing model/oil, rescaling/re-rendering and closing the window during calculation; prevent stale results.
- [ ] Check IFT manual-edit tracking and treatment changes; retain source-discrepancy protections for known oils.
- [ ] Implement comparison of the scenario's hydrodynamic and dimensionless descriptors against training-domain ranges, not just the 2–3 mm nozzle range.
- [ ] Decide whether scenario/result serialization/export is required for the D50 MVP closure; do not claim the feature exists yet.
- [ ] Perform external field-scale validation if suitable observations become available. Until then, report extrapolation as unvalidated.

**Outstanding research (Milestone 6, Part 2):** normalized CDF shape collapse; behavior and possible correlation of Rosin–Rammler `shape=k`; relationship of predicted `D50`, `k` and `scale=lambda`; distribution-family benchmarking; grouped leave-one-oil-out and field-scale transfer diagnostics. Milestone 4's direct-CDF fitting convention stays unchanged.

**Architecture action:** no wholesale rewrite now. Use `SSDI_GUI_REFACTORING_PLAN.md` to reduce the ~1,900-line Qt monolith through tested extractions, preserving `python -m upscaling_app.gui.ssdi_window` and stable model interfaces.

**Resume entry point:** `CHECKPOINT_2026-10-19_SSDI_GUI_MVP.md`.
