# Customer Analytics & ETL Pipeline

An end-to-end customer analytics project: data validation, feature engineering, EDA,
SQL analysis, and an interactive dashboard — built on a 994-record customer dataset.

**Live Dashboard:** [gauravkr2209.github.io/customer-analytics-etl-pipeline](https://gauravkr2209.github.io/customer-analytics-etl-pipeline/outputs/customer_analytics_dashboard.html)

**Stack:** Python (Pandas, NumPy, Matplotlib) · SQL (SQLite) · HTML/JS (Chart.js) · Power BI (build guide)

**Dataset Disclaimer:** Synthetic data created for portfolio purposes — does not represent a real business.

---

## Key Findings

| Metric | Value |
|---|---|
| Customers analyzed | 994 |
| Total revenue | ₹1,02,97,596.58 |
| Active / At Risk / Inactive | 16.0% / 13.4% / 70.6% |
| Revenue held by At Risk + Inactive customers | 84.5% (₹87,03,639.71) |
| High-value customers flagged At Risk | 37 |

The single biggest signal in this dataset: the large majority of revenue sits with
customers who are no longer actively purchasing, not with the currently active base.

## Business Problem

Analyze customer behavior to identify the most valuable segments, acquisition channels,
and cities; measure how much of the customer base is active vs. disengaged; flag
high-value customers showing early signs of churn; and turn those findings into concrete
retention and marketing recommendations.

## Dataset

`data/cleaned_customer_data.csv` — 994 rows, 19 columns. Already arrives clean: 0 missing
values, 0 duplicate IDs, 0 negative or logically invalid values (verified in
`scripts/01_data_validation.py` → `outputs/validation_report.csv`). No raw/uncleaned
version of the file exists in this project, so no duplicate-removal or imputation work
was needed — validation confirmed the data was sound rather than requiring correction.

**Source columns:** customer identity (`customer_id`, `customer_name`, `email`, `gender`,
`age`), location (`city`, `state`), lifecycle dates (`signup_date`,
`last_purchase_date`), behavior (`total_orders`, `total_spend`, `average_order_value`,
`customer_tenure_days`, `days_since_last_purchase`), and category labels
(`customer_segment`, `acquisition_channel`, `preferred_channel`, `customer_activity`,
`spend_category`).

The one true anomaly found: customer `CUST1855` has 0 recorded orders but ₹10,127.83 of
spend — kept and flagged (`data_flag_zero_orders_with_spend`) rather than deleted, since
removing real revenue without knowing the cause would understate the business.

## Feature Engineering

Script: `scripts/02_feature_engineering.py` → `data/customer_data_enriched.csv` (994
rows, 31 columns).

**Already in the source data (not engineered here):** `customer_activity`,
`spend_category`, `average_order_value`, `customer_tenure_days`,
`days_since_last_purchase`.

**Actually engineered in this project:**

| Feature | What it does |
|---|---|
| `r_score`, `f_score`, `m_score`, `rfm_score` | Quintile-based RFM (Recency, Frequency, Monetary) scoring per customer |
| `high_value_at_risk` | Flags customers in the top spend quartile with `customer_activity = 'At Risk'` |
| `tenure_band`, `age_group`, `recency_band` | Binned versions of tenure, age, and recency for grouping/filtering |
| `spend_per_tenure_day`, `orders_per_year` | Spend/orders normalized against customer lifetime |
| `data_flag_zero_orders_with_spend` | Carries the one data anomaly forward for transparency |

## Exploratory Data Analysis

Charts in `eda/*.png`: revenue by segment, activity status split, average spend by
acquisition channel, top 10 cities by revenue, spend distribution, and average spend by
tenure band.

## SQL Analysis

`sql/analysis_queries.sql` — 14 queries across 9 business questions, run against
`data/customer_analytics.db` (SQLite).

- **Segments:** Regular customers drive 63.6% of revenue on volume (641 customers); VIP
  customers have the highest average spend per head (₹10,720.90) despite being only 7.2%
  of the base.
- **Acquisition channels:** Paid Ads (₹10,814.77 avg) and Direct (₹10,802.45 avg)
  customers spend more per head than Social Media (₹10,029.57 avg), even though Social
  Media brings in the most customers (198).
- **Cities:** Noida (₹9,57,054), Delhi (₹9,40,759), and Lucknow (₹8,55,220) lead on total
  revenue.
- **Spend drivers:** Average order value correlates moderately with total spend (r =
  0.62); order count and tenure barely correlate (r ≈ 0.00–0.04). This is a
  correlational pattern, not a causal one — it doesn't prove raising AOV increases
  spend, only that the two move together in this dataset.

## High-Value At-Risk Analysis

- **High-value** = top quartile of `total_spend`.
- **At Risk** = `customer_activity = 'At Risk'` (91–179 days since last purchase, per
  the source data's own labeling).
- **37 customers** meet both — the clearest retention priority list in the project (full
  list in `sql/analysis_queries.sql`, Q7, and live in the dashboard's at-risk table).

## Interactive Dashboard

`outputs/customer_analytics_dashboard.html` — a self-contained HTML/JavaScript (Chart.js)
dashboard, live at the link above. Includes KPI cards, Segment/Activity/Channel/City
filters, six charts, and a live high-value-at-risk table that updates with the filters.

**Power BI:** no `.pbix` file is included. `powerbi/POWER_BI_BUILD_GUIDE.md` documents
DAX measures and a page layout for building a native Power BI version separately — it's
a guide, not the delivered dashboard.

## Business Recommendations

1. Prioritize the 37 high-value At Risk customers for retention outreach before they
   lapse into Inactive.
2. Run a separate, lower-cost reactivation campaign for the 702 Inactive customers.
3. Evaluate shifting acquisition spend toward Paid Ads/Direct, which bring higher average
   spend per customer than Social Media.
4. Test basket-size promotions given the AOV correlation — validate with an actual
   experiment rather than assuming causation.
5. Build a dedicated retention track for VIP customers, given their outsized average
   spend relative to their small share of the base.

## Limitations

- Dataset is synthetic; findings don't reflect a real business.
- No transaction-level data — analysis is at the customer-aggregate level.
- Correlational findings don't establish causation.
- `customer_activity`/`spend_category` thresholds come from the source data, not derived
  independently.

## Future Improvements

- Transaction-level and cohort-based retention analysis
- Customer lifetime value (CLV) modeling
- Churn prediction using real labeled outcomes
- A/B testing the proposed retention campaigns
- A native Power BI `.pbix`, built from the included guide

## Repository Structure

```
├── data/            # source + enriched CSVs, SQLite DB
├── scripts/         # validation, feature engineering, dashboard build
├── sql/             # analysis_queries.sql
├── eda/             # chart PNGs
├── outputs/         # validation report, interactive dashboard
└── powerbi/         # DAX/build guide
```

## Resume Summary

**Customer Analytics & ETL Pipeline** — Python | Pandas | SQL | Power BI
- Validated a 994-record dataset and engineered RFM scores and a high-value-at-risk flag,
  identifying 37 customers holding disproportionate revenue risk.
- Wrote 14 SQL queries answering 9 business questions, finding 84.5% of total revenue
  concentrated in At Risk/Inactive customers.
- Built an interactive analytics dashboard and a companion Power BI build guide;
  published both via GitHub Pages.
