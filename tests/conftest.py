"""
Pytest fixtures providing minimal, realistic DataFrames for unit tests.
All fixtures are designed to exercise actual business logic without the real CSV.
"""

from __future__ import annotations

from datetime import date

import pandas as pd
import pytest


@pytest.fixture
def raw_df() -> pd.DataFrame:
    """
    Minimal raw DataFrame matching load_data() output schema (5 rows).
    Includes one Canadian row and one typo-variant product name.
    """
    return pd.DataFrame(
        {
            "Row ID": ["1", "2", "3", "4", "5"],
            "Order ID": [
                "US-2024-001", "US-2024-002", "US-2024-003",
                "US-2024-004", "CA-2024-005",
            ],
            "Order Date": ["03-01-2024", "03-01-2024", "03-01-2024", "03-01-2024", "03-01-2024"],
            "Ship Date": ["29-06-2026", "01-07-2026", "01-07-2026", "01-07-2026", "01-07-2026"],
            "order_date": pd.to_datetime(["2024-01-03"] * 5),
            "ship_date": pd.to_datetime(
                ["2026-06-29", "2026-07-01", "2026-07-01", "2026-07-01", "2026-07-01"]
            ),
            "Ship Mode": [
                "Standard Class", "First Class", "Second Class", "Same Day", "Standard Class"
            ],
            "Region": ["Interior", "Atlantic", "Gulf", "Pacific", "Atlantic"],
            "Product Name": [
                "Wonka Bar - Milk Chocolate",      # → Wicked Choccy's
                "Laffy Taffy",                      # → Sugar Shack
                "Everlasting Gobstopper",           # → Secret Factory
                "Nerds",                            # → Sugar Shack
                "Hair Toffee",                      # → The Other Factory
            ],
            "State/Province": ["Texas", "New York", "Florida", "California", "Ontario"],
            "Sales": [6.50, 12.00, 8.25, 15.00, 9.00],
            "Units": pd.array([2, 3, 2, 4, 2], dtype="Int64"),
            "Gross Profit": [4.22, 7.80, 5.20, 9.50, 5.85],
            "Cost": [2.28, 4.20, 3.05, 5.50, 3.15],
            "Customer ID": ["C001", "C002", "C003", "C004", "C005"],
            "Country/Region": ["United States"] * 4 + ["Canada"],
            "City": ["Houston", "New York", "Miami", "Los Angeles", "Toronto"],
            "Postal Code": ["77095", "10001", "33101", "90001", "M5H 2N2"],
            "Division": ["Chocolate", "Sugar", "Sugar", "Sugar", "Sugar"],
            "Product ID": [
                "CHO-MIL-31000", "SUG-LAF-10000", "SUG-GOB-20000",
                "SUG-NRD-30000", "OTH-HAI-40000",
            ],
        }
    )


@pytest.fixture
def enriched_df(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Enriched DataFrame produced by enrich_data(raw_df)."""
    from src.data.enricher import enrich_data

    return enrich_data(raw_df)


@pytest.fixture
def filtered_df(enriched_df: pd.DataFrame) -> pd.DataFrame:
    """Enriched DataFrame with no filters applied (all rows pass)."""
    from src.analytics.filters import apply_filters

    return apply_filters(
        enriched_df,
        date_range=(date(2024, 1, 1), date(2026, 12, 31)),
        regions=[],
        ship_modes=[],
    )


@pytest.fixture
def empty_df() -> pd.DataFrame:
    """Zero-row DataFrame with the correct enriched column schema."""
    return pd.DataFrame(
        columns=[
            "Row ID", "Order ID", "Order Date", "Ship Date",
            "order_date", "ship_date", "Ship Mode", "Region",
            "Product Name", "State/Province", "Sales", "Units",
            "Gross Profit", "Cost", "Customer ID", "Country/Region",
            "City", "Postal Code", "Division", "Product ID",
            "lead_time_days", "factory", "cluster_floor",
            "relative_lead_time", "is_canada", "order_month",
        ]
    )
