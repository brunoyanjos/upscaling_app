# Upscaling App

Local Python project for organising experimental data, storing standardised records in a local database, running upscaling analyses, fitting droplet-size distributions, and exporting reproducible results.

## Initial scope

The first version focuses on:

- reading existing Excel spreadsheets;
- standardising experimental data;
- converting physical quantities to SI units;
- preserving source traceability;
- storing data in a local SQLite database;
- running basic statistical and upscaling analyses.

The graphical interface is not part of the first development stage.

## Data policy

The project stores canonical physical data in SI units. Derived quantities such as Reynolds number, Weber number, velocity, and non-dimensional droplet diameters are computed by the application.

See:

```text
docs/DATA_POLICY.md
```

## Repository structure

```text
data/raw/        Raw source files, not versioned
data/processed/  Intermediate processed files, not versioned
data/database/   Local SQLite databases, not versioned
data/reference/  Versioned reference data
data/exports/    Generated exported results, not versioned
data/figures/    Generated figures, not versioned
docs/            Project documentation
tests/           Tests for critical functions
```

## Development setup

Create and activate the virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the project in editable mode with development dependencies:

```bash
python -m pip install --upgrade pip
pip install -e ".[dev]"
```
