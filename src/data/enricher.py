"""
Feature engineering pipeline for the Nassau Candy Distributor dashboard.

Transforms the raw loaded DataFrame into an analytically enriched form by
adding derived columns used throughout the dashboard.
"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from src.config_loader import CONFIG

logger = logging.getLogger(__name__)


def enrich_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add derived analytical columns to the loaded order DataFrame.

    Columns added
    -------------
    lead_time_days : int
        Shipping lead time in calendar days (ship_date − order_date).
    factory : str
        Factory name derived from Product Name via FACTORY_MAP.
        Rows with no match are assigned "Unknown".
    cluster_floor : int
        The cohort baseline for lead_time_days. Three cohorts exist in the
        data (≈904, ≈1269, ≈1634 days). Subtracting the floor yields the
        efficiency signal.
    relative_lead_time : int
        Days above the cohort floor — the 0-11 day range that captures genuine
        route and ship-mode variation, isolated from dataset-level date offsets.
    is_canada : bool
        True for Canadian province destinations (excluded from US choropleth).
    order_month : str
        Year-month string (e.g. "2024-01") for time-series grouping.

    Parameters
    ----------
    df : pd.DataFrame
        Output of ``load_data()``. Must contain ``order_date``, ``ship_date``,
        and ``Product Name`` columns.

    Returns
    -------
    pd.DataFrame
        New DataFrame with all original columns plus the derived columns above.
        Input DataFrame is never mutated.
    """
    logger.info("Enriching data: %d rows", len(df))
    df = df.copy()

    # ── Lead time ────────────────────────────────────────────────────────────
    df["lead_time_days"] = (df["ship_date"] - df["order_date"]).dt.days

    # ── Factory mapping ──────────────────────────────────────────────────────
    df["factory"] = df["Product Name"].map(CONFIG.factories.product_map).fillna("Unknown")
    unknown_count = (df["factory"] == "Unknown").sum()
    if unknown_count > 0:
        logger.warning(
            "%d row(s) have product names not in the factory map → assigned 'Unknown'",
            unknown_count,
        )

    # ── Cluster floor (vectorized via np.select — replaces Python .apply()) ──
    boundaries = CONFIG.analytics.cluster_boundaries   # (1100, 1500)
    floors = CONFIG.analytics.cluster_floors           # (904, 1269, 1634)
    conditions = [
        df["lead_time_days"] < boundaries[0],
        (df["lead_time_days"] >= boundaries[0]) & (df["lead_time_days"] < boundaries[1]),
    ]
    df["cluster_floor"] = np.select(
        conditions,
        choicelist=[floors[0], floors[1]],
        default=floors[2],
    )

    # ── Relative lead time (0-11 day efficiency signal) ──────────────────────
    df["relative_lead_time"] = df["lead_time_days"] - df["cluster_floor"]

    # ── Geography flags ──────────────────────────────────────────────────────
    df["is_canada"] = df["State/Province"].isin(CONFIG.geography.canadian_provinces)

    # ── Time dimension ───────────────────────────────────────────────────────
    df["order_month"] = df["order_date"].dt.to_period("M").astype(str)

    logger.info("Enrichment complete")
    return df
