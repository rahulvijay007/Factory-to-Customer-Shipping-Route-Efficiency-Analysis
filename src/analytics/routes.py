"""
Route efficiency computation for the Nassau Candy Distributor dashboard.

Defines a "route" as a unique (Factory, Region, Ship Mode) combination and
computes a normalized 0-100 efficiency score based on relative lead time.
"""

from __future__ import annotations

import logging

import pandas as pd

logger = logging.getLogger(__name__)


def compute_route_efficiency(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute route efficiency scores for all factory-region-ship-mode combinations.

    Efficiency Score Formula
    ------------------------
    score = 100 × (1 − (avg_relative_lt − global_min) / (global_max − global_min))

    A score of 100 is the fastest route(s); 0 is the slowest. When all routes
    have identical avg_relative_lt the score is uniformly 100.

    Parameters
    ----------
    df : pd.DataFrame
        Enriched and filtered order DataFrame. Must contain: ``factory``,
        ``Region``, ``Ship Mode``, ``relative_lead_time``, ``lead_time_days``,
        ``Row ID``.

    Returns
    -------
    pd.DataFrame
        One row per (factory, Region, Ship Mode) combination with columns:
        ``factory``, ``Region``, ``Ship Mode``, ``avg_relative_lt``,
        ``avg_lead_time``, ``order_count``, ``efficiency_score``,
        ``route_label``.
        Sorted descending by ``efficiency_score``. Empty DataFrame if input
        is empty.
    """
    if df.empty:
        logger.warning("compute_route_efficiency called on empty DataFrame")
        return pd.DataFrame()

    logger.info("Computing route efficiency for %d rows", len(df))

    grp = (
        df.groupby(["factory", "Region", "Ship Mode"])
        .agg(
            avg_relative_lt=("relative_lead_time", "mean"),
            avg_lead_time=("lead_time_days", "mean"),
            order_count=("Row ID", "count"),
        )
        .reset_index()
    )

    # ── Efficiency score (min-max normalized, inverted) ──────────────────────
    mn = grp["avg_relative_lt"].min()
    mx = grp["avg_relative_lt"].max()
    if mx == mn:
        grp["efficiency_score"] = 100.0
    else:
        grp["efficiency_score"] = (
            100.0 * (1.0 - (grp["avg_relative_lt"] - mn) / (mx - mn))
        ).round(1)

    grp["route_label"] = grp["factory"] + " → " + grp["Region"]
    grp["avg_lead_time"] = grp["avg_lead_time"].round(1)
    grp["avg_relative_lt"] = grp["avg_relative_lt"].round(2)

    logger.info("Route efficiency computed: %d routes", len(grp))
    return grp.sort_values("efficiency_score", ascending=False).reset_index(drop=True)
