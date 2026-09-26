from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from upscaling_app.plotting.style import (
    APPLE_COLORS,
    PRESENTATION_COLORS,
    APPLE_GRAYS,
    apply_plot_style,
)

REGIME_COLORS = {
    "Untreated": PRESENTATION_COLORS["Azul"],
    "SSDI": PRESENTATION_COLORS["Laranja"],
}


# ============================================================
# SSDI experimental relations
# ============================================================


# ============================================================
# Treatment-effect analysis
# ============================================================
