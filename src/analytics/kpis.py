"""
Key Performance Indicator computation for the Nassau Candy Distributor dashboard.
"""

from __future__ import annotations

import logging
from typing import TypedDict

import pandas as pd

logger = logging.getLogger(__name__)


class KPIResult(TypedDict):
    """Typed dictionary returned by compute_kpis."""

    total_orders: int
    avg_lead_time: float
    avg_relative_lead_time: float
    total_revenue: float
    total_profit: float
    median_lead_time: float
    delay_frequency: float


_EMPTY_KPIS: KPIResult = {
    "total_orders": 0,
    "avg_lead_time": 0.0,
    "avg_relative_lead_time": 0.0,
    "total_revenue": 0.0,
    "total_profit": 0.0,
    "median_lead_time": 0.0,
    "delay_frequency": 0.0,
}


def compute_kpis(df: pd.DataFrame, delay_threshold: int) -> KPIResult:
    """
    Compute summary KPIs for the filtered order DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Enriched and filtered order DataFrame.
    delay_threshold : int
        Lead time (days) above which a shipment is considered delayed.
        Drives the ``delay_frequency`` KPI.

    Returns
    -------
    KPIResult
        Dictionary with the seven KPI values. All values are 0 / 0.0 when
        the input DataFrame is empty.
    """
    if df.empty:
        logger.warning("compute_kpis called on empty DataFrame — returning zero KPIs")
        return _EMPTY_KPIS.copy()

    logger.info("Computing KPIs for %d rows (delay threshold: %d days)", len(df), delay_threshold)

    return KPIResult(
        total_orders=len(df),
        avg_lead_time=round(float(df["lead_time_days"].mean()), 1),
        avg_relative_lead_time=round(float(df["relative_lead_time"].mean()), 2),
        total_revenue=float(df["Sales"].sum()),
        total_profit=float(df["Gross Profit"].sum()),
        median_lead_time=float(df["lead_time_days"].median()),
        delay_frequency=round(float((df["lead_time_days"] > delay_threshold).mean() * 100), 1),
    )
