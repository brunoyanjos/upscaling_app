# Import Strategy

## Objective

The import layer converts external spreadsheets into internal canonical data structures. The spreadsheet layout is not the database model.

## Source types

Initial source types:

- `sintef_datasheet`: experimental datasheet containing measured, predicted and calculated quantities;
- `droplet_distribution`: droplet-size distribution table, usually with diameter bins and treatment columns.

## General import rules

1. Read the source file without modifying it.
2. Detect or define the source type explicitly.
3. Extract only relevant primary quantities.
4. Convert physical quantities to SI units before canonical storage.
5. Preserve traceability metadata.
6. Recompute derived quantities inside the application.

## Required traceability fields

Each imported record should retain:

- source file name;
- source type;
- sheet name, when applicable;
- original row index, when applicable;
- import timestamp;
- importer version, when available.

## SINTEF datasheet

The SINTEF datasheet may contain several sheets, including data sheets, parameter sheets, measured summaries and predicted summaries.

The first importer should focus on experimental data sheets and extract primary quantities such as:

- oil code;
- nozzle diameter;
- oil flow rate;
- gas flow rate;
- oil density;
- oil viscosity;
- interfacial tension;
- measured droplet diameter;
- experimental condition;
- treatment condition.

Spreadsheet-calculated quantities such as Reynolds number, Weber number and non-dimensional droplet diameters may be read for comparison, but should not define the internal values.

## Droplet distribution tables

Distribution tables should be converted from wide format to long format.

Example external format:

```text
diameter | C9500 | C9500-gas | IBC | IBC-gas | ...
```

Canonical internal format:

```text
case_id | treatment | gas_condition | diameter_bin_m | frequency
```

The diameter unit must be explicitly defined or inferred only when supported by source documentation.
