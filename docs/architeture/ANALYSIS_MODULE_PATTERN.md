# Analysis Module Pattern

## Purpose

This document defines the preferred architecture for analysis modules in Upscaling App.

The pattern was consolidated while reorganizing:

```text
analysis/experimental/summary
analysis/experimental/treatment_effect
analysis/experimental/ssdi
analysis/experimental/ssmd
```

Its purpose is to preserve a clear separation between scientific calculations, orchestration, visualization, reporting, model physics, and CLI execution.

---

## 1. Canonical structure

```text
analysis/<domain>/<module>/
├── __init__.py
├── analysis.py
├── pipeline.py
├── plotting.py
└── reporting.py
```

Do not add `workflows/`, `utils/`, numbered scripts, or additional layers unless the scientific workflow genuinely requires them.

---

## 2. Responsibility map

```text
normalized data
      ↓
analysis.py
      ↓
result tables / metrics
      ↓
pipeline.py
      ├── reporting.py
      └── plotting.py
             ↓
       terminal + figures
```

CLI:

```text
cli.py
   ↓
run_<module>_workflow()
```

---

## 3. `analysis.py`

### Responsibility

Contains scientific and statistical calculations.

Typical contents:

```text
data preparation
explicit filtering
pair construction
derived quantities
grouped summaries
regressions
correlations
diagnostic metrics
```

### Rules

`analysis.py` should:

- consume normalized data;
- keep scientific assumptions explicit;
- validate pair integrity;
- keep internal units in SI;
- reuse validated physics from `upscaling/` when appropriate;
- return DataFrames, dictionaries, scalars, or other calculation results.

It should not:

```text
save figures
print reports
create output directories
parse raw spreadsheets
contain CLI logic
```

---

## 4. `pipeline.py`

### Responsibility

Orchestrates the module.

Preferred structure:

```python
@dataclass
class ExampleResult:
    data: pd.DataFrame
    summary: pd.DataFrame


def run_example_analysis() -> ExampleResult:
    data = load_experiments()
    summary = summarize_response(data)

    return ExampleResult(
        data=data,
        summary=summary,
    )


def run_example_workflow() -> ExampleResult:
    result = run_example_analysis()

    print_example_report(result)

    save_example_plot(
        result.summary,
        paths.EXAMPLE_FIGURES_DIR / "example.png",
    )

    return result
```

The distinction is intentional:

```text
run_*_analysis()
    reusable calculation
    no user-facing side effects

run_*_workflow()
    reporting
    plotting
    CLI-facing execution
```

---

## 5. Result dataclasses

Every pipeline should expose a stable result object.

Example:

```python
@dataclass
class TreatmentEffectResult:
    effects: pd.DataFrame
    by_oil: pd.DataFrame
    by_method: pd.DataFrame
```

Prefer meaningful fields over generic dictionaries.

Do not retain intermediate tables merely because the current implementation happens to use them.

---

## 6. `plotting.py`

### Responsibility

Turns already-calculated results into figures.

Allowed visualization-oriented operations include:

```text
sorting
label formatting
finite-value masks
axis-unit conversion
reshaping for display
```

Do not calculate scientific results inside plotting.

Avoid:

```text
np.polyfit
correlation
scientific grouping
pair construction
outlier detection
ranking
model fitting
physical equations
```

If a plot requires:

```text
slope
intercept
R²
median
IQR
correlation
```

calculate those values in `analysis.py` and pass them to the plotting function.

Use shared project styling:

```text
upscaling_app.plotting.colors
upscaling_app.plotting.style
```

Current scientific color semantics:

```text
Untreated     petroleum / dark neutral
SSMD          blue
SSDI C9500    orange
SSDI IBC      yellow
statistics    gray
identity      light gray
```

Color should encode scientific meaning rather than arbitrary visual distinction.

---

## 7. `reporting.py`

### Responsibility

Presents already-calculated results in the terminal.

Typical operations:

```text
rename columns
format numbers
convert SI values for display
order rows
print concise tables
```

Do not place scientific analysis inside reporting.

Avoid:

```text
pair construction
regression
correlation
outlier detection
model fitting
hidden scientific filtering
```

Reporting should support validation of a run, not invent new analysis.

---

## 8. `__init__.py`

Keep `__init__.py` minimal.

Do not place scientific implementation logic there.

---

## 9. CLI pattern

The CLI is a dispatcher.

Preferred:

```python
elif args.experimental_command == "ssmd":
    from upscaling_app.analysis.experimental.ssmd.pipeline import (
        run_ssmd_experimental_workflow,
    )

    run_ssmd_experimental_workflow()
```

The CLI should know which workflow to execute, not how the science works.

Do not put DataFrame manipulation, physics, regression, plotting, or calibration in `cli.py`.

---

## 10. Paths

Output locations belong in:

```text
upscaling_app.paths
```

Prefer:

```python
EXPERIMENTAL_SSMD_FIGURES_DIR = (
    EXPERIMENTAL_FIGURES_DIR / "ssmd"
)
```

over repeatedly constructing:

```python
paths.EXPERIMENTAL_FIGURES_DIR / "ssmd"
```

Output filenames should describe scientific content:

```text
d50_reduction_by_method.png
ssdi_spearman_screening.png
ssmd_gas_effect.png
```

---

## 11. Data-source rule

Scientific analysis consumes normalized databases only.

```text
raw spreadsheet
      ↓
database/
      ↓
normalized database
      ↓
analysis/
```

Never parse raw spreadsheets inside an analysis module.

Current normalized relationships remain:

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

`experiment_id` remains deterministic.

---

## 12. Units

Use SI internally whenever applicable.

```text
diameter              m
density               kg/m³
dynamic viscosity     Pa·s
volumetric flow       m³/s
interfacial tension   N/m
fraction              dimensionless
```

Presentation conversions occur near the presentation boundary:

```text
m → mm
0.40 → 40 %
```

Do not change the primary internal representation merely for plotting convenience.

---

## 13. Explicit scientific selection

Avoid hidden selection criteria.

Bad:

```python
def prepare_data(
    data,
    include_gas=False,
):
    ...
```

when excluding gas changes the population being analysed.

Preferred:

```text
prepare complete valid dataset
        ↓
apply explicit subset only where required
```

The subset must remain visible in code and reporting.

Examples:

```text
pooled = Untreated + SSDI
ssdi_only = SSDI
2 mm gas/no-gas paired subset
```

---

## 14. Reuse validated physics

If an experimental diagnostic requires a physical quantity already implemented by a validated modelling workflow:

```text
analysis.experimental
        ↓
reuse
        ↓
upscaling.<model>.physics
```

Do not copy the physical equation into the experimental-analysis package.

This avoids divergence between experimental diagnostics and production physics.

Preserve the distinction:

```text
physical preprocessing
≠
parameter fitting
≠
prediction
≠
model evaluation
```

---

## 15. Cross-module reuse

Reuse a scientific operation when its definition is genuinely shared.

Example:

```text
treatment_effect
    owns general treated ↔ untreated effect calculation

ssdi
    reuses it for C9500 × IBC comparison
```

Do not create subtly different copies of the same pairing or metric formula.

---

## 16. Statistical scope

### Repeated observations

Repeated experiments on the same oil are not independent observations of oil-level properties.

### Pooled analyses

Pooled relationships may combine:

```text
within-regime variation
+
between-regime separation
```

Always state the analysed population.

### Descriptive vs predictive

Keep distinct:

```text
experimental variability
calibration fit
sensitivity analysis
predictive validation
```

Improved in-sample fit is not automatically improved predictive performance.

---

## 17. Model boundary

For this project:

```text
analysis/experimental/
    measured experimental behaviour

analysis/ssdi/
analysis/ssmd/
    persisted model-result evaluation

upscaling/ssdi/
upscaling/ssmd/
    physics, calibration, prediction
```

The experimental-analysis layer may identify variability, regime structure, unexplained behaviour, or candidate mechanisms.

It must not silently modify production correlations.

---

## 18. Default development sequence

Use this order:

```text
1. Define the scientific question.
2. Define the required outputs.
3. Implement analysis.py.
4. Define the Result dataclass.
5. Implement run_*_analysis().
6. Implement reporting.py.
7. Implement plotting.py.
8. Implement run_*_workflow().
9. Connect the workflow in cli.py.
10. Run the CLI and inspect counts, pair integrity, units, tables, and figures.
```

Do not begin by adding plots.

Start with the scientific question and the data products needed to answer it.

---

## 19. Closure checklist

Before considering a module closed:

```text
[ ] normalized data only
[ ] SI units internally
[ ] analysed population explicit
[ ] pairing keys explicit and validated
[ ] calculations in analysis.py
[ ] no scientific fitting in plotting.py
[ ] no scientific analysis in reporting.py
[ ] analysis/workflow separation in pipeline.py
[ ] meaningful Result dataclass
[ ] CLI dispatches workflow only
[ ] paths centralized in paths.py
[ ] project color semantics preserved
[ ] every plot answers a defined scientific question
[ ] shared logic is not duplicated
[ ] experimental analysis remains separate from model evaluation
[ ] no physical equation was changed merely to improve fit
```

---

## 20. Design principle

```text
analysis
    calculates

pipeline
    orchestrates

reporting
    communicates numerically

plotting
    communicates visually

CLI
    dispatches
```

Add complexity only when the scientific workflow requires it.

Do not introduce structural layers pre-emptively.
