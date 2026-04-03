"""
Geographic aggregation functions for the Nassau Candy Distributor dashboard.
"""

from __future__ import annotations

import logging

import pandas as pd

from src.config_loader import CONFIG

logger = logging.getLogger(__name__)


def compute_state_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate shipping metrics by US state for choropleth map rendering.

    Canadian provinces are excluded because Plotly's USA-states choropleth
    does not render them.

    Parameters
    ----------
    df : pd.DataFrame
        Enriched and filtered order DataFrame. Must contain: ``is_canada``,
        ``State/Province``, ``lead_time_days``, ``Row ID``.

    Returns
    -------
    pd.DataFrame
        Columns: ``state``, ``state_abbrev``, ``avg_lead_time``, ``order_count``.
        One row per US state that appears in the filtered data.
        Empty DataFrame if no US rows exist.
    """
    us_df = df[~df["is_canada"]]
    if us_df.empty:
        logger.warning("compute_state_metrics: no US rows in DataFrame")
        return pd.DataFrame(columns=["state", "state_abbrev", "avg_lead_time", "order_count"])

    state_grp = (
        us_df.groupby("State/Province")
        .agg(avg_lead_time=("lead_time_days", "mean"), order_count=("Row ID", "count"))
        .reset_index()
        .rename(columns={"State/Province": "state"})
    )
    state_grp["state_abbrev"] = state_grp["state"].map(CONFIG.geography.us_state_abbrev)
    state_grp["avg_lead_time"] = state_grp["avg_lead_time"].round(1)

    unmapped = state_grp["state_abbrev"].isna().sum()
    if unmapped > 0:
        logger.warning("%d state(s) could not be mapped to USPS abbreviations", unmapped)

    return state_grp.dropna(subset=["state_abbrev"])


def get_state_sales(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate per-state sales, lead time, and order count for US states only.

    This function eliminates the DRY violation where the same groupby-agg
    pattern was written verbatim in two separate chart sections (Tab 2 and
    Tab 4) of the original app.py.

    Parameters
    ----------
    df : pd.DataFrame
        Enriched and filtered order DataFrame. Must contain: ``is_canada``,
        ``State/Province``, ``lead_time_days``, ``Sales``, ``Row ID``.

    Returns
    -------
    pd.DataFrame
        Columns: ``State/Province``, ``avg_lead_time``, ``total_sales``,
        ``order_count``. One row per US state. Empty DataFrame if no US rows.
    """
    us_df = df[~df["is_canada"]]
    if us_df.empty:
        logger.warning("get_state_sales: no US rows in DataFrame")
        return pd.DataFrame(
            columns=["State/Province", "avg_lead_time", "total_sales", "order_count"]
        )

    return (
        us_df.groupby("State/Province")
        .agg(
            avg_lead_time=("lead_time_days", "mean"),
            total_sales=("Sales", "sum"),
            order_count=("Row ID", "count"),
        )
        .reset_index()
    )


def get_order_timeline(df: pd.DataFrame, n: int | None = None) -> pd.DataFrame:
    """
    Return the most recent orders for Gantt chart rendering.

    Parameters
    ----------
    df : pd.DataFrame
        Enriched and filtered order DataFrame (typically pre-filtered to one state).
    n : int or None
        Number of orders to return. Defaults to ``CONFIG.analytics.timeline_default_n``
        when None.

    Returns
    -------
    pd.DataFrame
        Latest ``n`` orders sorted by ``order_date`` descending, with columns:
        ``Order ID``, ``order_date``, ``ship_date``, ``lead_time_days``,
        ``Ship Mode``, ``factory``, ``State/Province``, ``Sales``.
    """
    limit = n if n is not None else CONFIG.analytics.timeline_default_n
    cols = [
        "Order ID", "order_date", "ship_date", "lead_time_days",
        "Ship Mode", "factory", "State/Province", "Sales",
    ]
    return (
        df[cols]
        .sort_values("order_date", ascending=False)
        .head(limit)
        .reset_index(drop=True)
    )
