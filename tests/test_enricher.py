"""Unit tests for src/data/enricher.py."""

from __future__ import annotations

import pandas as pd


def test_lead_time_calculation(raw_df):
    """Row 0: order 2024-01-03, ship 2026-06-29 → 908 days."""
    from src.data.enricher import enrich_data

    result = enrich_data(raw_df)
    assert result["lead_time_days"].iloc[0] == 908


def test_factory_mapping_known_products(raw_df):
    """Known product names map to correct factories."""
    from src.data.enricher import enrich_data

    result = enrich_data(raw_df)
    assert result["factory"].iloc[0] == "Wicked Choccy's"    # Wonka Bar - Milk Chocolate
    assert result["factory"].iloc[1] == "Sugar Shack"         # Laffy Taffy
    assert result["factory"].iloc[2] == "Secret Factory"      # Everlasting Gobstopper
    assert result["factory"].iloc[3] == "Sugar Shack"         # Nerds
    assert result["factory"].iloc[4] == "The Other Factory"   # Hair Toffee


def test_factory_mapping_unknown_product(raw_df):
    """Unmapped product name produces 'Unknown' factory."""
    from src.data.enricher import enrich_data

    df = raw_df.copy()
    df.loc[0, "Product Name"] = "Totally Fake Candy 9000"
    result = enrich_data(df)
    assert result["factory"].iloc[0] == "Unknown"


def test_cluster_floor_assignment(raw_df):
    """lead_time 908 < 1100 → cluster_floor = 904."""
    from src.data.enricher import enrich_data

    result = enrich_data(raw_df)
    assert result["cluster_floor"].iloc[0] == 904


def test_relative_lead_time_equals_lead_minus_floor(raw_df):
    """relative_lead_time = lead_time_days − cluster_floor for all rows."""
    from src.data.enricher import enrich_data

    result = enrich_data(raw_df)
    expected = result["lead_time_days"] - result["cluster_floor"]
    pd.testing.assert_series_equal(
        result["relative_lead_time"], expected, check_names=False
    )


def test_is_canada_flag(raw_df):
    """Ontario (row 4) → is_canada=True; Texas (row 0) → is_canada=False."""
    from src.data.enricher import enrich_data

    result = enrich_data(raw_df)
    assert result["is_canada"].iloc[4] is True or result["is_canada"].iloc[4] == True
    assert result["is_canada"].iloc[0] is False or result["is_canada"].iloc[0] == False


def test_enrich_does_not_mutate_input(raw_df):
    """Input DataFrame must not be modified in place."""
    from src.data.enricher import enrich_data

    original_cols = list(raw_df.columns)
    enrich_data(raw_df)
    assert list(raw_df.columns) == original_cols
    assert "lead_time_days" not in raw_df.columns
