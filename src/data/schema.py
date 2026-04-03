"""
Pandera schema for validating the Nassau Candy Distributor CSV.

Validation runs on the post-cast DataFrame (after numeric columns have been
converted) but before date columns are parsed. Schema failures are logged as
warnings — they do not halt execution, because the downstream dropna() on
parsed dates handles bad rows gracefully.
"""

from __future__ import annotations

import logging

import pandas as pd
import pandera.pandas as pa
from pandera.pandas import Check, Column, DataFrameSchema

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Schema definition
# ---------------------------------------------------------------------------

csv_schema = DataFrameSchema(
    columns={
        "Row ID": Column(
            pa.String,
            nullable=False,
            checks=Check(
                lambda s: s.str.strip().str.len() > 0,
                error="Row ID must not be blank",
            ),
        ),
        "Order ID": Column(pa.String, nullable=False),
        "Order Date": Column(
            pa.String,
            nullable=False,
            checks=Check(
                lambda s: pd.to_datetime(s, format="%d-%m-%Y", errors="coerce").notna().all(),
                error="Order Date must be parseable as DD-MM-YYYY",
            ),
        ),
        "Ship Date": Column(
            pa.String,
            nullable=False,
            checks=Check(
                lambda s: pd.to_datetime(s, format="%d-%m-%Y", errors="coerce").notna().all(),
                error="Ship Date must be parseable as DD-MM-YYYY",
            ),
        ),
        "Ship Mode": Column(
            pa.String,
            nullable=False,
            checks=Check.isin(
                ["Standard Class", "First Class", "Second Class", "Same Day"]
            ),
        ),
        "Region": Column(
            pa.String,
            nullable=False,
            checks=Check.isin(["Interior", "Atlantic", "Gulf", "Pacific"]),
        ),
        "Sales": Column(pa.Float, nullable=False, checks=Check.ge(0)),
        "Units": Column(pa.Int, nullable=False, checks=Check.ge(0)),
        "Gross Profit": Column(pa.Float, nullable=True),
        "Cost": Column(pa.Float, nullable=False, checks=Check.ge(0)),
        "Product Name": Column(pa.String, nullable=False),
        "State/Province": Column(pa.String, nullable=False),
    },
    coerce=False,
    strict="filter",  # allow extra columns, only validate declared ones
)


# ---------------------------------------------------------------------------
# Validation helper
# ---------------------------------------------------------------------------


def validate_schema(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate a DataFrame against the CSV schema.

    Parameters
    ----------
    df : pd.DataFrame
        Post-cast DataFrame from load_data (numeric columns already converted).

    Returns
    -------
    pd.DataFrame
        The validated DataFrame (unchanged on success).

    Raises
    ------
    ValueError
        If schema validation fails (wraps pandera's SchemaError with a clear message).
    """
    try:
        return csv_schema.validate(df, lazy=True)
    except pa.errors.SchemaErrors as exc:  # type: ignore[attr-defined]
        msg = f"Data validation found {len(exc.failure_cases)} issue(s): {exc.failure_cases.to_dict('records')[:5]}"
        raise ValueError(msg) from exc
    except pa.errors.SchemaError as exc:  # type: ignore[attr-defined]
        raise ValueError(f"Data validation error: {exc}") from exc
