# Power BI Dashboard — Build Guide

This project's `.pbix` file needs to be built in Power BI Desktop (Windows) since that
application isn't available in this environment. Use this guide to recreate the exact
dashboard in ~20 minutes. The HTML prototype at
`outputs/customer_analytics_dashboard.html` shows the target layout and can be opened in
any browser as a working reference / stand-in until the `.pbix` is built.

## 1. Get the data in
1. Open Power BI Desktop → **Get Data → Text/CSV**.
2. Load `data/customer_data_enriched.csv` (the feature-engineered dataset — 994 rows, 31 columns).
3. In Power Query Editor, confirm data types: `signup_date` / `last_purchase_date` → Date/Time,
   `total_spend` / `average_order_value` / `spend_per_tenure_day` → Decimal Number,
   everything else numeric → Whole Number. Click **Close & Apply**.

## 2. Create DAX measures
Add a new table of measures (Modeling → New Table → paste `Measures = {}` then add each
measure below), or add them directly to the `customer_data_enriched` table.

```DAX
Total Customers = DISTINCTCOUNT(customer_data_enriched[customer_id])

Total Revenue = SUM(customer_data_enriched[total_spend])

Total Orders = SUM(customer_data_enriched[total_orders])

Avg Order Value = AVERAGE(customer_data_enriched[average_order_value])

Avg Spend per Customer = DIVIDE([Total Revenue], [Total Customers])

Active Customers = CALCULATE([Total Customers], customer_data_enriched[customer_activity] = "Active")

At Risk Customers = CALCULATE([Total Customers], customer_data_enriched[customer_activity] = "At Risk")

Inactive Customers = CALCULATE([Total Customers], customer_data_enriched[customer_activity] = "Inactive")

Revenue At Risk = CALCULATE(
    [Total Revenue],
    customer_data_enriched[customer_activity] IN {"At Risk", "Inactive"}
)

Pct Revenue At Risk = DIVIDE([Revenue At Risk], [Total Revenue])

High Value At Risk Customers = CALCULATE(
    [Total Customers],
    customer_data_enriched[high_value_at_risk] = TRUE
)

Pct of Total Revenue by Segment =
DIVIDE([Total Revenue], CALCULATE([Total Revenue], ALL(customer_data_enriched[customer_segment])))
```

## 3. Page layout — "Overview"
- **KPI cards** (top row, Card visual): Total Customers, Total Revenue, Avg Order Value,
  Total Orders, At Risk Customers, Revenue At Risk (with `Pct Revenue At Risk` as a
  secondary label).
- **Slicers** (left rail or top bar): `customer_segment`, `customer_activity`,
  `acquisition_channel`, `city`, `age_group`. Sync slicers across all report pages
  (View → Sync Slicers).
- **Clustered column chart**: `customer_segment` (axis) vs `Total Revenue` (values) —
  "Revenue by Customer Segment".
- **Donut chart**: `customer_activity` (legend) vs `Total Customers` — "Customer Activity
  Status".

## 4. Page layout — "Acquisition & Geography"
- **Bar chart**: `acquisition_channel` (axis) vs `Avg Spend per Customer` — "Which channel
  brings the highest-value customers".
- **Bar chart**: `acquisition_channel` (axis) vs `Total Customers` — "Volume by channel".
- **Map or bar chart**: `city` (axis) vs `Total Revenue`, top 10 filtered via a Top N filter
  — "Top Cities by Revenue". Use the Map visual if you want to plot by `state` for a
  geographic view.

## 5. Page layout — "Retention & Risk"
- **Table visual**: filtered to `high_value_at_risk = TRUE`, columns: `customer_id`,
  `customer_name`, `city`, `customer_segment`, `total_spend`, `total_orders`,
  `days_since_last_purchase`, `rfm_score`. Sort descending by `total_spend`.
  This is the retention call-list.
- **Stacked bar**: `tenure_band` (axis) vs `Avg Spend` — does loyalty correlate with spend?
- **Scatter chart**: `days_since_last_purchase` (X) vs `total_spend` (Y), color by
  `customer_activity`, size by `total_orders` — visually clusters high-value customers who
  have gone quiet (top-left, dark-colored "At Risk" dots).

## 6. Formatting
- Use a consistent brand palette (e.g. the 6-color set in `eda/*.png` /
  `outputs/customer_analytics_dashboard.html`: `#4C72B0, #DD8452, #55A868, #C44E52,
  #8172B2, #937860`).
- Format `total_spend`/currency measures with the ₹ symbol (Format → Currency → INR) if
  presenting for an Indian retail audience, since the source cities/states are Indian.
- Add a title text box and a "last refreshed" date field on each page.

## 7. Export
- File → Export → **Export report as PDF** (for the screenshots that go in the GitHub
  README) and save the `.pbix` file itself in `powerbi/customer_analytics.pbix`.
