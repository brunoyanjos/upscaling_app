from __future__ import annotations

import pandas as pd


def report_distribution_fit(
    parameters: pd.DataFrame,
    elapsed_seconds: float,
) -> None:
    print()
    print("Rosin-Rammler distribution fitting")
    print("=" * 40)

    print(f"Experiments fitted : {len(parameters)}")
    print(f"Elapsed time       : {elapsed_seconds:.2f} s")

    print()
    print("Distribution fitting completed.")
