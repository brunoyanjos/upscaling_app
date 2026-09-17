from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = ROOT_DIR / "data"
DATABASE_DIR = DATA_DIR / "database"

RAW_DIR = DATA_DIR / "raw"
RESULTS_DIR = DATA_DIR / "results"

FIGURES_DIR = RESULTS_DIR / "figures"


DISTRIBUTIONS_DATABASE = DATABASE_DIR / "distributions.xlsx"


EXPERIMENTS_DATABASE = DATABASE_DIR / "experiments.xlsx"


OIL_EXTERNAL_PROPERTIES = RAW_DIR / "oil_external_properties.xlsx"
OIL_PROPERTIES_DATABASE = DATABASE_DIR / "oil_properties.xlsx"


SSDI_RESULTS = RESULTS_DIR / "ssdi_results.xlsx"
