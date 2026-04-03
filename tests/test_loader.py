"""Unit tests for src/data/loader.py."""

from __future__ import annotations

import textwrap

import pandas as pd
import pytest


def _write_csv(tmp_path, content: str) -> str:
    """Write CSV content to a temp file and return its path as string."""
    p = tmp_path / "test_data.csv"
    p.write_text(textwrap.dedent(content), encoding="utf-8")
    return str(p)


_VALID_CSV_HEADER = (
    "Row ID,Order ID,Order Date,Ship Date,Ship Mode,Customer ID,"
    "Country/Region,City,State/Province,Postal Code,Division,Region,"
    "Product ID,Product Name,Sales,Units,Gross Profit,Cost\n"
)
_VALID_ROW = (
    "1,US-2024-001,03-01-2024,01-07-2026,Standard Class,101,"
    "United States,Houston,Texas,77095,Chocolate,Interior,"
    "CHO-MIL-31000,Wonka Bar - Milk Chocolate,6.50,2,4.22,2.28\n"
)


def test_load_data_returns_dataframe(tmp_path):
    path = _write_csv(tmp_path, _VALID_CSV_HEADER + _VALID_ROW)
    from src.data.loader import load_data

    result = load_data(path)
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 1


def test_load_data_strips_whitespace(tmp_path):
    content = (
        " Row ID , Order ID ,Order Date,Ship Date,Ship Mode,Customer ID,"
        "Country/Region,City,State/Province,Postal Code,Division,Region,"
        "Product ID,Product Name,Sales,Units,Gross Profit,Cost\n"
        " 1 , US-2024-001 ,03-01-2024,01-07-2026,Standard Class,101,"
        "United States,Houston,Texas,77095,Chocolate,Interior,"
        "CHO-MIL-31000,Wonka Bar - Milk Chocolate,6.50,2,4.22,2.28\n"
    )
    path = _write_csv(tmp_path, content)
    from src.data.loader import load_data

    result = load_data(path)
    assert "Row ID" in result.columns
    assert result["Row ID"].iloc[0] == "1"
    assert result["Order ID"].iloc[0] == "US-2024-001"


def test_load_data_casts_sales_to_float(tmp_path):
    path = _write_csv(tmp_path, _VALID_CSV_HEADER + _VALID_ROW)
    from src.data.loader import load_data

    result = load_data(path)
    assert result["Sales"].dtype == float


def test_load_data_raises_on_missing_file():
    from src.data.loader import load_data

    with pytest.raises(FileNotFoundError):
        load_data("nonexistent_path_xyz_123.csv")


def test_load_data_drops_nat_rows(tmp_path):
    bad_row = (
        "2,US-2024-002,invalid-date,01-07-2026,Standard Class,102,"
        "United States,Dallas,Texas,75001,Chocolate,Interior,"
        "CHO-MIL-31000,Wonka Bar - Milk Chocolate,5.00,1,3.00,2.00\n"
    )
    path = _write_csv(tmp_path, _VALID_CSV_HEADER + _VALID_ROW + bad_row)
    from src.data.loader import load_data

    result = load_data(path)
    # Bad row should be dropped; only the valid row remains
    assert len(result) == 1
    assert "US-2024-001" in result["Order ID"].values
