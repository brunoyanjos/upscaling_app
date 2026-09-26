from __future__ import annotations

import matplotlib as mpl

from upscaling_app.plotting.colors import GRAY_COLORS


def apply_plot_style() -> None:
    mpl.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": [
                "Times New Roman",
                "Times",
                "DejaVu Serif",
            ],
            "mathtext.fontset": "stix",
            "font.size": 12,
            "axes.labelsize": 13,
            "legend.fontsize": 11,
            "xtick.labelsize": 11,
            "ytick.labelsize": 11,
            "figure.dpi": 150,
            "savefig.dpi": 300,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.edgecolor": GRAY_COLORS["medium"],
            "axes.labelcolor": GRAY_COLORS["text"],
            "xtick.color": GRAY_COLORS["dark"],
            "ytick.color": GRAY_COLORS["dark"],
            "text.color": GRAY_COLORS["text"],
            "legend.frameon": False,
            "grid.color": GRAY_COLORS["grid"],
            "grid.alpha": 0.6,
        }
    )
