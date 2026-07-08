# Setup on Ubuntu WSL

## Create the virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## Install dependencies

```bash
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

## Verify installation

```bash
python -c "import pandas, numpy, scipy, matplotlib, sqlalchemy; print('Environment OK')"
pytest
```

## First commit

```bash
git status
git add .
git commit -m "Initial project structure"
```
