"""
Unit tests for src/data_loader.py and src/eda_utils.py.

Run with:
    pytest tests/
from the project root (with venv activated).
"""

import os
import sys
import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from data_loader import load_brent_prices, load_events, DataLoadError, _parse_mixed_dates
from eda_utils import (
    compute_log_returns, run_adf_test, compute_rolling_volatility, AnalysisError
)

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


# ---- data_loader tests ----

def test_load_brent_prices_success():
    df = load_brent_prices(os.path.join(DATA_DIR, "BrentOilPrices.csv"))
    assert list(df.columns) == ["Date", "Price"]
    assert df["Date"].is_monotonic_increasing
    assert df["Date"].duplicated().sum() == 0
    assert df["Price"].isna().sum() == 0
    assert len(df) > 8000


def test_load_brent_prices_missing_file():
    with pytest.raises(DataLoadError, match="File not found"):
        load_brent_prices("nonexistent_file.csv")


def test_parse_mixed_dates_handles_both_formats():
    s = pd.Series(["20-May-87", "Apr 22, 2020"])
    result = _parse_mixed_dates(s)
    assert result.notna().all()
    assert result.iloc[0].year == 1987
    assert result.iloc[1].year == 2020


def test_parse_mixed_dates_raises_on_bad_input():
    s = pd.Series(["not-a-date", "also-not-a-date"])
    with pytest.raises(DataLoadError):
        _parse_mixed_dates(s)


def test_load_events_success():
    df = load_events(os.path.join(DATA_DIR, "events.csv"))
    assert len(df) >= 10
    assert "Category" in df.columns
    assert pd.api.types.is_datetime64_any_dtype(df["Date"])


def test_load_events_missing_file():
    with pytest.raises(DataLoadError, match="File not found"):
        load_events("nonexistent_events.csv")


# ---- eda_utils tests ----

def test_compute_log_returns():
    df = pd.DataFrame({"Price": [100, 110, 105]})
    result = compute_log_returns(df)
    assert "Log_Return" in result.columns
    assert len(result) == 2  # first row dropped (NaN from shift)


def test_compute_log_returns_rejects_non_positive_price():
    df = pd.DataFrame({"Price": [100, -5, 105]})
    with pytest.raises(AnalysisError, match="non-positive"):
        compute_log_returns(df)


def test_run_adf_test_returns_expected_keys():
    df = pd.DataFrame({"Price": range(1, 101)})
    returns_df = compute_log_returns(df.assign(Price=df["Price"] + 100))
    result = run_adf_test(returns_df["Log_Return"], label="test_series")
    assert set(result.keys()) == {
        "label", "adf_statistic", "p_value", "critical_values", "is_stationary"
    }


def test_run_adf_test_rejects_empty_series():
    with pytest.raises(AnalysisError, match="empty"):
        run_adf_test(pd.Series(dtype=float), label="empty")


def test_compute_rolling_volatility():
    df = pd.DataFrame({"Log_Return": [0.01, -0.02, 0.03, 0.01, -0.01] * 10})
    result = compute_rolling_volatility(df, window=5)
    assert "Rolling_Volatility_5d" in result.columns


def test_compute_rolling_volatility_rejects_invalid_window():
    df = pd.DataFrame({"Log_Return": [0.01, -0.02, 0.03]})
    with pytest.raises(AnalysisError, match="positive integer"):
        compute_rolling_volatility(df, window=-1)