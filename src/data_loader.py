"""
data_loader.py

Functions for loading and validating the Brent oil price dataset and the
researched events dataset used in the Week 10 change point analysis project.

The raw Brent price file mixes two date formats across its history:
    - "20-May-87"    (day-month-abbreviated 2-digit year)  -> most rows
    - "Apr 22, 2020" (month day, 4-digit year)              -> ~651 recent rows
load_brent_prices() detects and handles both automatically.
"""

import os
import pandas as pd

from config import ANALYSIS_CONFIG


class DataLoadError(Exception):
    """Raised when the Brent price or events dataset cannot be loaded or validated."""
    pass


def _parse_mixed_dates(date_series: pd.Series) -> pd.Series:
    """
    Parse a Series of date strings that may use either of two known formats.

    Parameters
    ----------
    date_series : pd.Series
        Raw date strings, e.g. "20-May-87" or "Apr 22, 2020".

    Returns
    -------
    pd.Series
        Parsed datetime64 values.

    Raises
    ------
    DataLoadError
        If any date strings remain unparsed after both known formats are tried.
    """
    parsed = pd.to_datetime(date_series, format="%d-%b-%y", errors="coerce")

    failed_mask = parsed.isna()
    if failed_mask.any():
        parsed.loc[failed_mask] = pd.to_datetime(
            date_series.loc[failed_mask], format="%b %d, %Y", errors="coerce"
        )

    still_failed = parsed.isna()
    if still_failed.any():
        bad_values = date_series.loc[still_failed].unique()
        raise DataLoadError(
            f"{still_failed.sum()} date value(s) could not be parsed with either "
            f"known format. Examples of unparsed values: {list(bad_values[:5])}"
        )

    return parsed


def load_brent_prices(filepath: str) -> pd.DataFrame:
    """
    Load, clean, and validate the raw Brent oil price CSV.

    Parameters
    ----------
    filepath : str
        Path to BrentOilPrices.csv (columns: Date, Price).

    Returns
    -------
    pd.DataFrame
        Cleaned DataFrame with columns ["Date", "Price"], sorted by Date,
        Date as datetime64, Price as float, no duplicate dates, no nulls.

    Raises
    ------
    DataLoadError
        If the file is missing, has unexpected columns, contains unparsable
        dates, or contains missing/duplicate values after cleaning.
    """
    if not os.path.exists(filepath):
        raise DataLoadError(f"File not found: {filepath}")

    try:
        df = pd.read_csv(filepath)
    except Exception as exc:
        raise DataLoadError(f"Failed to read CSV at {filepath}: {exc}") from exc

    expected_cols = {"Date", "Price"}
    if not expected_cols.issubset(df.columns):
        raise DataLoadError(
            f"Expected columns {expected_cols}, found {set(df.columns)}"
        )

    df["Date"] = _parse_mixed_dates(df["Date"])

    if df["Price"].isna().any():
        n_missing = df["Price"].isna().sum()
        raise DataLoadError(f"{n_missing} row(s) have a missing Price value.")

    df = df.sort_values("Date").reset_index(drop=True)

    n_dupes = df["Date"].duplicated().sum()
    if n_dupes > 0:
        raise DataLoadError(f"Found {n_dupes} duplicate Date value(s) after parsing.")

    return df


def load_events(filepath: str) -> pd.DataFrame:
    """
    Load and validate the researched events dataset.

    Parameters
    ----------
    filepath : str
        Path to events.csv (columns: Date, Event_Name, Category,
        Description, Expected_Impact).

    Returns
    -------
    pd.DataFrame
        Validated DataFrame with Date parsed as datetime64.

    Raises
    ------
    DataLoadError
        If the file is missing, has unexpected columns, or has too few
        events to meet the assignment's minimum (10).
    """
    if not os.path.exists(filepath):
        raise DataLoadError(f"File not found: {filepath}")

    try:
        events_df = pd.read_csv(filepath)
    except Exception as exc:
        raise DataLoadError(f"Failed to read CSV at {filepath}: {exc}") from exc

    expected_cols = {"Date", "Event_Name", "Category", "Description", "Expected_Impact"}
    if not expected_cols.issubset(events_df.columns):
        raise DataLoadError(
            f"Expected columns {expected_cols}, found {set(events_df.columns)}"
        )

    try:
        events_df["Date"] = pd.to_datetime(events_df["Date"], format="%Y-%m-%d")
    except Exception as exc:
        raise DataLoadError(f"Failed to parse event dates: {exc}") from exc

    if len(events_df) < ANALYSIS_CONFIG.min_required_events:
        raise DataLoadError(
            f"Events dataset has only {len(events_df)} rows; assignment "
            f"requires a minimum of {ANALYSIS_CONFIG.min_required_events}."
        )

    return events_df