"""
02_feature_engineering.py
--------------------------
Adds derived features to the cleaned customer dataset for EDA, SQL analysis,
and the Power BI dashboard. Saves the enriched dataset to /data.
"""

import pandas as pd
import numpy as np

SRC = "/mnt/user-data/uploads/cleaned_customer_data.csv"
df = pd.read_csv(SRC, parse_dates=["signup_date", "last_purchase_date"])

# --- Age bands ---
df["age_group"] = pd.cut(
    df["age"], bins=[0, 25, 35, 45, 55, 100],
    labels=["18-25", "26-35", "36-45", "46-55", "56+"]
)

# --- Tenure bands (how long they've been a customer) ---
df["tenure_years"] = (df["customer_tenure_days"] / 365).round(1)
df["tenure_band"] = pd.cut(
    df["customer_tenure_days"], bins=[0, 365, 730, 1095, 5000],
    labels=["<1 yr", "1-2 yrs", "2-3 yrs", "3+ yrs"]
)

# --- Recency band (engagement freshness) ---
df["recency_band"] = pd.cut(
    df["days_since_last_purchase"], bins=[-1, 30, 90, 180, 365, 5000],
    labels=["0-30d", "31-90d", "91-180d", "181-365d", "365d+"]
)

# --- Revenue per day of tenure (spend efficiency) ---
df["spend_per_tenure_day"] = (df["total_spend"] / df["customer_tenure_days"]).round(2)

# --- Order frequency (orders per year of tenure) ---
df["orders_per_year"] = (df["total_orders"] / (df["customer_tenure_days"] / 365)).round(2)

# --- High-value at-risk flag: top spend tier that has gone quiet ---
spend_p75 = df["total_spend"].quantile(0.75)
df["high_value_at_risk"] = (
    (df["total_spend"] >= spend_p75) & (df["customer_activity"] == "At Risk")
)

# --- Simple RFM-style score (Recency, Frequency, Monetary), 1-5 scale each ---
df["r_score"] = pd.qcut(df["days_since_last_purchase"].rank(method="first"), 5, labels=[5, 4, 3, 2, 1]).astype(int)
df["f_score"] = pd.qcut(df["total_orders"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
df["m_score"] = pd.qcut(df["total_spend"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
df["rfm_score"] = df["r_score"] + df["f_score"] + df["m_score"]

# --- Clean 'Unknown' categorical placeholders into an explicit category (kept, not dropped) ---
for col in ["gender", "city", "preferred_channel"]:
    df[col] = df[col].replace("Unknown", "Not Provided")

# --- Flag the one data-quality inconsistency found in validation (kept for transparency) ---
df["data_flag_zero_orders_with_spend"] = (df["total_orders"] == 0) & (df["total_spend"] > 0)

OUT = "/home/claude/project/data/customer_data_enriched.csv"
df.to_csv(OUT, index=False)
print(f"Saved enriched dataset: {OUT}")
print(f"Rows: {len(df)}, Columns: {df.shape[1]}")
print("\nNew columns added:")
new_cols = ["age_group", "tenure_years", "tenure_band", "recency_band",
            "spend_per_tenure_day", "orders_per_year", "high_value_at_risk",
            "r_score", "f_score", "m_score", "rfm_score", "data_flag_zero_orders_with_spend"]
print(new_cols)
