"""
eda_utils.py

Reusable analysis and plotting functions for the Brent oil price EDA:
log returns, stationarity testing, rolling volatility, and standard plots.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from statsmodels.tsa.stattools import adfuller


class AnalysisError(Exception):
    """Raised when an analysis function receives invalid input."""
    pass


def compute_log_returns(df: pd.DataFrame, price_col: str = "Price") -> pd.DataFrame:
    """
    Compute daily log returns: log(price_t) - log(price_{t-1}).

    Parameters
    ----------
    df : pd.DataFrame
        Must contain a numeric price column and be sorted by date.
    price_col : str
        Name of the price column.

    Returns
    -------
    pd.DataFrame
        Copy of df with an added "Log_Return" column, first row (NaN) dropped.

    Raises
    ------
    AnalysisError
        If price_col is missing or contains non-positive values (log undefined).
    """
    if price_col not in df.columns:
        raise AnalysisError(f"Column '{price_col}' not found in DataFrame.")

    if (df[price_col] <= 0).any():
        raise AnalysisError(
            f"Column '{price_col}' contains non-positive values; "
            f"log returns are undefined for price <= 0."
        )

    out = df.copy()
    out["Log_Return"] = np.log(out[price_col]) - np.log(out[price_col].shift(1))
    out = out.dropna(subset=["Log_Return"]).reset_index(drop=True)
    return out


def run_adf_test(series: pd.Series, label: str = "series") -> dict:
    """
    Run the Augmented Dickey-Fuller stationarity test.

    Parameters
    ----------
    series : pd.Series
        Numeric series to test (e.g. raw prices or log returns).
    label : str
        Human-readable name for logging/printing purposes.

    Returns
    -------
    dict
        Keys: "label", "adf_statistic", "p_value", "critical_values", "is_stationary".

    Raises
    ------
    AnalysisError
        If the series is empty or contains NaN values.
    """
    if series.empty:
        raise AnalysisError(f"Cannot run ADF test on empty series ('{label}').")
    if series.isna().any():
        raise AnalysisError(f"Series '{label}' contains NaN values; drop them before testing.")

    result = adfuller(series)
    return {
        "label": label,
        "adf_statistic": result[0],
        "p_value": result[1],
        "critical_values": result[4],
        "is_stationary": result[1] < 0.05,
    }


def compute_rolling_volatility(
    df: pd.DataFrame, return_col: str = "Log_Return", window: int = 30
) -> pd.DataFrame:
    """
    Compute rolling standard deviation of returns as a volatility proxy.

    Parameters
    ----------
    df : pd.DataFrame
        Must contain return_col.
    return_col : str
        Name of the returns column.
    window : int
        Rolling window size in trading days.

    Returns
    -------
    pd.DataFrame
        Copy of df with an added f"Rolling_Volatility_{window}d" column.

    Raises
    ------
    AnalysisError
        If return_col is missing or window is not a positive integer.
    """
    if return_col not in df.columns:
        raise AnalysisError(f"Column '{return_col}' not found in DataFrame.")
    if not isinstance(window, int) or window <= 0:
        raise AnalysisError(f"window must be a positive integer, got {window}.")

    out = df.copy()
    out[f"Rolling_Volatility_{window}d"] = out[return_col].rolling(window=window).std()
    return out


def plot_price_series(df: pd.DataFrame, save_path: str = None, show: bool = True):
    """Plot the raw price series over time, optionally saving to save_path."""
    if "Date" not in df.columns or "Price" not in df.columns:
        raise AnalysisError("DataFrame must contain 'Date' and 'Price' columns.")

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(df["Date"], df["Price"], linewidth=0.8, color="#1f4e79")
    ax.set_title("Brent Crude Oil Price (Daily), 1987-2022", fontsize=14, fontweight="bold")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price (USD per barrel)")
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150)
    if show:
        plt.show()
    else:
        plt.close(fig)


def plot_log_returns(df: pd.DataFrame, save_path: str = None, show: bool = True):
    """Plot daily log returns over time, optionally saving to save_path."""
    if "Date" not in df.columns or "Log_Return" not in df.columns:
        raise AnalysisError("DataFrame must contain 'Date' and 'Log_Return' columns.")

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(df["Date"], df["Log_Return"], linewidth=0.5, color="#833C0C")
    ax.set_title("Brent Crude Oil Daily Log Returns, 1987-2022", fontsize=14, fontweight="bold")
    ax.set_xlabel("Date")
    ax.set_ylabel("Log Return")
    ax.axhline(0, color="black", linewidth=0.5)
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150)
    if show:
        plt.show()
    else:
        plt.close(fig)


def plot_rolling_volatility(
    df: pd.DataFrame, vol_col: str = "Rolling_Volatility_30d",
    save_path: str = None, show: bool = True
):
    """Plot rolling volatility over time, optionally saving to save_path."""
    if "Date" not in df.columns or vol_col not in df.columns:
        raise AnalysisError(f"DataFrame must contain 'Date' and '{vol_col}' columns.")

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(df["Date"], df[vol_col], color="#7B1F3A", linewidth=0.9)
    ax.set_title("Brent Crude Oil - 30-Day Rolling Volatility of Log Returns",
                 fontsize=14, fontweight="bold")
    ax.set_xlabel("Date")
    ax.set_ylabel("Rolling Std Dev of Log Returns")
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150)
    if show:
        plt.show()
    else:
        plt.close(fig)


def plot_events_overlay(
    price_df: pd.DataFrame, events_df: pd.DataFrame,
    save_path: str = None, show: bool = True
):
    """Plot the price series with vertical lines marking researched events."""
    required_price_cols = {"Date", "Price"}
    required_event_cols = {"Date", "Category"}
    if not required_price_cols.issubset(price_df.columns):
        raise AnalysisError(f"price_df must contain columns {required_price_cols}.")
    if not required_event_cols.issubset(events_df.columns):
        raise AnalysisError(f"events_df must contain columns {required_event_cols}.")

    colors = {
        "Geopolitical Conflict": "#C0392B", "OPEC Policy": "#27AE60",
        "Economic Shock": "#8E44AD", "Sanctions/Policy": "#F39C12",
        "Market Event": "#16A085", "Geopolitical Shock": "#C0392B",
    }

    fig, ax = plt.subplots(figsize=(16, 7))
    ax.plot(price_df["Date"], price_df["Price"], linewidth=0.7, color="#1f4e79", zorder=1)

    for _, row in events_df.iterrows():
        color = colors.get(row["Category"], "gray")
        ax.axvline(row["Date"], color=color, linestyle="--", alpha=0.5, linewidth=1, zorder=0)

    ax.set_title("Brent Crude Oil Price with Key Events Overlaid, 1987-2022",
                 fontsize=14, fontweight="bold")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price (USD per barrel)")

    legend_elements = [
        Line2D([0], [0], color=c, linestyle="--", lw=1.5, label=cat)
        for cat, c in colors.items() if cat in events_df["Category"].values
    ]
    ax.legend(handles=legend_elements, loc="upper left", fontsize=8)

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150)
    if show:
        plt.show()
    else:
        plt.close(fig)