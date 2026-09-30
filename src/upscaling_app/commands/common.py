from __future__ import annotations

import argparse


def add_ssdi_source_argument(
    parser: argparse.ArgumentParser,
) -> None:
    from upscaling_app.upscaling.ssdi.versions import (
        BASELINE_VERSION,
    )

    parser.add_argument(
        "--ssdi-source",
        dest="ssdi_source_version",
        default=BASELINE_VERSION,
        help=(
            "Persisted SSDI model version used to provide "
            "the untreated D50 prediction. "
            f"Default: {BASELINE_VERSION}."
        ),
    )
