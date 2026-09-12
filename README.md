# Customer Analytics & ETL Pipeline

An end-to-end customer analytics project demonstrating Python, Pandas, SQL, data
validation, EDA, feature engineering, and BI dashboarding — built on a dataset of 994
customer records across 15 Indian cities.

**Pipeline:** Raw Data → Data Profiling → Data Cleaning → Data Validation → Feature
Engineering → EDA → SQL Analysis → Power BI Dashboard → Business Insights

---

## 1. Problem Statement

The business wants to understand its customer base well enough to answer nine concrete
questions: how big is it, how much does it spend, which segments/channels/cities matter
most, how many customers are active vs. lapsing, which high-value customers are at risk of
churn, what drives spend, and where retention/marketing effort should go. This project
builds the full pipeline — from raw CSV to a browsable BI dashboard — to answer them with
evidence rather than guesswork.

## 2. Dataset

`data/cleaned_customer_data.csv` — 994 rows, 19 columns: customer identity (`customer_id`,
`name`, `email`, `gender`, `age`), location (`city`, `state`), lifecycle dates
(`signup_date`, `last_purchase_date`), behavioral fields (`total_orders`, `total_spend`,
`average_order_value`, `customer_tenure_days`, `days_since_last_purchase`), and
categorical labels (`customer_segment`, `acquisition_channel`, `preferred_channel`,
`customer_activity`, `spend_category`).

## 3. Data Profiling & Validation

Script: `scripts/01_data_validation.py` → `outputs/validation_report.csv`

| Check | Records Flagged | % of Dataset |
|---|---|---|
| Duplicate `customer_id` | 0 | 0.0% |
| Duplicate `email` | 0 | 0.0% |
| Null values (any column) | 0 | 0.0% |
| Negative `total_spend` | 0 | 0.0% |
| Age outside 13–100 | 0 | 0.0% |
| `total_orders` = 0 but `total_spend` > 0 | 1 | 0.1% |
| `last_purchase_date` before `signup_date` | 0 | 0.0% |
| `'Unknown'` gender | 8 | 0.8% |
| `'Unknown'` city | 10 | 1.0% |
| `'Unknown'` preferred_channel | 7 | 0.7% |
| `average_order_value` inconsistent with spend/orders | 0 | 0.0% |

**Takeaway:** the dataset is largely clean and internally consistent (already
pre-cleaned). The only real anomaly is one customer (`CUST1855`) with 0 recorded orders
but ₹10,127.83 of spend — flagged rather than dropped, since deleting real revenue
without knowing the cause would understate the business. `'Unknown'` values in
gender/city/preferred_channel (~1% each) were relabeled `'Not Provided'` during feature
engineering rather than imputed, to avoid inventing data.

## 4. Feature Engineering

Script: `scripts/02_feature_engineering.py` → `data/customer_data_enriched.csv` (994 rows,
31 columns)

New fields added:
- `age_group`, `tenure_band`, `recency_band` — binned versions of age, tenure, and days
  since last purchase for easier slicing.
- `tenure_years`, `spend_per_tenure_day`, `orders_per_year` — normalized behavioral rates.
- `r_score`, `f_score`, `m_score`, `rfm_score` — a quintile-based RFM (Recency, Frequency,
  Monetary) score per customer, 3–15 scale.
- `high_value_at_risk` — flag for customers in the top spend quartile whose
  `customer_activity = 'At Risk'`, used directly in the retention query and dashboard.
- `data_flag_zero_orders_with_spend` — carries the one validation anomaly forward for
  transparency instead of silently fixing or dropping it.

## 5. EDA Highlights

Charts: `eda/*.png`

- **Revenue by segment** (`01_revenue_by_segment.png`) — Regular customers generate the
  majority of revenue by volume, but VIP and Premium customers spend more per head.
- **Activity status split** (`02_activity_status.png`) — the base skews heavily inactive.
- **Channel avg spend** (`03_channel_avg_spend.png`) — Paid Ads and Direct customers spend
  the most per head, even though Social Media brings in the most customers overall.
- **Top cities** (`04_top_cities.png`) — Noida, Delhi, and Lucknow lead on total revenue.
- **Spend distribution** (`05_spend_distribution.png`) — right-skewed, as expected for
  revenue data; a small number of high spenders pull the average up.
- **Tenure vs. spend** (`06_tenure_vs_spend.png`) — spend rises through the 2–3 year
  tenure band before tapering for 3+ year customers.

## 6. SQL Analysis

All 14 business-question queries: `sql/analysis_queries.sql` (run against
`data/customer_analytics.db`, a SQLite load of the enriched dataset — portable to
Postgres/MySQL/Snowflake with minor date-function changes).

### Key results

**Q1–2: Size & revenue**
- **994 customers**, **7,000 total orders**, **₹1,02,97,596.58 total revenue**
- Average revenue per customer: ₹10,359.76 · Average order value: ₹1,796.65

**Q3: Most valuable segments**

| Segment | Customers | Total Revenue | Avg Spend/Customer | % of Revenue |
|---|---|---|---|---|
| Regular | 641 | ₹65,53,300.57 | ₹10,223.56 | 63.6% |
| Premium | 281 | ₹29,72,391.00 | ₹10,577.90 | 28.9% |
| VIP | 72 | ₹7,71,905.01 | ₹10,720.90 | 7.5% |

VIP customers spend the most per head, but there are so few of them that Regular
customers still drive most of the revenue by sheer volume.

**Q4: Best acquisition channels** (by avg spend per customer)

Paid Ads (₹10,814.77) > Direct (₹10,802.45) > Referral (₹10,435.36) > Organic Search
(₹10,144.66) > Social Media (₹10,029.57) > Email Campaign (₹10,022.81). Social Media
brings in the most customers (198) but the lowest average spend among the top volume
channels — a quantity vs. quality trade-off.

**Q5: Top cities by revenue** — Noida (₹9,57,054), Delhi (₹9,40,759), Lucknow
(₹8,55,220), Chennai (₹8,16,823), Bengaluru (₹7,66,753). Pune has the highest *average*
spend per customer (₹12,215) despite lower volume.

**Q6: Activity split** — **Inactive: 702 (70.6%)**, **Active: 159 (16.0%)**, **At Risk:
133 (13.4%)**. Only 1 in 6 customers is currently active.

**Q7: High-value customers at risk** — 37 customers are in the top spend quartile *and*
flagged "At Risk" (full list in `sql/analysis_queries.sql` Q7 / dashboard table). Top of
the list: Ankit Chauhan (₹32,804.17, Hyderabad), Aditi Chauhan (₹29,969.01, Ahmedabad,
VIP), Priya Nair (₹26,721.88, Noida).

**Q8: Factors associated with higher spend** — a correlation check against `total_spend`
found:
| Factor | Correlation with total_spend |
|---|---|
| Spend per tenure day (derived) | 0.68 |
| Average order value | 0.62 |
| Customer tenure (days) | 0.04 |
| Days since last purchase | 0.02 |
| Total orders | -0.01 |
| Age | -0.01 |

**Order count and tenure barely correlate with total spend — average order value is the
dominant driver.** This means the business grows revenue more by getting customers to
spend more per basket than by getting them to order more frequently or stay longer.
Segment-wise, VIP "At Risk" customers still average ₹11,814 in spend — higher than VIP
Active customers (₹10,660) — confirming valuable customers are churning, not just casual
ones.

**Q9: Where to focus retention & marketing**
- **84.5% of total revenue (₹87,03,639.71) sits with At Risk + Inactive customers.**
  This is the single biggest number in the analysis — the business's revenue base is
  overwhelmingly tied up in customers who are not currently engaged.
- Best channel × city combinations for marketing spend: Email Campaign in Pune (avg
  ₹13,652/customer), Paid Ads in Pune (₹13,521), Paid Ads in Hyderabad (₹13,460).
- The retention priority list (highest-spend At Risk/Inactive customers) is in
  `sql/analysis_queries.sql` Q9a and mirrored in the dashboard's "High-Value Customers At
  Risk" table.

## 7. Power BI Dashboard

Since this environment can't run Power BI Desktop, two things are provided:
1. **`outputs/customer_analytics_dashboard.html`** — a fully interactive, self-contained
   HTML dashboard (KPI cards, 6 charts, 4 slicers, and a sortable "high-value at risk"
   table) built on the same enriched dataset. Open it directly in any browser — no
   install needed. This mirrors the intended Power BI layout and can serve as the
   dashboard deliverable, or as a live reference while building the `.pbix`.
2. **`powerbi/POWER_BI_BUILD_GUIDE.md`** — step-by-step instructions plus ready-to-paste
   DAX measures to recreate the same dashboard natively in Power BI Desktop, across three
   report pages (Overview, Acquisition & Geography, Retention & Risk).

Dashboard features: KPI cards (customers, revenue, AOV, orders, at-risk count, revenue at
risk), Segment/Activity/Channel/City filters, revenue-by-segment and activity-status
charts, channel and city performance charts, tenure-vs-spend trend, and a live "high-value
at risk" retention table that updates with the filters.

## 8. Business Recommendations

1. **Revenue is concentrated in disengaged customers.** With 84.5% of revenue sitting in
   At Risk/Inactive accounts, a win-back campaign targeting the 133 "At Risk" customers —
   especially the 37 high-value ones — should be the top priority; they're closer to
   recoverable than the 702 already-Inactive customers.
2. **Grow basket size, not just order frequency.** Since AOV correlates far more strongly
   with total spend than order count or tenure does, promotions and upsell/bundle
   strategies aimed at raising average order value are likely to move revenue more than
   frequency-based loyalty programs.
3. **Double down on Paid Ads and Direct acquisition.** Both channels bring in
   higher-spending customers on average than Social Media or Email Campaign, even though
   Social Media brings in more volume — worth testing budget reallocation.
4. **Prioritize Pune, Noida, Delhi, and Hyderabad for combined marketing + retention
   spend** — they show the best channel × city combinations for average spend per
   customer.
5. **VIP is a small but disproportionately valuable segment (7.5% of customers, but the
   highest avg spend/customer) — and it has a meaningful At Risk cohort.** A dedicated VIP
   retention track (personal outreach, early access, loyalty perks) protects the most
   valuable relationships first.

## 9. Repository Structure

```
├── README.md                          # this file
├── data/
│   ├── cleaned_customer_data.csv      # source dataset (994 rows, 19 cols)
│   ├── customer_data_enriched.csv     # feature-engineered dataset (994 rows, 31 cols)
│   └── customer_analytics.db          # SQLite load used for SQL analysis
├── scripts/
│   ├── 01_data_validation.py
│   ├── 02_feature_engineering.py
│   └── build_dashboard.py
├── sql/
│   └── analysis_queries.sql           # all 9 business questions as SQL
├── eda/
│   └── *.png                          # 6 EDA charts
├── outputs/
│   ├── validation_report.csv
│   └── customer_analytics_dashboard.html   # interactive dashboard
└── powerbi/
    └── POWER_BI_BUILD_GUIDE.md        # DAX measures + layout guide for the .pbix
```

## 10. Tools Used
Python (Pandas, Matplotlib), SQL (SQLite, portable to Postgres/BigQuery/Snowflake),
Power BI (Desktop build guide + DAX), HTML/JS/Chart.js (interactive dashboard prototype).
