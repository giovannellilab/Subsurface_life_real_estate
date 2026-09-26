"""Shared, reproducible plotting defaults for project analysis modules."""
from __future__ import annotations

import numpy as np
from matplotlib import colormaps


VIRIDIS = "viridis"


def viridis_colors(count: int, *, lower: float = 0.18, upper: float = 0.85) -> list[tuple[float, float, float, float]]:
    """Return distinguishable sequential colors from the project's default map."""
    if count < 1:
        return []
    positions = np.linspace(lower, upper, count)
    return list(colormaps[VIRIDIS](positions))
