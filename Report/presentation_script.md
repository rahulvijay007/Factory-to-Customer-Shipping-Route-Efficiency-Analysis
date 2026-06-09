# Presentation Script — Internship Review 1
**Project:** Shipping Route Efficiency Analysis | **Presenter:** Rahul Vijay
**Total Duration:** ~5 minutes | **Slides:** 9

---

## Slide 1 — Title Slide *(~15 seconds)*

Good morning, everyone. My name is Rahul Vijay, and I am a Machine Learning Intern at Unified Mentor Pvt. Ltd. Today I will be presenting my first internship review, which covers the work I have done on Shipping Route Efficiency Analysis — a data analytics and machine learning project focused on optimising factory-to-customer logistics performance.

---

## Slide 2 — Offer Letter *(~20 seconds)*

Before I begin, here is a quick look at my offer letter from Unified Mentor. I was onboarded on the 25th of March 2026 for a three-month internship in the Machine Learning domain. My intern ID is UMID22303268609 and my onboarding was handled by the HR Manager, Ms. Drishti Madaan. The internship runs until the 25th of June 2026.

---

## Slide 3 — Table of Contents *(~15 seconds)*

Here is a quick overview of what I will cover today. I will walk you through the internship overview, introduce the problem domain, define the exact problem we are solving, explain our methodology, walk through the experimentation pipeline, and finally share the results and key findings.

---

## Slide 4 — Internship Overview *(~40 seconds)*

I am interning at Unified Mentor Pvt. Ltd., an EdTech company based in Gurugram that connects students with live industry projects. My role is Machine Learning Intern.

The project I am working on involves building a shipping route efficiency analytics platform for a distribution sector client of Unified Mentor. The technology stack includes Python, Pandas, NumPy, pandera for data validation, Streamlit for the interactive dashboard, and Plotly for visualisations. The entire project follows a modular, layered software architecture with clear separation between data, analytics, and presentation layers.

---

## Slide 5 — Introduction *(~40 seconds)*

The project sits at the intersection of data engineering, analytics, and interactive visualisation. The client operates a factory-to-customer shipping network across multiple US states and Canada, with orders dispatched from five factories using four ship modes — Standard Class, First Class, Second Class, and Same Day.

The core challenge is that raw lead times in the dataset span 900 to over 1,600 days — a cohort artifact — which makes direct comparison across orders meaningless. Our work centres on normalising these values intelligently to extract a true performance signal and surface actionable insights through a dashboard.

---

## Slide 6 — Problem Definition *(~45 seconds)*

The problem was clear: the client had no visibility into which factory-region-ship mode combinations were performing efficiently versus which were consistently delayed. Orders were logged, but there was no scoring system, no geographic breakdown, and no way to compare routes side by side.

Our solution was to design and build a multi-tab interactive dashboard that computes route efficiency scores on a zero-to-hundred scale, identifies delay hotspots, and lets operations teams drill into individual routes by state, ship mode, and time period. The deliverables include a fully functional Streamlit application, a validated data pipeline, seven key performance indicators, and a geographic choropleth map of lead time performance across US states.

---

## Slide 7 — Methodology *(~60 seconds)*

The system is built across five distinct layers: configuration management, data ingestion and validation, analytics and scoring, visualisation, and the Streamlit presentation layer.

The most technically significant piece is the cohort-based lead time normalisation. Since raw lead times cluster into three groups — roughly 900, 1,270, and 1,630 days — we assign each order a cluster floor using a vectorised NumPy select operation. Subtracting this floor from the raw lead time gives us the relative lead time, which ranges from zero to eleven days. This is the true efficiency signal.

Route efficiency scores are then calculated by grouping orders by factory, region, and ship mode, computing the mean relative lead time per group, and applying an inverted min-max normalisation. A score of 100 means the fastest route; a score near zero means the slowest. This scoring is recomputed only when dashboard filters change, using a session state caching strategy keyed on a filter hash tuple.

---

## Slide 8 — Experimentation *(~45 seconds)*

The data pipeline processes a dataset of approximately 10,200 shipping orders with 18 attributes, covering order date, ship date, factory, region, state, ship mode, revenue, and profit, among others.

The pipeline runs in seven sequential steps: load the CSV, validate the schema using pandera, enrich the data by computing lead times and factory assignments, apply user-selected filters from the dashboard, compute the seven KPIs, score all routes, and generate the Plotly charts. Each step is independently unit-tested — the project has 28 passing tests covering data integrity, KPI correctness, and chart outputs.

---

## Slide 9 — Results *(~45 seconds)*

The dashboard surfaces several strong findings. Pacific region routes consistently score highest, with efficiency scores above 90 out of 100. Gulf region routes using Standard Class show the highest delay variability. Across all 36 factory-region-ship mode combinations, scores range from roughly 71 to 96.

The dashboard delivers four tabs: a route efficiency leaderboard, a geographic lead time map, a ship mode comparison with box plots and heatmaps, and a route drill-down with a Gantt-style order timeline. The client now has a fully operational analytics tool that replaces manual spreadsheet analysis with real-time, filter-driven insights.

To summarise — this internship has given me hands-on experience with building production-grade data pipelines, designing analytics systems, and delivering client-facing interactive dashboards. Thank you.

---

*End of script — estimated delivery time: 4 minutes 45 seconds to 5 minutes.*
