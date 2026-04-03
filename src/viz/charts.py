"""
Plotly chart factory functions for the Nassau Candy Distributor dashboard.

All functions are pure — they take data and configuration parameters, build
a Plotly figure, and return it. No Streamlit imports. This makes each chart
independently testable and keeps presentation logic out of app.py.
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.config_loader import FactoryCoord


# ---------------------------------------------------------------------------
# Tab 1 — Route Efficiency Overview
# ---------------------------------------------------------------------------


def route_leaderboard_chart(
    route_df: pd.DataFrame,
    top_n: int,
    height: int,
    xaxis_max: int,
    color_scale: str,
) -> go.Figure:
    """
    Horizontal bar chart of the top-N routes ranked by efficiency score.

    Parameters
    ----------
    route_df : pd.DataFrame
        Output of ``compute_route_efficiency()``, sorted descending by score.
    top_n : int
        Number of routes to display.
    height : int
        Chart height in pixels.
    xaxis_max : int
        X-axis upper limit (should exceed 100 to give label room).
    color_scale : str
        Plotly color scale name (e.g. "RdYlGn").

    Returns
    -------
    go.Figure
    """
    top = route_df.head(top_n).sort_values("efficiency_score")
    fig = px.bar(
        top,
        x="efficiency_score",
        y="route_label",
        color="efficiency_score",
        color_continuous_scale=color_scale,
        orientation="h",
        text="efficiency_score",
        labels={
            "efficiency_score": "Efficiency Score (0–100)",
            "route_label": "Route (Factory → Region)",
        },
        title=f"Route Efficiency Leaderboard (Top {top_n})",
        range_color=[0, 100],
    )
    fig.update_traces(texttemplate="%{text:.1f}", textposition="outside")
    fig.update_layout(
        coloraxis_showscale=False,
        yaxis_title="",
        xaxis_range=[0, xaxis_max],
        height=height,
        margin=dict(l=0),
    )
    return fig


def factory_region_lead_time_chart(
    factory_region_df: pd.DataFrame,
    height: int,
) -> go.Figure:
    """
    Grouped bar chart of average lead time by factory, colored by region.

    Parameters
    ----------
    factory_region_df : pd.DataFrame
        Columns: ``factory``, ``Region``, ``avg_lead_time``.
    height : int
        Chart height in pixels.

    Returns
    -------
    go.Figure
    """
    fig = px.bar(
        factory_region_df,
        x="factory",
        y="avg_lead_time",
        color="Region",
        barmode="group",
        title="Avg Lead Time by Factory & Region",
        labels={"avg_lead_time": "Avg Lead Time (days)", "factory": "Factory"},
    )
    fig.update_layout(xaxis_tickangle=-20, height=height, legend_title="Region")
    return fig


# ---------------------------------------------------------------------------
# Tab 2 — Geographic Shipping Map
# ---------------------------------------------------------------------------


def state_choropleth_chart(
    state_df: pd.DataFrame,
    factory_coords: dict[str, FactoryCoord],
    height: int,
    color_scale: str,
) -> go.Figure:
    """
    US choropleth of average lead time with factory star markers overlaid.

    Parameters
    ----------
    state_df : pd.DataFrame
        Output of ``compute_state_metrics()``. Columns: ``state``,
        ``state_abbrev``, ``avg_lead_time``, ``order_count``.
    factory_coords : dict[str, FactoryCoord]
        Factory name → coordinates mapping from CONFIG.
    height : int
        Chart height in pixels.
    color_scale : str
        Plotly color scale (e.g. "RdYlGn_r" — red = high/bad).

    Returns
    -------
    go.Figure
    """
    fig = px.choropleth(
        state_df,
        locations="state_abbrev",
        locationmode="USA-states",
        color="avg_lead_time",
        scope="usa",
        color_continuous_scale=color_scale,
        hover_name="state",
        hover_data={"avg_lead_time": ":.0f", "order_count": True, "state_abbrev": False},
        labels={"avg_lead_time": "Avg Lead Time (days)", "order_count": "Orders"},
        title="Average Shipping Lead Time by US State",
    )

    factory_names = list(factory_coords.keys())
    fig.add_trace(
        go.Scattergeo(
            lat=[factory_coords[f].lat for f in factory_names],
            lon=[factory_coords[f].lon for f in factory_names],
            text=factory_names,
            mode="markers+text",
            marker=dict(size=14, color="navy", symbol="star"),
            textposition="top center",
            textfont=dict(size=11, color="navy"),
            name="Factories",
            geo="geo",
        )
    )

    fig.update_layout(
        geo=dict(showlakes=True, lakecolor="rgb(230,245,255)"),
        margin=dict(l=0, r=0, t=40, b=0),
        height=height,
        legend=dict(x=0.01, y=0.05),
    )
    return fig


def region_lead_time_bar_chart(
    region_df: pd.DataFrame,
    color_scale: str,
) -> go.Figure:
    """
    Bar chart of average lead time per region, sorted ascending.

    Parameters
    ----------
    region_df : pd.DataFrame
        Columns: ``Region``, ``avg_lead_time``.
    color_scale : str
        Plotly color scale.

    Returns
    -------
    go.Figure
    """
    fig = px.bar(
        region_df.sort_values("avg_lead_time"),
        x="Region",
        y="avg_lead_time",
        color="avg_lead_time",
        color_continuous_scale=color_scale,
        title="Avg Lead Time by Region",
        labels={"avg_lead_time": "Avg Lead Time (days)"},
        text="avg_lead_time",
    )
    fig.update_traces(texttemplate="%{text:.1f}d", textposition="outside")
    fig.update_layout(coloraxis_showscale=False, showlegend=False)
    return fig


def state_scatter_chart(
    state_sales_df: pd.DataFrame,
    height: int,
    color_scale: str,
) -> go.Figure:
    """
    Scatter plot of average lead time vs total revenue by state.

    Bubble size encodes order volume. Used in both Tab 2 and Tab 4 from the
    same pre-computed ``get_state_sales()`` result.

    Parameters
    ----------
    state_sales_df : pd.DataFrame
        Output of ``get_state_sales()``. Columns: ``State/Province``,
        ``avg_lead_time``, ``total_sales``, ``order_count``.
    height : int
        Chart height in pixels.
    color_scale : str
        Plotly color scale (e.g. "RdYlGn_r").

    Returns
    -------
    go.Figure
    """
    fig = px.scatter(
        state_sales_df,
        x="avg_lead_time",
        y="total_sales",
        size="order_count",
        hover_name="State/Province",
        color="avg_lead_time",
        color_continuous_scale=color_scale,
        title="Lead Time vs Revenue by State",
        labels={
            "avg_lead_time": "Avg Lead Time (days)",
            "total_sales": "Total Sales ($)",
            "order_count": "Orders",
        },
        height=height,
    )
    fig.update_layout(coloraxis_showscale=False)
    return fig


# ---------------------------------------------------------------------------
# Tab 3 — Ship Mode Comparison
# ---------------------------------------------------------------------------


def ship_mode_box_chart(
    df: pd.DataFrame,
    mode_order: list[str],
) -> go.Figure:
    """
    Box plot of relative lead time distribution by ship mode.

    Y-axis uses ``relative_lead_time`` (days above cohort floor) to isolate
    the ship-mode efficiency signal from dataset-level date offsets.

    Parameters
    ----------
    df : pd.DataFrame
        Enriched and filtered order DataFrame with ``relative_lead_time``.
    mode_order : list[str]
        Display order for ship mode categories.

    Returns
    -------
    go.Figure
    """
    fig = px.box(
        df,
        x="Ship Mode",
        y="relative_lead_time",
        color="Ship Mode",
        category_orders={"Ship Mode": mode_order},
        title="Relative Lead Time Distribution by Ship Mode",
        labels={"relative_lead_time": "Days Above Cohort Floor", "Ship Mode": ""},
        points="outliers",
    )
    fig.update_layout(showlegend=False)
    return fig


def ship_mode_region_bar_chart(
    mode_region_df: pd.DataFrame,
    mode_order: list[str],
) -> go.Figure:
    """
    Grouped bar chart of average lead time by region and ship mode.

    Parameters
    ----------
    mode_region_df : pd.DataFrame
        Columns: ``Ship Mode``, ``Region``, ``avg_lead_time``.
    mode_order : list[str]
        Display order for ship mode categories.

    Returns
    -------
    go.Figure
    """
    fig = px.bar(
        mode_region_df,
        x="Region",
        y="avg_lead_time",
        color="Ship Mode",
        barmode="group",
        category_orders={"Ship Mode": mode_order},
        title="Avg Lead Time by Region & Ship Mode",
        labels={"avg_lead_time": "Avg Lead Time (days)"},
    )
    return fig


def efficiency_heatmap_chart(
    route_df: pd.DataFrame,
    height: int,
    color_scale: str,
    zmin: int,
    zmax: int,
) -> go.Figure:
    """
    Annotated heatmap of efficiency score by factory × ship mode.

    Parameters
    ----------
    route_df : pd.DataFrame
        Output of ``compute_route_efficiency()``.
    height : int
        Chart height in pixels.
    color_scale : str
        Plotly color scale (e.g. "RdYlGn").
    zmin, zmax : int
        Color scale range anchors (typically 0 and 100).

    Returns
    -------
    go.Figure
    """
    pivot = route_df.pivot_table(
        index="factory",
        columns="Ship Mode",
        values="efficiency_score",
        aggfunc="mean",
    ).round(1)

    fig = px.imshow(
        pivot,
        color_continuous_scale=color_scale,
        title="Efficiency Score Heatmap: Factory × Ship Mode",
        labels=dict(color="Efficiency Score"),
        aspect="auto",
        zmin=zmin,
        zmax=zmax,
        text_auto=True,
    )
    fig.update_layout(height=height)
    return fig


# ---------------------------------------------------------------------------
# Tab 4 — Route Drill-Down
# ---------------------------------------------------------------------------


def state_lead_time_bar_chart(
    state_df: pd.DataFrame,
    height: int,
    color_scale: str,
) -> go.Figure:
    """
    Vertical bar chart ranking US states by average lead time (ascending).

    Parameters
    ----------
    state_df : pd.DataFrame
        Output of ``compute_state_metrics()``.
    height : int
        Chart height in pixels.
    color_scale : str
        Plotly color scale (e.g. "RdYlGn_r").

    Returns
    -------
    go.Figure
    """
    fig = px.bar(
        state_df.sort_values("avg_lead_time"),
        x="state",
        y="avg_lead_time",
        color="avg_lead_time",
        color_continuous_scale=color_scale,
        title="Avg Lead Time by State (US only)",
        labels={"avg_lead_time": "Avg Lead Time (days)", "state": "State"},
        height=height,
    )
    fig.update_layout(xaxis_tickangle=-45, coloraxis_showscale=False)
    return fig


def order_gantt_chart(
    timeline_df: pd.DataFrame,
    selected_state: str,
    height: int,
    color_map: dict[str, str],
) -> go.Figure:
    """
    Gantt / timeline chart showing order-to-ship spans per order.

    Each bar spans from ``order_date`` to ``ship_date``, color-coded by
    ship mode. Outlier orders are visually obvious as unusually long bars.

    Parameters
    ----------
    timeline_df : pd.DataFrame
        Output of ``get_order_timeline()``.
    selected_state : str
        State name for the chart title.
    height : int
        Chart height in pixels.
    color_map : dict[str, str]
        Ship mode → hex color mapping.

    Returns
    -------
    go.Figure
    """
    fig = px.timeline(
        timeline_df,
        x_start="order_date",
        x_end="ship_date",
        y="Order ID",
        color="Ship Mode",
        hover_data=["lead_time_days", "factory", "Sales"],
        title=f"Order-to-Ship Timeline: {selected_state} (latest {len(timeline_df)} orders)",
        color_discrete_map=color_map,
        labels={"lead_time_days": "Lead Time (days)"},
        height=height,
    )
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(xaxis_title="Date")
    return fig
