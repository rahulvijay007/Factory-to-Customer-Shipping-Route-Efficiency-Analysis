"""Unit tests for src/analytics — filters, kpis, routes, geography."""

from __future__ import annotations

from datetime import date

import pandas as pd
import pytest


# ---------------------------------------------------------------------------
# apply_filters
# ---------------------------------------------------------------------------


def test_filter_date_range_excludes_all(enriched_df):
    from src.analytics.filters import apply_filters

    result = apply_filters(
        enriched_df,
        date_range=(date(2020, 1, 1), date(2020, 12, 31)),
        regions=[],
        ship_modes=[],
    )
    assert result.empty


def test_filter_by_region(enriched_df):
    from src.analytics.filters import apply_filters

    result = apply_filters(
        enriched_df,
        date_range=(date(2024, 1, 1), date(2026, 12, 31)),
        regions=["Interior"],
        ship_modes=[],
    )
    assert (result["Region"] == "Interior").all()


def test_filter_by_ship_mode(enriched_df):
    from src.analytics.filters import apply_filters

    result = apply_filters(
        enriched_df,
        date_range=(date(2024, 1, 1), date(2026, 12, 31)),
        regions=[],
        ship_modes=["Same Day"],
    )
    assert (result["Ship Mode"] == "Same Day").all()


def test_filter_threshold_only_affects_kpi_not_data(enriched_df):
    """Threshold no longer filters rows — it only drives the delay KPI."""
    from src.analytics.filters import apply_filters
    from src.analytics.kpis import compute_kpis

    # All rows pass regardless of threshold value
    result = apply_filters(
        enriched_df,
        date_range=(date(2024, 1, 1), date(2026, 12, 31)),
        regions=[],
        ship_modes=[],
    )
    assert len(result) == len(enriched_df)

    # Threshold set below minimum → 100% delay
    min_lt = int(enriched_df["lead_time_days"].min()) - 1
    kpis = compute_kpis(result, delay_threshold=min_lt)
    assert kpis["delay_frequency"] == 100.0

    # Threshold set above maximum → 0% delay
    max_lt = int(enriched_df["lead_time_days"].max()) + 1
    kpis = compute_kpis(result, delay_threshold=max_lt)
    assert kpis["delay_frequency"] == 0.0


# ---------------------------------------------------------------------------
# compute_kpis
# ---------------------------------------------------------------------------


def test_kpis_total_orders_equals_len(filtered_df):
    from src.analytics.kpis import compute_kpis

    result = compute_kpis(filtered_df, delay_threshold=1000)
    assert result["total_orders"] == len(filtered_df)


def test_kpis_empty_guard():
    from src.analytics.kpis import compute_kpis

    result = compute_kpis(pd.DataFrame(), delay_threshold=1000)
    assert result["total_orders"] == 0
    assert result["delay_frequency"] == 0


def test_kpis_delay_frequency_all_delayed(filtered_df):
    from src.analytics.kpis import compute_kpis

    min_lt = int(filtered_df["lead_time_days"].min()) - 1
    result = compute_kpis(filtered_df, delay_threshold=min_lt)
    assert result["delay_frequency"] == 100.0


def test_kpis_delay_frequency_none_delayed(filtered_df):
    from src.analytics.kpis import compute_kpis

    max_lt = int(filtered_df["lead_time_days"].max()) + 1
    result = compute_kpis(filtered_df, delay_threshold=max_lt)
    assert result["delay_frequency"] == 0.0


def test_kpis_returns_all_required_keys(filtered_df):
    from src.analytics.kpis import compute_kpis

    result = compute_kpis(filtered_df, delay_threshold=1200)
    required = {
        "total_orders", "avg_lead_time", "avg_relative_lead_time",
        "total_revenue", "total_profit", "median_lead_time", "delay_frequency",
    }
    assert required == set(result.keys())


# ---------------------------------------------------------------------------
# compute_route_efficiency
# ---------------------------------------------------------------------------


def test_route_efficiency_score_range(filtered_df):
    from src.analytics.routes import compute_route_efficiency

    result = compute_route_efficiency(filtered_df)
    assert (result["efficiency_score"] >= 0).all()
    assert (result["efficiency_score"] <= 100).all()


def test_route_efficiency_empty_guard(empty_df):
    from src.analytics.routes import compute_route_efficiency

    result = compute_route_efficiency(empty_df)
    assert result.empty


def test_route_efficiency_all_same_lead_time(filtered_df):
    """When all relative_lead_times are identical, all scores should be 100."""
    from src.analytics.routes import compute_route_efficiency

    df = filtered_df.copy()
    df["relative_lead_time"] = 5  # force uniform value
    result = compute_route_efficiency(df)
    assert (result["efficiency_score"] == 100.0).all()


def test_route_efficiency_label_format(filtered_df):
    from src.analytics.routes import compute_route_efficiency

    result = compute_route_efficiency(filtered_df)
    assert result["route_label"].str.contains(" → ").all()


# ---------------------------------------------------------------------------
# geography
# ---------------------------------------------------------------------------


def test_state_metrics_excludes_canada(enriched_df):
    from src.analytics.geography import compute_state_metrics

    result = compute_state_metrics(enriched_df)
    assert "Ontario" not in result["state"].values


def test_get_state_sales_excludes_canada(enriched_df):
    from src.analytics.geography import get_state_sales

    result = get_state_sales(enriched_df)
    assert "Ontario" not in result["State/Province"].values


def test_get_state_sales_empty_guard(empty_df):
    from src.analytics.geography import get_state_sales

    result = get_state_sales(empty_df)
    assert result.empty
