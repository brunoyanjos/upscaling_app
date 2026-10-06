import numpy as np
import pandas as pd

PAIR_KEYS = [
    "oil_id",
    "dispersion_kind",
    "dispersion_tag",
]


def build_nozzle_scale_pairs(
    data: pd.DataFrame,
) -> pd.DataFrame:
    required_columns = [
        "experiment_id",
        "oil_id",
        "dispersion_kind",
        "dispersion_tag",
        "distribution_regime",
        "nozzle_diameter",
        "has_gas",
        "shape",
        "scale",
        "rr_d50",
        "cdf_rmse",
        "cdf_total_variation",
    ]

    missing = [column for column in required_columns if column not in data.columns]

    if missing:
        raise ValueError(
            "Missing columns for nozzle-scale pairing: " + ", ".join(missing)
        )

    # Scale comparison is explicitly restricted to no-gas
    # experiments because no 3 mm gas counterpart exists.
    subset = data.loc[
        (~data["has_gas"])
        & (
            data["nozzle_diameter"].isin(
                [
                    0.002,
                    0.003,
                ]
            )
        )
    ].copy()

    duplicates = subset.duplicated(
        subset=[
            *PAIR_KEYS,
            "nozzle_diameter",
        ],
        keep=False,
    )

    if duplicates.any():
        raise ValueError(
            "Multiple experiments found for the same "
            "scale-pair key and nozzle diameter."
        )

    two_mm = subset.loc[
        np.isclose(
            subset["nozzle_diameter"],
            0.002,
        )
    ].copy()

    three_mm = subset.loc[
        np.isclose(
            subset["nozzle_diameter"],
            0.003,
        )
    ].copy()

    two_mm = two_mm.rename(
        columns={
            "experiment_id": "experiment_id_2mm",
            "shape": "shape_2mm",
            "scale": "scale_2mm",
            "rr_d50": "rr_d50_2mm",
            "cdf_rmse": "cdf_rmse_2mm",
            "cdf_total_variation": "total_variation_2mm",
        }
    )

    three_mm = three_mm.rename(
        columns={
            "experiment_id": "experiment_id_3mm",
            "shape": "shape_3mm",
            "scale": "scale_3mm",
            "rr_d50": "rr_d50_3mm",
            "cdf_rmse": "cdf_rmse_3mm",
            "cdf_total_variation": "total_variation_3mm",
        }
    )

    keep_2mm = [
        *PAIR_KEYS,
        "distribution_regime",
        "experiment_id_2mm",
        "shape_2mm",
        "scale_2mm",
        "rr_d50_2mm",
        "cdf_rmse_2mm",
        "total_variation_2mm",
    ]

    keep_3mm = [
        *PAIR_KEYS,
        "experiment_id_3mm",
        "shape_3mm",
        "scale_3mm",
        "rr_d50_3mm",
        "cdf_rmse_3mm",
        "total_variation_3mm",
    ]

    pairs = two_mm[keep_2mm].merge(
        three_mm[keep_3mm],
        on=PAIR_KEYS,
        how="inner",
        validate="one_to_one",
    )

    pairs["shape_delta"] = pairs["shape_3mm"] - pairs["shape_2mm"]

    pairs["shape_ratio"] = pairs["shape_3mm"] / pairs["shape_2mm"]

    pairs["log_shape_ratio"] = np.log(pairs["shape_ratio"])

    pairs["rr_d50_ratio"] = pairs["rr_d50_3mm"] / pairs["rr_d50_2mm"]

    return pairs.sort_values(
        [
            "distribution_regime",
            "dispersion_tag",
            "oil_id",
        ]
    ).reset_index(drop=True)


def summarize_nozzle_scale_pairs(
    pairs: pd.DataFrame,
) -> pd.DataFrame:
    rows = []

    groups = [
        ("All", pairs),
        *list(
            pairs.groupby(
                "distribution_regime",
                sort=False,
            )
        ),
    ]

    for regime, subset in groups:
        delta = subset["shape_delta"].to_numpy(dtype=float)

        ratio = subset["shape_ratio"].to_numpy(dtype=float)

        rows.append(
            {
                "regime": regime,
                "n": len(subset),
                "mean_shape_2mm": subset["shape_2mm"].mean(),
                "mean_shape_3mm": subset["shape_3mm"].mean(),
                "median_shape_delta": np.median(delta),
                "mean_shape_delta": np.mean(delta),
                "median_shape_ratio": np.median(ratio),
                "mean_shape_ratio": np.mean(ratio),
            }
        )

    return pd.DataFrame(rows)


def build_gas_effect_pairs(
    data: pd.DataFrame,
) -> pd.DataFrame:
    required_columns = [
        "experiment_id",
        "oil_id",
        "dispersion_kind",
        "dispersion_tag",
        "distribution_regime",
        "water_jet_fraction",
        "nozzle_diameter",
        "has_gas",
        "shape",
        "scale",
        "rr_d50",
        "cdf_rmse",
        "cdf_total_variation",
    ]

    missing = [column for column in required_columns if column not in data.columns]

    if missing:
        raise ValueError(
            "Missing columns for gas-effect pairing: " + ", ".join(missing)
        )

    subset = data.loc[
        np.isclose(
            data["nozzle_diameter"],
            0.002,
        )
    ].copy()

    pair_keys = [
        "oil_id",
        "dispersion_kind",
        "dispersion_tag",
    ]

    duplicates = subset.duplicated(
        subset=[
            *pair_keys,
            "has_gas",
        ],
        keep=False,
    )

    if duplicates.any():
        raise ValueError(
            "Multiple experiments found for the same " "gas-effect pairing key."
        )

    no_gas = subset.loc[~subset["has_gas"]].copy()

    gas = subset.loc[subset["has_gas"]].copy()

    no_gas = no_gas.rename(
        columns={
            "experiment_id": "experiment_id_no_gas",
            "shape": "shape_no_gas",
            "scale": "scale_no_gas",
            "rr_d50": "rr_d50_no_gas",
            "cdf_rmse": "cdf_rmse_no_gas",
            "cdf_total_variation": "total_variation_no_gas",
        }
    )

    gas = gas.rename(
        columns={
            "experiment_id": "experiment_id_gas",
            "shape": "shape_gas",
            "scale": "scale_gas",
            "rr_d50": "rr_d50_gas",
            "cdf_rmse": "cdf_rmse_gas",
            "cdf_total_variation": "total_variation_gas",
        }
    )

    keep_no_gas = [
        *pair_keys,
        "distribution_regime",
        "water_jet_fraction",
        "experiment_id_no_gas",
        "shape_no_gas",
        "scale_no_gas",
        "rr_d50_no_gas",
        "cdf_rmse_no_gas",
        "total_variation_no_gas",
    ]

    keep_gas = [
        *pair_keys,
        "experiment_id_gas",
        "shape_gas",
        "scale_gas",
        "rr_d50_gas",
        "cdf_rmse_gas",
        "total_variation_gas",
    ]

    pairs = no_gas[keep_no_gas].merge(
        gas[keep_gas],
        on=pair_keys,
        how="inner",
        validate="one_to_one",
    )

    pairs["shape_delta_gas"] = pairs["shape_gas"] - pairs["shape_no_gas"]
    pairs["shape_ratio_gas"] = pairs["shape_gas"] / pairs["shape_no_gas"]

    pairs["log_shape_ratio_gas"] = np.log(pairs["shape_ratio_gas"])
    pairs["rr_d50_ratio_gas"] = pairs["rr_d50_gas"] / pairs["rr_d50_no_gas"]

    return pairs.sort_values(
        [
            "distribution_regime",
            "dispersion_tag",
            "oil_id",
        ]
    ).reset_index(drop=True)


def summarize_gas_effect_pairs(
    pairs: pd.DataFrame,
) -> pd.DataFrame:
    rows = []

    groups = [
        ("All", pairs),
        *list(
            pairs.groupby(
                "distribution_regime",
                sort=False,
            )
        ),
    ]

    for regime, subset in groups:
        delta = subset["shape_delta_gas"].to_numpy(dtype=float)

        ratio = subset["shape_ratio_gas"].to_numpy(dtype=float)

        log_ratio = subset["log_shape_ratio_gas"].to_numpy(dtype=float)

        rows.append(
            {
                "regime": regime,
                "n": len(subset),
                "mean_shape_no_gas": subset["shape_no_gas"].mean(),
                "mean_shape_gas": subset["shape_gas"].mean(),
                "median_shape_delta": np.median(delta),
                "mean_shape_delta": np.mean(delta),
                "median_shape_ratio": np.median(ratio),
                "mean_shape_ratio": np.mean(ratio),
                "median_log_shape_ratio": np.median(log_ratio),
            }
        )

    ssmd = pairs.loc[pairs["distribution_regime"] == "SSMD"]

    for fraction, subset in ssmd.groupby(
        "water_jet_fraction",
        sort=True,
    ):
        delta = subset["shape_delta_gas"].to_numpy(dtype=float)

        ratio = subset["shape_ratio_gas"].to_numpy(dtype=float)

        log_ratio = subset["log_shape_ratio_gas"].to_numpy(dtype=float)

        rows.append(
            {
                "regime": (f"SSMD — {fraction:.0%}"),
                "n": len(subset),
                "mean_shape_no_gas": subset["shape_no_gas"].mean(),
                "mean_shape_gas": subset["shape_gas"].mean(),
                "median_shape_delta": np.median(delta),
                "mean_shape_delta": np.mean(delta),
                "median_shape_ratio": np.median(ratio),
                "mean_shape_ratio": np.mean(ratio),
                "median_log_shape_ratio": np.median(log_ratio),
            }
        )

    return pd.DataFrame(rows)
