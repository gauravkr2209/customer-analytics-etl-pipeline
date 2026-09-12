-- ==========================================================================
-- Customer Analytics & ETL Pipeline — SQL Analysis
-- Table: customers  (994 rows, enriched with feature-engineered columns)
-- Dialect: ANSI SQL / SQLite (also portable to Postgres, MySQL, Snowflake
-- with minor date-function adjustments)
-- ==========================================================================

-- 1. How many customers does the business have?
SELECT COUNT(*) AS total_customers
FROM customers;


-- 2. How much total revenue/spend is generated? (plus AOV and order volume)
SELECT
    COUNT(*)                       AS total_customers,
    SUM(total_orders)              AS total_orders,
    ROUND(SUM(total_spend), 2)     AS total_revenue,
    ROUND(AVG(total_spend), 2)     AS avg_revenue_per_customer,
    ROUND(AVG(average_order_value), 2) AS avg_order_value
FROM customers;


-- 3. Which customer segments are most valuable?
SELECT
    customer_segment,
    COUNT(*)                              AS customers,
    ROUND(SUM(total_spend), 2)            AS total_revenue,
    ROUND(AVG(total_spend), 2)            AS avg_spend_per_customer,
    ROUND(100.0 * SUM(total_spend) /
        (SELECT SUM(total_spend) FROM customers), 1) AS pct_of_total_revenue
FROM customers
GROUP BY customer_segment
ORDER BY total_revenue DESC;


-- 4. Which acquisition channels perform best?
SELECT
    acquisition_channel,
    COUNT(*)                           AS customers_acquired,
    ROUND(SUM(total_spend), 2)         AS total_revenue,
    ROUND(AVG(total_spend), 2)         AS avg_spend_per_customer,
    ROUND(AVG(total_orders), 2)        AS avg_orders_per_customer
FROM customers
GROUP BY acquisition_channel
ORDER BY avg_spend_per_customer DESC;


-- 5. Which cities generate the most customer spend?
SELECT
    city,
    state,
    COUNT(*)                      AS customers,
    ROUND(SUM(total_spend), 2)    AS total_revenue,
    ROUND(AVG(total_spend), 2)    AS avg_spend_per_customer
FROM customers
GROUP BY city, state
ORDER BY total_revenue DESC
LIMIT 10;


-- 6. How many customers are Active, At Risk, and Inactive?
SELECT
    customer_activity,
    COUNT(*) AS customers,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM customers), 1) AS pct_of_base,
    ROUND(SUM(total_spend), 2) AS revenue_in_segment
FROM customers
GROUP BY customer_activity
ORDER BY customers DESC;


-- 7. Which high-value customers are at risk? (top-quartile spend + At Risk activity)
SELECT
    customer_id,
    customer_name,
    city,
    customer_segment,
    total_spend,
    total_orders,
    days_since_last_purchase,
    rfm_score
FROM customers
WHERE high_value_at_risk = 1        -- pre-computed flag from feature engineering
ORDER BY total_spend DESC;

-- Equivalent, computed inline without the pre-built flag:
-- WHERE customer_activity = 'At Risk'
--   AND total_spend >= (SELECT AVG(total_spend) + 0.5 * (SELECT (
--        SELECT SQRT(AVG((total_spend - avg_spend) * (total_spend - avg_spend)))
--        FROM customers, (SELECT AVG(total_spend) AS avg_spend FROM customers)
--   )) FROM customers)  -- (use percentile logic per your SQL dialect instead)


-- 8. What factors are associated with higher customer spending?
-- 8a. Spend by segment x activity status
SELECT
    customer_segment,
    customer_activity,
    COUNT(*)                    AS customers,
    ROUND(AVG(total_spend), 2)  AS avg_spend
FROM customers
GROUP BY customer_segment, customer_activity
ORDER BY customer_segment, avg_spend DESC;

-- 8b. Spend by tenure band (does loyalty/longevity correlate with spend?)
SELECT
    tenure_band,
    COUNT(*)                    AS customers,
    ROUND(AVG(total_spend), 2)  AS avg_spend,
    ROUND(AVG(total_orders), 2) AS avg_orders
FROM customers
GROUP BY tenure_band
ORDER BY avg_spend DESC;

-- 8c. Spend by preferred shopping channel
SELECT
    preferred_channel,
    COUNT(*)                    AS customers,
    ROUND(AVG(total_spend), 2)  AS avg_spend
FROM customers
GROUP BY preferred_channel
ORDER BY avg_spend DESC;

-- 8d. Spend by age group
SELECT
    age_group,
    COUNT(*)                    AS customers,
    ROUND(AVG(total_spend), 2)  AS avg_spend
FROM customers
GROUP BY age_group
ORDER BY age_group;


-- 9. Where should the business focus retention and marketing efforts?
-- 9a. Retention priority list — highest revenue-at-risk customers
SELECT
    customer_id, customer_name, city, customer_segment,
    total_spend, days_since_last_purchase, acquisition_channel
FROM customers
WHERE customer_activity IN ('At Risk', 'Inactive')
ORDER BY total_spend DESC
LIMIT 20;

-- 9b. Best channel + city combinations to double down on for marketing spend
SELECT
    acquisition_channel,
    city,
    COUNT(*)                   AS customers,
    ROUND(SUM(total_spend), 2) AS total_revenue,
    ROUND(AVG(total_spend), 2) AS avg_spend
FROM customers
GROUP BY acquisition_channel, city
HAVING COUNT(*) >= 5
ORDER BY avg_spend DESC
LIMIT 10;

-- 9c. Revenue at risk overall (dollars sitting in At Risk + Inactive customers)
SELECT
    ROUND(SUM(CASE WHEN customer_activity IN ('At Risk','Inactive') THEN total_spend ELSE 0 END), 2) AS revenue_at_risk,
    ROUND(100.0 * SUM(CASE WHEN customer_activity IN ('At Risk','Inactive') THEN total_spend ELSE 0 END)
        / SUM(total_spend), 1) AS pct_of_total_revenue
FROM customers;
