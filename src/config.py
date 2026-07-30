"""
config.py

Centralized, typed configuration for the Brent Oil Price Change Point
Analysis project. Replaces scattered magic numbers and hard-coded paths
with a single, documented source of truth used by src/, backend/, and
tests/.
"""

from dataclasses import dataclass
import os

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@dataclass(frozen=True)
class DataPaths:
    """Filesystem locations of project datasets."""
    data_dir: str = os.path.join(_PROJECT_ROOT, "data")
    brent_prices_csv: str = os.path.join(_PROJECT_ROOT, "data", "BrentOilPrices.csv")
    events_csv: str = os.path.join(_PROJECT_ROOT, "data", "events.csv")
    changepoint_json: str = os.path.join(_PROJECT_ROOT, "data", "change_point_results.json")


@dataclass(frozen=True)
class AnalysisConfig:
    """Parameters controlling the statistical analysis."""
    rolling_volatility_window_days: int = 30
    stationarity_alpha: float = 0.05
    min_required_events: int = 10


@dataclass(frozen=True)
class ServerConfig:
    """Flask backend runtime configuration."""
    host: str = "0.0.0.0"
    port: int = 5000
    debug: bool = True


DATA_PATHS = DataPaths()
ANALYSIS_CONFIG = AnalysisConfig()
SERVER_CONFIG = ServerConfig()
