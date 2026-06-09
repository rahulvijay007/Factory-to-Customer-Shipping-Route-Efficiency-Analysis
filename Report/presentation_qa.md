# Possible Questions & Answers — Internship Review 1
**Project:** Shipping Route Efficiency Analysis | **Presenter:** Rahul Vijay

---

## Section 1 — About the Internship & Company

**Q1. What does Unified Mentor do and why did you choose them?**

Unified Mentor is an EdTech company based in Gurugram that offers live project-based internships to students. Instead of giving practice datasets with toy problems, they assign interns to real client projects with actual business goals. I chose them because I wanted hands-on exposure to a full data analytics workflow — from raw data to a deployed dashboard — rather than a purely academic exercise.

---

**Q2. What is your exact role and what were you expected to deliver?**

My role is Machine Learning Intern. I was expected to build an end-to-end shipping route analytics platform for a distribution sector client. The deliverable was a fully functional, interactive Streamlit dashboard that computes route efficiency scores, visualises geographic performance, compares ship modes, and allows operations teams to drill into individual routes — all driven by a clean, validated data pipeline.

---

**Q3. How long is the internship and how is your work supervised?**

The internship runs for three months, from 25th March to 25th June 2026. Work is supervised through Unified Mentor's mentorship model — technical mentors review code, provide guidance on architecture decisions, and conduct periodic reviews like this one. The HR point of contact for onboarding and logistics is Ms. Drishti Madaan.

---

## Section 2 — About the Problem

**Q4. What exactly is the business problem you are solving?**

The client operates a factory-to-customer shipping network across the United States and Canada. They had no systematic way to evaluate which routes — defined as a combination of factory, destination region, and ship mode — were performing efficiently versus which were consistently slow. Orders were logged but there was no scoring mechanism, no geographic breakdown, and no drill-down capability. The goal was to give the operations team a tool that surfaces this information in real time.

---

**Q5. Why is route efficiency important for a distribution business?**

In distribution, lead time directly affects customer satisfaction, inventory planning, and cost. A route that is consistently slow ties up working capital, increases the risk of stockouts at destination, and drives up expediting costs. By scoring routes and identifying the worst performers, the client can renegotiate carrier contracts, reassign factory sourcing for certain regions, or shift customers to a faster ship mode — all of which reduce cost and improve service levels.

---

**Q6. Why did you not just use the raw lead time to measure efficiency?**

The raw lead times in the dataset range from 904 to 1,642 days. At first glance, this looks like corrupt data — no real shipment takes four years. But after analysis, it turned out to be a cohort artifact: orders from different year-bands inherit systematically different baseline delays, most likely due to how historical data was migrated or timestamped. If you compare a 950-day order against a 1,300-day order directly, you are comparing apples and oranges. We had to remove this baseline offset first to get a meaningful comparison.

---

## Section 3 — About the Data

**Q7. What does the dataset look like?**

The dataset contains approximately 10,200 shipping orders with 18 attributes each. Key columns include order date, ship date, factory name, customer region, customer state, ship mode, product category, quantity, revenue, and profit. The date format is DD-MM-YYYY and lead time is calculated as the difference between ship date and order date in days.

---

**Q8. How did you validate the data before using it?**

We used the pandera library to define a schema that enforces column types, allowed categorical values, and value ranges. For example, the schema checks that ship mode is always one of the four allowed values — Standard Class, First Class, Second Class, Same Day — and that lead times fall within the expected range. Any row that fails validation is flagged before the data reaches the analytics layer. This prevents silent errors from propagating into KPI calculations.

---

**Q9. What are the three cohorts you mentioned and how did you identify them?**

When you plot the distribution of raw lead times, three distinct clusters appear — one centred around 904 days, one around 1,269 days, and one around 1,634 days. These correspond to orders from different year combinations of order year and ship year. We identified the floor of each cluster empirically and set boundaries at 1,100 and 1,500 days to separate them. Any order below 1,100 days belongs to the first cohort, between 1,100 and 1,500 to the second, and above 1,500 to the third.

---

**Q10. What is relative lead time and how is it computed?**

Relative lead time is the lead time after removing the cohort baseline. The formula is simple:

`relative_lead_time = lead_time_days − cluster_floor`

Each order's cluster floor is assigned using a vectorised NumPy select operation that looks up the correct floor based on which cohort the order belongs to. The result is a value between 0 and 11 days, which is the true efficiency signal — it measures how long the shipment took relative to the fastest shipment in the same cohort.

---

## Section 4 — About the Methodology & Architecture

**Q11. Can you explain the five-layer architecture of your system?**

The system is divided into five layers, each with a single responsibility. The configuration layer externalises all hardcoded values — cluster floors, colour schemes, chart sizes — into a YAML file loaded once at startup. The data layer handles CSV ingestion, schema validation, and feature engineering. The analytics layer computes KPIs, route efficiency scores, and geographic aggregations. The visualisation layer contains pure Plotly chart factory functions with no Streamlit dependencies. Finally, the presentation layer is the Streamlit app itself — a thin orchestrator that wires everything together and handles user interactions.

---

**Q12. What is session state caching and why does it matter?**

Streamlit reruns the entire Python script every time the user interacts with the UI. Without caching, all expensive computations — filtering 10,000 rows, scoring 36 routes, aggregating state metrics — would repeat on every button click or slider move. To prevent this, we store computed results in Streamlit's session state, keyed by a five-element tuple that captures the current filter settings — date range, regions, ship modes, and the delay threshold. If the filters have not changed between reruns, the cached results are used directly. Only when the filter hash changes do we recompute. This makes the dashboard feel instantaneous for the user.

---

**Q13. How exactly does the efficiency score go from 0 to 100?**

After computing the mean relative lead time for each factory-region-ship mode combination, we apply an inverted min-max normalisation. The formula is:

`score = (max − value) / (max − min) × 100`

We invert it because a lower lead time means higher efficiency. A route with the lowest mean relative lead time gets a score of 100, and the slowest route gets a score near zero. All other routes are scaled proportionally in between. This produces an intuitive, comparable score across all 36 route combinations.

---

**Q14. Why did you choose Streamlit over other dashboard frameworks like Dash or Tableau?**

Streamlit is Python-native, which means the same language used for data engineering and analytics is used for the dashboard — no context switching, no separate front-end code. It is also significantly faster to build with for data applications because layout, widgets, and charts are declared in a single script. For a three-month internship project where the priority was depth of analytics over UI polish, Streamlit was the right trade-off. Dash would have required more boilerplate and Tableau would have limited our ability to implement the custom cohort normalisation logic.

---

**Q15. Why Plotly specifically for charts?**

Plotly produces interactive charts natively — hover tooltips, zoom, pan, and selection are built in without extra code. For a logistics dashboard where the user needs to inspect individual data points — for example, hovering over a state on the choropleth to see its exact average lead time — static charts would have been a significant usability downgrade. Plotly also integrates directly with Streamlit via `st.plotly_chart()`, which keeps the code clean.

---

## Section 5 — About Testing & Code Quality

**Q16. You mentioned 28 unit tests. What do they test?**

The tests are organised across the data, analytics, and visualisation modules. They cover schema validation — checking that invalid data is correctly rejected, type casting, date parsing, and feature engineering outputs like relative lead time values and cluster floor assignments. Analytics tests verify KPI calculations against known inputs, route efficiency score bounds (always between 0 and 100), and filter logic. Chart tests confirm that chart factory functions return valid Plotly figure objects without crashing. All 28 tests must pass before any change is considered complete.

---

**Q17. How did you handle the factory name typo in the dataset?**

One of the five factory names in the dataset is `"Wonka Bar -Scrumdiddlyumptious"` — missing a space after the dash. The canonical name should be `"Wonka Bar - Scrumdiddlyumptious"`. Rather than correcting the data (which could introduce inconsistency if new data arrives with the same typo), we mapped both the typo and the correct spelling to the same factory in the configuration file. The factory coordinates and labels in the dashboard always display the canonical name, but the data layer accepts both.

---

## Section 6 — About the Results

**Q18. Which routes performed best and which performed worst?**

Pacific region routes consistently scored highest across all ship modes, with efficiency scores above 90 out of 100. This suggests that factories serving the Pacific coast have reliable, short lead times relative to their cohort baseline. Gulf region routes using Standard Class showed the highest variability and the lowest scores in some combinations — indicating that this is the most problematic route in the network. The full leaderboard of all 36 factory-region-ship mode combinations is visible on the dashboard's first tab.

---

**Q19. What does a score of, say, 75 actually mean in practice?**

A score of 75 means that route is performing at the 75th percentile of efficiency relative to the worst route in the network. More practically, if the worst route has a mean relative lead time of 9 days and the best has 1 day, a score of 75 corresponds to a mean relative lead time of about 3 days above the fastest route. It is a normalised, relative measure — it tells you where a route stands in the current dataset, not an absolute delivery target.

---

**Q20. How many routes does the dashboard analyse?**

There are 36 distinct factory-region-ship mode combinations in the dataset — 5 factories, 4 regions, and 4 ship modes would theoretically give 80 combinations, but not all factories serve all regions, so the actual combinations present in the data come to 36.

---

## Section 7 — About Professional Growth

**Q21. What is the most technically challenging part of this project?**

The cohort normalisation was the hardest part to get right. The challenge was not the formula itself — that is straightforward once you know the cluster floors — but identifying that the raw lead times were cohort-based artifacts in the first place. It required exploratory data analysis, histogram analysis of the distribution, and validation that the resulting relative lead times were actually meaningful as an efficiency signal. Getting this wrong would have meant the entire efficiency scoring system was built on a flawed premise.

---

**Q22. What would you do differently if you had more time?**

Three things. First, I would add a forecasting module — using the historical efficiency scores to predict future route performance and flag routes likely to degrade. Second, I would integrate a proper database backend instead of reading from a flat CSV on every session, which would allow the dashboard to scale to larger datasets without performance issues. Third, I would add user authentication so different operations managers could save their own filter presets and see personalised views.

---

**Q23. What has this internship taught you that you could not learn in a classroom?**

Client-oriented thinking. In a classroom, the problem is always well-defined and the solution is graded on correctness. In this project, the problem definition itself evolved — the initial brief was vague, and I had to ask clarifying questions, make assumptions explicitly, document them, and design a solution that would still be useful even if some assumptions turned out to be wrong. Writing code that someone else will use, and potentially maintain, is a fundamentally different experience from writing code to pass an assignment.

---

*End of Q&A document — 23 questions across 7 sections.*
