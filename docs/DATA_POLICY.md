# Data Policy

## Objective

The Upscaling App stores experimental and physical data in a standardised internal format. Source spreadsheets are treated as external and potentially unstable inputs.

## Core rules

1. Canonical physical quantities must be stored in SI units.
2. Derived quantities must be computed by the application, not treated as primary data.
3. Source files must remain traceable, but their layout must not define the internal data model.

## Canonical units

| Quantity | Canonical unit |
|---|---|
| Length | m |
| Diameter | m |
| Flow rate | m³/s |
| Velocity | m/s |
| Density | kg/m³ |
| Dynamic viscosity | Pa·s |
| Interfacial tension | N/m |
| Pressure | Pa |
| Time | s |

## Primary data

Primary data are quantities measured, imposed, or physically characterised in the experiment.

Examples:

- oil code;
- oil name;
- nozzle diameter;
- oil flow rate;
- gas flow rate;
- oil density;
- oil viscosity;
- interfacial tension;
- measured droplet diameter;
- experimental scenario;
- treatment condition.

## Derived data

Derived quantities are computed from primary data by reproducible functions in the application.

Examples:

- Reynolds number;
- Weber number;
- oil velocity;
- gas void fraction;
- non-dimensional droplet diameter;
- distribution fitting metrics.

## Source traceability

Imported records should retain enough metadata to identify their origin.

Examples:

- source file name;
- sheet name;
- original row;
- original column name;
- import date;
- source type.

## Treatment of spreadsheet-calculated quantities

Quantities calculated in external spreadsheets may be imported for comparison or validation, but they must not replace the internally computed values.

For example, if a spreadsheet contains `We`, the application should still compute `We` from density, velocity, diameter, and interfacial tension.

## Oil reference data

Oil codes and display names are stored in `data/reference/oils.csv`.

The oil code is the stable identifier. The display name is a human-readable label and should not be used as the primary key.
