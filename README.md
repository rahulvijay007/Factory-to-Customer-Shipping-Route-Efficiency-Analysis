# Factory-to-Customer Shipping Route Efficiency Analysis
### Nassau Candy Distributor — Logistics Analytics Dashboard

A Streamlit web application that transforms raw order and shipment data into route-level operational intelligence for Nassau Candy Distributor. The dashboard enables data-driven decisions on logistics performance, shipping delays, and route efficiency across US regions.

---

## Background

Nassau Candy Distributor ships products from five factories to customers across multiple US regions. Shipping efficiency directly affects customer satisfaction and operational cost, yet logistics decisions were previously made without route-level visibility.

This project identifies which factory-to-customer routes are efficient, which experience delays, and where geographic bottlenecks exist — turning reactive logistics into a proactive, data-driven discipline.

---

## Dashboard Modules

| Tab | Description |
|---|---|
| **Route Efficiency Overview** | Efficiency leaderboard (0–100 score), avg lead time by factory & region, full sortable route table |
| **Geographic Shipping Map** | US state choropleth of lead times, factory location markers, regional summary |
| **Ship Mode Comparison** | Lead time distribution by ship mode, region × mode grouped bar, factory × mode heatmap |
| **Route Drill-Down** | State performance ranking, lead time vs revenue scatter, order-to-ship Gantt timeline |

**Sidebar Filters:** Date range · Region · Ship Mode · Delay-threshold slider

---

## Key Metrics

| KPI | Definition |
|---|---|
| Shipping Lead Time | `Ship Date − Order Date` (days) |
| Average Lead Time | Mean lead time per route |
| Route Efficiency Score | 0–100, normalized from relative lead time (100 = fastest) |
| Delay Frequency | % of orders exceeding the user-defined threshold |
| Route Volume | Order count per factory → region → ship mode |

> **Note on lead times:** This dataset contains lead times of 900–1640 days, a structural artifact of the order-fulfillment schedule. The Efficiency Score uses *relative lead time* — days above each cohort's minimum — which isolates the 0–11 day variation driven by route and ship mode choice.

---

## Project Structure

```
.
├── app.py                      # Streamlit orchestrator (≤200 lines)
├── config.yaml                 # All configurable values (factories, colors, chart sizes, etc.)
├── requirements.txt
├── Dataset/
│   └── Nassau Candy Distributor.csv
├── src/
│   ├── config_loader.py        # Typed AppConfig dataclass, CONFIG singleton
│   ├── data/
│   │   ├── loader.py           # CSV ingestion, type casting, date parsing
│   │   ├── enricher.py         # Feature engineering (lead time, factory map, etc.)
│   │   └── schema.py           # pandera schema validation
│   ├── analytics/
│   │   ├── filters.py          # apply_filters()
│   │   ├── kpis.py             # KPIResult TypedDict + compute_kpis()
│   │   ├── routes.py           # compute_route_efficiency()
│   │   └── geography.py        # compute_state_metrics(), get_state_sales(), get_order_timeline()
│   └── viz/
│       └── charts.py           # 10 pure Plotly chart factory functions
└── tests/
    ├── conftest.py
    ├── test_loader.py
    ├── test_enricher.py
    └── test_analytics.py
```

---

## Setup

**Prerequisites:** Python 3.12+

```bash
# 1. Clone the repository
git clone <repo-url>
cd <project-directory>

# 2. Create and activate a virtual environment
python -m venv venv
source venv/Scripts/activate      # Windows (Git Bash)
# source venv/bin/activate         # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch the dashboard
streamlit run app.py
```

The app opens at **http://localhost:8501**.

---

## Running Tests

```bash
source venv/Scripts/activate
pytest tests/ -v
```

28 unit tests cover: data loading, feature engineering, all analytics functions (filters, KPIs, route efficiency, geographic aggregations).

---

## Tech Stack

| Library | Version | Purpose |
|---|---|---|
| Streamlit | 1.56.0 | Web dashboard framework |
| Pandas | 3.0.2 | Data manipulation |
| Plotly | 6.6.0 | Interactive charts and maps |
| NumPy | 2.4.4 | Vectorized operations |
| pandera | 0.30.1 | DataFrame schema validation |
| PyYAML | 6.0.3 | Configuration loading |
| pytest | 9.0.2 | Unit testing |

---

## Factories

| Factory | Location (Lat, Lon) | Products |
|---|---|---|
| Lot's O' Nuts | 32.88, −111.77 (Arizona) | Wonka Bar – Nutty Crunch Surprise, Fudge Mallows, Scrumdiddlyumptious |
| Wicked Choccy's | 32.08, −81.09 (Georgia) | Wonka Bar – Milk Chocolate, Triple Dazzle Caramel |
| Sugar Shack | 48.12, −96.18 (Minnesota) | Laffy Taffy, SweeTARTS, Nerds, Fun Dip, Fizzy Lifting Drinks |
| Secret Factory | 41.45, −90.57 (Illinois) | Everlasting Gobstopper, Lickable Wallpaper, Wonka Gum |
| The Other Factory | 35.12, −89.97 (Tennessee) | Hair Toffee, Kazookles |

---

## Dataset

**File:** `Dataset/Nassau Candy Distributor.csv`  
**Rows:** 10,194 orders · **Columns:** 18  
**Order dates:** January 2024 – December 2025  
**Ship modes:** Standard Class · Second Class · First Class · Same Day  
**Regions:** Atlantic · Gulf · Interior · Pacific  
**Countries:** United States (9,994 rows) · Canada (200 rows)

---

## Configuration

All hardcoded values live in `config.yaml` — factory mappings, coordinates, US state abbreviations, chart dimensions, color scales, and UI strings. No values are hardcoded in Python source files.

To modify chart colors or sizes, edit `config.yaml` and restart the app. No code changes required.

---

*Unified Mentor Internship Project · Nassau Candy Distributor*
