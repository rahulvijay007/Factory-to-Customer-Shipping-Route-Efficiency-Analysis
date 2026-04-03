"""
DataFrame filtering utilities for the Nassau Candy Distributor dashboard.
"""

from __future__ import annotations

import logging
from datetime import date

import pandas as pd

logger = logging.getLogger(__name__)


def apply_filters(
    df: pd.DataFrame,
    date_range: tuple[date, date],
    regions: list[str],
    ship_modes: list[str],
) -> pd.DataFrame:
    """
    Apply sidebar filter selections to the enriched order DataFrame.

    Note: the lead-time threshold slider is intentionally excluded here.
    It controls the *Delay Frequency* KPI (passed to ``compute_kpis``),
    but must not filter the data — otherwise the KPI would always be 0%
    because the rows that count as delayed would already have been removed.

    Parameters
    ----------
    df : pd.DataFrame
        Enriched order DataFrame from ``enrich_data()``.
    date_range : tuple[date, date]
        Inclusive (from, to) range applied to ``order_date``.
    regions : list[str]
        Region names to include. Empty list means no region filter.
    ship_modes : list[str]
        Ship mode names to include. Empty list means no ship mode filter.

    Returns
    -------
    pd.DataFrame
        Filtered copy of the input DataFrame.
    """
    mask = (df["order_date"] >= pd.Timestamp(date_range[0])) & (
        df["order_date"] <= pd.Timestamp(date_range[1])
    )
    if regions:
        mask &= df["Region"].isin(regions)
    if ship_modes:
        mask &= df["Ship Mode"].isin(ship_modes)

    result = df[mask].copy()
    logger.debug(
        "Filters applied: %d → %d rows (date=%s–%s, regions=%s, modes=%s)",
        len(df), len(result), date_range[0], date_range[1], regions, ship_modes,
    )
    return result
