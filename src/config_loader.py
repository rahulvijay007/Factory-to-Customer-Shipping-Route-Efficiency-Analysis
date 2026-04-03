"""
Configuration loader for the Nassau Candy Distributor dashboard.

Parses config.yaml once at import time and exposes a typed AppConfig singleton.
All modules import CONFIG from here rather than loading YAML directly.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Typed configuration dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FactoryCoord:
    """Geographic coordinates for a factory location."""

    lat: float
    lon: float


@dataclass(frozen=True)
class ChartConfig:
    """Dimensions and style constants for Plotly charts."""

    leaderboard_top_n: int
    leaderboard_height: int
    leaderboard_xaxis_max: int
    factory_bar_height: int
    choropleth_height: int
    heatmap_height: int
    state_bar_height: int
    scatter_height: int
    gantt_height: int
    efficiency_color_scale: str
    lead_time_color_scale: str
    efficiency_zmin: int
    efficiency_zmax: int
    factory_marker_size: int
    factory_marker_color: str
    factory_text_size: int


@dataclass(frozen=True)
class UIConfig:
    """Streamlit UI strings and chart configuration."""

    page_title: str
    page_icon: str
    app_title: str
    app_caption: str
    ship_mode_order: tuple[str, ...]
    ship_mode_colors: dict[str, str]
    charts: ChartConfig


@dataclass(frozen=True)
class AnalyticsConfig:
    """Parameters controlling analytical calculations."""

    cluster_floors: tuple[int, ...]
    cluster_boundaries: tuple[int, ...]
    timeline_default_n: int


@dataclass(frozen=True)
class GeographyConfig:
    """Geographic reference data."""

    us_state_abbrev: dict[str, str]
    canadian_provinces: frozenset[str]


@dataclass(frozen=True)
class FactoriesConfig:
    """Factory-product relationships and coordinates."""

    product_map: dict[str, str]
    coordinates: dict[str, FactoryCoord]


@dataclass(frozen=True)
class DatasetConfig:
    """Dataset file location."""

    path: str


@dataclass(frozen=True)
class AppConfig:
    """Root application configuration."""

    dataset: DatasetConfig
    factories: FactoriesConfig
    geography: GeographyConfig
    analytics: AnalyticsConfig
    ui: UIConfig


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------


def load_config(path: str = "config.yaml") -> AppConfig:
    """
    Load and parse the application configuration from a YAML file.

    Parameters
    ----------
    path : str
        Path to the YAML configuration file. Defaults to "config.yaml".

    Returns
    -------
    AppConfig
        Fully typed, frozen configuration object.

    Raises
    ------
    RuntimeError
        If the config file does not exist or cannot be parsed.
    """
    config_path = Path(path)
    if not config_path.exists():
        raise RuntimeError(
            f"Configuration file not found: {config_path.resolve()!r}. "
            "Ensure config.yaml is present in the working directory."
        )

    try:
        with config_path.open("r", encoding="utf-8") as f:
            raw: dict = yaml.safe_load(f)
    except yaml.YAMLError as exc:
        raise RuntimeError(f"Failed to parse config.yaml: {exc}") from exc

    # ── Dataset ─────────────────────────────────────────────────────────────
    dataset_cfg = DatasetConfig(path=raw["dataset"]["path"])

    # ── Factories ───────────────────────────────────────────────────────────
    coords = {
        name: FactoryCoord(lat=float(c["lat"]), lon=float(c["lon"]))
        for name, c in raw["factories"]["coordinates"].items()
    }
    factories_cfg = FactoriesConfig(
        product_map=dict(raw["factories"]["product_map"]),
        coordinates=coords,
    )

    # ── Geography ───────────────────────────────────────────────────────────
    geography_cfg = GeographyConfig(
        us_state_abbrev=dict(raw["geography"]["us_state_abbrev"]),
        canadian_provinces=frozenset(raw["geography"]["canadian_provinces"]),
    )

    # ── Analytics ───────────────────────────────────────────────────────────
    analytics_raw = raw["analytics"]
    analytics_cfg = AnalyticsConfig(
        cluster_floors=tuple(int(x) for x in analytics_raw["cluster_floors"]),
        cluster_boundaries=tuple(int(x) for x in analytics_raw["cluster_boundaries"]),
        timeline_default_n=int(analytics_raw["timeline_default_n"]),
    )

    # ── UI / Charts ─────────────────────────────────────────────────────────
    ui_raw = raw["ui"]
    charts_raw = ui_raw["charts"]
    chart_cfg = ChartConfig(
        leaderboard_top_n=int(charts_raw["leaderboard_top_n"]),
        leaderboard_height=int(charts_raw["leaderboard_height"]),
        leaderboard_xaxis_max=int(charts_raw["leaderboard_xaxis_max"]),
        factory_bar_height=int(charts_raw["factory_bar_height"]),
        choropleth_height=int(charts_raw["choropleth_height"]),
        heatmap_height=int(charts_raw["heatmap_height"]),
        state_bar_height=int(charts_raw["state_bar_height"]),
        scatter_height=int(charts_raw["scatter_height"]),
        gantt_height=int(charts_raw["gantt_height"]),
        efficiency_color_scale=str(charts_raw["efficiency_color_scale"]),
        lead_time_color_scale=str(charts_raw["lead_time_color_scale"]),
        efficiency_zmin=int(charts_raw["efficiency_zmin"]),
        efficiency_zmax=int(charts_raw["efficiency_zmax"]),
        factory_marker_size=int(charts_raw["factory_marker_size"]),
        factory_marker_color=str(charts_raw["factory_marker_color"]),
        factory_text_size=int(charts_raw["factory_text_size"]),
    )
    ui_cfg = UIConfig(
        page_title=str(ui_raw["page_title"]),
        page_icon=str(ui_raw["page_icon"]),
        app_title=str(ui_raw["app_title"]),
        app_caption=str(ui_raw["app_caption"]),
        ship_mode_order=tuple(ui_raw["ship_mode_order"]),
        ship_mode_colors=dict(ui_raw["ship_mode_colors"]),
        charts=chart_cfg,
    )

    config = AppConfig(
        dataset=dataset_cfg,
        factories=factories_cfg,
        geography=geography_cfg,
        analytics=analytics_cfg,
        ui=ui_cfg,
    )
    logger.info("Configuration loaded from %s", config_path.resolve())
    return config


# ---------------------------------------------------------------------------
# Module-level singleton — loaded once per process
# ---------------------------------------------------------------------------

CONFIG: AppConfig = load_config()
