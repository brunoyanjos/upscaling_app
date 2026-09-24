from __future__ import annotations

import matplotlib as mpl

PRESENTATION_COLORS = {
    "Verde": "#008543",
    "Laranja": "#EC8B00",
    "Cinza": "#63666B",
    "Azul": "#016299",
}

APPLE_COLORS = {
    "red": "#FF383C",
    "orange": "#FF8D28",
    "yellow": "#FFCC00",
    "green": "#34C759",
    "mint": "#00C8B3",
    "teal": "#00C3D0",
    "cyan": "#00C0E8",
    "blue": "#0088FF",
    "indigo": "#6155F5",
    "purple": "#CB30E0",
    "pink": "#FF3755",
    "brown": "#AC7F5E",
}

APPLE_GRAYS = {
    "gray": "#8E8E93",
    "gray2": "#282833",
    "gray3": "#C7C7CC",
    "gray4": "#D1D1D6",
    "gray5": "#E5E5EA",
    "gray6": "#F2F2F7",
}


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
            "axes.edgecolor": APPLE_GRAYS["gray3"],
            "axes.labelcolor": "#1C1C1E",
            "xtick.color": "#3A3A3C",
            "ytick.color": "#3A3A3C",
            "text.color": "#1C1C1E",
            "legend.frameon": False,
            "grid.color": APPLE_GRAYS["gray5"],
            "grid.alpha": 0.6,
        }
    )
