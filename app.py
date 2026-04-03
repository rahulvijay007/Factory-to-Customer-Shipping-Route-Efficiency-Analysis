"""
Nassau Candy Distributor — Shipping Route Efficiency Dashboard
Streamlit orchestrator: loads data, manages sidebar filters, caches computed
results in session state, renders four tab modules via chart factory functions.
"""

from __future__ import annotations

import logging

import streamlit as st

from src.config_loader import CONFIG
from src.analytics.filters import apply_filters
from src.analytics.geography import compute_state_metrics, get_order_timeline, get_state_sales
from src.analytics.kpis import compute_kpis
from src.analytics.routes import compute_route_efficiency
from src.data.enricher import enrich_data
from src.data.loader import load_data
from src.viz import charts

logging.basicConfig(level=logging.INFO, format="%(name)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# App configuration
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title=CONFIG.ui.page_title,
    page_icon=CONFIG.ui.page_icon,
    layout="wide",
    initial_sidebar_state="expanded",
)
st.title(CONFIG.ui.app_title)
st.caption(CONFIG.ui.app_caption)


# ---------------------------------------------------------------------------
# Cached data load
# ---------------------------------------------------------------------------

@st.cache_data
def get_data() -> "pd.DataFrame":  # noqa: F821
    df = load_data()
    return enrich_data(df)


try:
    df_all = get_data()
except FileNotFoundError as exc:
    st.error(f"Could not load dataset: {exc}")
    st.stop()
except ValueError as exc:
    st.error(f"Data validation error: {exc}")
    st.stop()


# ---------------------------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------------------------

st.sidebar.header("Filters")

min_date = df_all["order_date"].min().date()
max_date = df_all["order_date"].max().date()

date_input = st.sidebar.date_input(
    "Order Date Range",
    value=[min_date, max_date],
    min_value=min_date,
    max_value=max_date,
)
date_from, date_to = (
    (date_input[0], date_input[1])
    if isinstance(date_input, (list, tuple)) and len(date_input) == 2
    else (min_date, max_date)
)

regions: list[str] = st.sidebar.multiselect(
    "Region",
    options=sorted(df_all["Region"].dropna().unique()),
    default=[],
    placeholder="All regions",
)

ship_modes: list[str] = st.sidebar.multiselect(
    "Ship Mode",
    options=list(CONFIG.ui.ship_mode_order),
    default=[],
    placeholder="All modes",
)

lt_min = int(df_all["lead_time_days"].min())
lt_max = int(df_all["lead_time_days"].max())
threshold: int = st.sidebar.slider(
    "Lead-Time Threshold (days)",
    min_value=lt_min,
    max_value=lt_max,
    value=lt_min + 7,
    step=10,
    help="Shipments exceeding this threshold count toward the Delay Frequency KPI. Does not filter the data.",
)

st.sidebar.info(
    "**Note on Lead Times**\n\n"
    "This dataset contains lead times of 900–1640 days (a structural artifact of "
    "the order-fulfillment schedule). The *Efficiency Score* uses *relative lead time* "
    "— days above the cohort minimum — which isolates the 0–11 day variation driven "
    "by route and ship mode."
)


# ---------------------------------------------------------------------------
# Session state — compute expensive results once per filter change
# ---------------------------------------------------------------------------

filter_key = (date_from, date_to, tuple(sorted(regions)), tuple(sorted(ship_modes)), threshold)

if st.session_state.get("filter_key") != filter_key:
    _fdf = apply_filters(df_all, (date_from, date_to), regions, ship_modes)
    st.session_state["filtered_df"]  = _fdf
    st.session_state["route_df"]     = compute_route_efficiency(_fdf)
    st.session_state["state_df"]     = compute_state_metrics(_fdf)
    st.session_state["state_sales"]  = get_state_sales(_fdf)
    st.session_state["kpis"]         = compute_kpis(_fdf, threshold)
    st.session_state["filter_key"]   = filter_key
    logger.info("Filter state changed — recomputed session results")

filtered_df  = st.session_state["filtered_df"]
route_df     = st.session_state["route_df"]
state_df     = st.session_state["state_df"]
state_sales  = st.session_state["state_sales"]
kpis         = st.session_state["kpis"]

if filtered_df.empty:
    st.warning("No data matches the current filter selection. Adjust the sidebar filters.")
    st.stop()


# ---------------------------------------------------------------------------
# KPI banner
# ---------------------------------------------------------------------------

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Orders", f"{kpis['total_orders']:,}")
k2.metric(
    "Avg Lead Time",
    f"{kpis['avg_lead_time']:.0f} days",
    delta=f"Rel: +{kpis['avg_relative_lead_time']:.1f}d above floor",
    delta_color="inverse",
)
k3.metric(
    "Delay Frequency",
    f"{kpis['delay_frequency']:.1f}%",
    delta=f">{threshold} days threshold",
    delta_color="inverse",
)
k4.metric(
    "Total Revenue",
    f"${kpis['total_revenue']:,.0f}",
    delta=f"Profit: ${kpis['total_profit']:,.0f}",
)
st.divider()

cfg = CONFIG.ui.charts  # shorthand


# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------

tab1, tab2, tab3, tab4 = st.tabs([
    "Route Efficiency Overview",
    "Geographic Shipping Map",
    "Ship Mode Comparison",
    "Route Drill-Down",
])

# ── Tab 1: Route Efficiency Overview ────────────────────────────────────────
with tab1:
    if route_df.empty:
        st.info("No route data available for current filters.")
    else:
        col_left, col_right = st.columns([6, 4])

        with col_left:
            try:
                st.plotly_chart(
                    charts.route_leaderboard_chart(
                        route_df, cfg.leaderboard_top_n, cfg.leaderboard_height,
                        cfg.leaderboard_xaxis_max, cfg.efficiency_color_scale,
                    ),
                    use_container_width=True,
                )
            except Exception as exc:
                logger.error("route_leaderboard_chart failed: %s", exc)
                st.warning("Leaderboard chart could not be rendered.")

        with col_right:
            factory_region = (
                filtered_df.groupby(["factory", "Region"])["lead_time_days"]
                .mean().round(1).reset_index()
                .rename(columns={"lead_time_days": "avg_lead_time"})
            )
            try:
                st.plotly_chart(
                    charts.factory_region_lead_time_chart(factory_region, cfg.factory_bar_height),
                    use_container_width=True,
                )
            except Exception as exc:
                logger.error("factory_region_lead_time_chart failed: %s", exc)
                st.warning("Factory/Region chart could not be rendered.")

        st.subheader("All Routes — Performance Table")
        display_cols = {
            "factory": "Factory", "Region": "Region", "Ship Mode": "Ship Mode",
            "order_count": "Orders", "avg_lead_time": "Avg Lead Time (days)",
            "avg_relative_lt": "Relative Lead Time (days)", "efficiency_score": "Efficiency Score",
        }
        st.dataframe(
            route_df.rename(columns=display_cols)[list(display_cols.values())],
            use_container_width=True, hide_index=True,
        )

# ── Tab 2: Geographic Shipping Map ─────────────────────────────────────────
with tab2:
    if state_df.empty:
        st.info("No US state data available for current filters.")
    else:
        try:
            st.plotly_chart(
                charts.state_choropleth_chart(
                    state_df, CONFIG.factories.coordinates,
                    cfg.choropleth_height, cfg.lead_time_color_scale,
                ),
                use_container_width=True,
            )
        except Exception as exc:
            logger.error("state_choropleth_chart failed: %s", exc)
            st.warning("Choropleth map could not be rendered.")

        st.caption(
            "Canadian provinces (~200 orders) are excluded from this map but included "
            "in all KPIs, tables, and other charts."
        )

        bot_left, bot_right = st.columns(2)
        with bot_left:
            region_sum = (
                filtered_df.groupby("Region")["lead_time_days"]
                .mean().round(1).reset_index()
                .rename(columns={"lead_time_days": "avg_lead_time"})
            )
            try:
                st.plotly_chart(
                    charts.region_lead_time_bar_chart(region_sum, cfg.lead_time_color_scale),
                    use_container_width=True,
                )
            except Exception as exc:
                logger.error("region_lead_time_bar_chart failed: %s", exc)
                st.warning("Region chart could not be rendered.")

        with bot_right:
            if not state_sales.empty:
                try:
                    st.plotly_chart(
                        charts.state_scatter_chart(state_sales, cfg.scatter_height, cfg.lead_time_color_scale),
                        use_container_width=True,
                        key="scatter_tab2",
                    )
                except Exception as exc:
                    logger.error("state_scatter_chart (Tab 2) failed: %s", exc)
                    st.warning("Scatter chart could not be rendered.")

# ── Tab 3: Ship Mode Comparison ─────────────────────────────────────────────
with tab3:
    mode_order = list(CONFIG.ui.ship_mode_order)
    top_left, top_right = st.columns(2)

    with top_left:
        try:
            st.plotly_chart(
                charts.ship_mode_box_chart(filtered_df, mode_order),
                use_container_width=True,
            )
        except Exception as exc:
            logger.error("ship_mode_box_chart failed: %s", exc)
            st.warning("Box plot could not be rendered.")
        st.caption(
            "Y-axis shows days above the cohort-minimum lead time, isolating the "
            "ship-mode efficiency signal from dataset-level date artifacts."
        )

    with top_right:
        mode_region = (
            filtered_df.groupby(["Ship Mode", "Region"])["lead_time_days"]
            .mean().round(1).reset_index()
            .rename(columns={"lead_time_days": "avg_lead_time"})
        )
        try:
            st.plotly_chart(
                charts.ship_mode_region_bar_chart(mode_region, mode_order),
                use_container_width=True,
            )
        except Exception as exc:
            logger.error("ship_mode_region_bar_chart failed: %s", exc)
            st.warning("Ship mode/region chart could not be rendered.")

    if not route_df.empty:
        try:
            st.plotly_chart(
                charts.efficiency_heatmap_chart(
                    route_df, cfg.heatmap_height,
                    cfg.efficiency_color_scale, cfg.efficiency_zmin, cfg.efficiency_zmax,
                ),
                use_container_width=True,
            )
        except Exception as exc:
            logger.error("efficiency_heatmap_chart failed: %s", exc)
            st.warning("Heatmap could not be rendered.")

    mode_perf = filtered_df.groupby("Ship Mode")["relative_lead_time"].mean().round(2)
    if not mode_perf.empty:
        best_mode, worst_mode = mode_perf.idxmin(), mode_perf.idxmax()
        col_a, col_b = st.columns(2)
        col_a.success(
            f"**Most efficient ship mode:** {best_mode}  \n"
            f"Avg {mode_perf[best_mode]:.1f} days above cohort floor"
        )
        col_b.warning(
            f"**Least efficient ship mode:** {worst_mode}  \n"
            f"Avg {mode_perf[worst_mode]:.1f} days above cohort floor"
        )

# ── Tab 4: Route Drill-Down ─────────────────────────────────────────────────
with tab4:
    drill_left, drill_right = st.columns(2)

    with drill_left:
        if not state_df.empty:
            try:
                st.plotly_chart(
                    charts.state_lead_time_bar_chart(state_df, cfg.state_bar_height, cfg.lead_time_color_scale),
                    use_container_width=True,
                )
            except Exception as exc:
                logger.error("state_lead_time_bar_chart failed: %s", exc)
                st.warning("State bar chart could not be rendered.")

    with drill_right:
        if not state_sales.empty:
            try:
                st.plotly_chart(
                    charts.state_scatter_chart(state_sales, cfg.scatter_height, cfg.lead_time_color_scale),
                    use_container_width=True,
                    key="scatter_tab4",
                )
            except Exception as exc:
                logger.error("state_scatter_chart (Tab 4) failed: %s", exc)
                st.warning("Scatter chart could not be rendered.")

    st.subheader("Order-to-Ship Timeline")
    all_states = sorted(filtered_df["State/Province"].dropna().unique())
    selected_state: str = st.selectbox("Select State / Province", options=all_states)

    state_orders = get_order_timeline(
        filtered_df[filtered_df["State/Province"] == selected_state]
    )

    if state_orders.empty:
        st.info("No orders for the selected state under current filters.")
    else:
        try:
            st.plotly_chart(
                charts.order_gantt_chart(
                    state_orders, selected_state,
                    cfg.gantt_height, dict(CONFIG.ui.ship_mode_colors),
                ),
                use_container_width=True,
            )
        except Exception as exc:
            logger.error("order_gantt_chart failed: %s", exc)
            st.warning("Gantt chart could not be rendered.")
        st.caption(
            f"Each bar spans from Order Date to Ship Date. "
            f"Showing up to {CONFIG.analytics.timeline_default_n} most recent orders for {selected_state}."
        )
