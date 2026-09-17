# Milestone 1 — Data Architecture and CLI Foundation

**Status:** Completed

## Objective

Establish the project foundation required for reproducible modelling workflows before rebuilding the SSDI, SSMD, and droplet-size distribution pipelines.

## Completed work

### Python package structure

The project was reorganized using a `src/` layout:

```text
src/
└── upscaling_app/
```

The package is configured through `pyproject.toml` and installed in editable mode with:

```bash
pip install -e .
```

### Command-line interface

A project-wide CLI entry point was introduced:

```bash
upscaling
```

The database workflow is available through:

```bash
upscaling database build
```

Future commands are reserved for SSDI, SSMD, distribution fitting, and analysis.

### Database architecture

Raw experimental spreadsheets are converted into normalized databases before being used by scientific pipelines.

The adopted relationship is:

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

The generated databases are:

```text
data/database/
├── oil_properties.xlsx
├── experiments.xlsx
└── distributions.xlsx
```

### Oil properties database

`oil_properties.xlsx` stores properties associated with the oil itself, including:

- oil identifier;
- oil name;
- density;
- pour point;
- wax fraction;
- asphaltene fraction;
- viscosity at 20 °C;
- viscosity at 50 °C.

### Experiments database

`experiments.xlsx` stores individual experimental conditions, including:

- `experiment_id`;
- `oil_id`;
- dispersion type and tag;
- nozzle diameter;
- gas presence;
- interfacial tension;
- oil and gas flow rates;
- oil viscosity;
- gas and oil density;
- measured `d50`;
- source sheet.

The 2 mm experiments with and without gas are treated as distinct experimental conditions.

### Distribution database

`distributions.xlsx` stores droplet-size distribution data in normalized form:

```text
experiment_id
droplet_diameter
volume_fraction
```

Each distribution is linked to its corresponding experimental condition through `experiment_id`.

### Deterministic experiment identifiers

Experimental identifiers are deterministic.

UUID5 is used instead of UUID4 so that rebuilding the databases preserves the relationship between experimental records and droplet-size distributions.

The experiment-ID generation logic is shared between database builders.

### Tag normalization

Raw SINTEF naming conventions are normalized during database construction.

Examples include:

```text
C9500      -> SSDI-C9500
IBC        -> SSDI-IBC
WJ45%      -> WJ-45%
Untreated  -> <oil_id>-Untreated
```

The modelling pipelines should therefore consume normalized tags rather than interpret raw spreadsheet naming.

### Unit normalization

Processed databases use SI units whenever applicable.

```text
density              kg/m³
dynamic viscosity    Pa·s
diameter              m
volumetric flow       m³/s
interfacial tension   N/m
fractions             dimensionless
```

Unit conversion occurs during database construction.

### Documentation

The following project documentation was created:

```text
README.md
AGENTS.md
docs/PROJECT_CONTEXT.md
```

These files define project usage, development conventions, scientific context, and architectural decisions.

## Architectural decisions

The following principles were established during this milestone:

1. Raw spreadsheets are parsed only in the database layer.
2. Scientific pipelines consume normalized databases.
3. Physical equations are separated from data ingestion.
4. Statistical analysis is separated from calibration.
5. Experimental identifiers remain stable across rebuilds.
6. SI units are used internally whenever applicable.
7. Reusable logic belongs inside `src/upscaling_app/`.
8. Numbered one-off scripts should not drive the long-term architecture.
9. Dataset selection and model settings should migrate to configuration files.
10. Database reconstruction should be deterministic and idempotent.

## Result

The project now has a stable data and execution foundation for rebuilding the scientific workflows without depending on ad hoc scripts or direct access to raw spreadsheets.

## Next milestone

**Milestone 2 — SSDI Pipeline Reconstruction**

The next phase will rebuild the SSDI workflow using the normalized databases and separate:

```text
data selection
derived physical properties
SSDI physics
optimization
prediction
result persistence
statistical analysis
outlier analysis
```
