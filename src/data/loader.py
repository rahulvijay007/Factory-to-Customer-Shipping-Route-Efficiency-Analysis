"""
Dataset loader for the Nassau Candy Distributor dashboard.

Handles CSV ingestion, type casting, schema validation, and date parsing.
Returns a clean DataFrame ready for enrichment.
"""

from __future__ import annotations

import logging

import pandas as pd

from src.config_loader import CONFIG
from src.data.schema import validate_schema

logger = logging.getLogger(__name__)

# Columns to cast to float after initial string load
_FLOAT_COLS = ["Sales", "Gross Profit", "Cost"]


def load_data(filepath: str | None = None) -> pd.DataFrame:
    """
    Load and validate the order dataset from CSV.

    Parameters
    ----------
    filepath : str or None
        Path to the CSV file. Defaults to ``CONFIG.dataset.path`` when None.

    Returns
    -------
    pd.DataFrame
        Clean DataFrame with parsed ``order_date`` and ``ship_date`` columns.
        Rows with unparseable dates are dropped.

    Raises
    ------
    FileNotFoundError
        If the CSV file does not exist at the given path.
    ValueError
        If the file is empty.
    """
    path = filepath if filepath is not None else CONFIG.dataset.path
    logger.info("Loading dataset from: %s", path)

    # ── Read raw CSV ─────────────────────────────────────────────────────────
    try:
        raw_df = pd.read_csv(path, dtype=str)
    except FileNotFoundError:
        logger.error("Dataset file not found: %s", path)
        raise FileNotFoundError(
            f"Dataset file not found: {path!r}. "
            "Verify the file exists and the path in config.yaml is correct."
        )
    except pd.errors.EmptyDataError:
        logger.error("Dataset file is empty: %s", path)
        raise ValueError(f"Dataset file is empty: {path!r}")

    # ── Strip whitespace ─────────────────────────────────────────────────────
    raw_df.columns = raw_df.columns.str.strip()
    for col in raw_df.select_dtypes(include="str").columns:
        raw_df[col] = raw_df[col].str.strip()

    # ── Cast numeric columns ─────────────────────────────────────────────────
    for col in _FLOAT_COLS:
        raw_df[col] = pd.to_numeric(raw_df[col], errors="coerce")
    raw_df["Units"] = pd.to_numeric(raw_df["Units"], errors="coerce").astype("Int64")

    # ── Schema validation (warning only — does not halt execution) ───────────
    try:
        validate_schema(raw_df)
        logger.info("Schema validation passed")
    except ValueError as exc:
        logger.warning("Schema validation warning: %s", exc)

    # ── Parse date columns ───────────────────────────────────────────────────
    raw_df["order_date"] = pd.to_datetime(
        raw_df["Order Date"], format="%d-%m-%Y", errors="coerce"
    )
    raw_df["ship_date"] = pd.to_datetime(
        raw_df["Ship Date"], format="%d-%m-%Y", errors="coerce"
    )

    nat_count = raw_df["order_date"].isna().sum() + raw_df["ship_date"].isna().sum()
    if nat_count > 0:
        logger.warning("%d unparseable date value(s) detected — affected rows will be dropped", nat_count)

    raw_df = raw_df.dropna(subset=["order_date", "ship_date"])
    logger.info("Dataset loaded: %d rows after date validation", len(raw_df))
    return raw_df
