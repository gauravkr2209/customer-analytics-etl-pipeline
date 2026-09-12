"""
01_data_validation.py
----------------------
Validates the cleaned customer dataset before it enters the analytics pipeline.
Produces a validation report and flags any records that fail business rules.
"""

import pandas as pd

SRC = "/mnt/user-data/uploads/cleaned_customer_data.csv"

df = pd.read_csv(SRC)

report = []


def check(name, condition_count, total=len(df)):
    pct = round(100 * condition_count / total, 2)
    report.append((name, condition_count, f"{pct}%"))


# --- Structural checks ---
check("Duplicate customer_id", df["customer_id"].duplicated().sum())
check("Duplicate email", df["email"].duplicated().sum())
check("Null values (any column)", df.isnull().sum().sum())

# --- Business rule checks ---
check("Negative total_spend", (df["total_spend"] < 0).sum())
check("Negative total_orders", (df["total_orders"] < 0).sum())
check("Age outside 13-100", (~df["age"].between(13, 100)).sum())
check("total_orders = 0 but total_spend > 0 (inconsistent)",
      ((df["total_orders"] == 0) & (df["total_spend"] > 0)).sum())
check("last_purchase_date before signup_date",
      (pd.to_datetime(df["last_purchase_date"]) < pd.to_datetime(df["signup_date"])).sum())
check("'Unknown' gender", (df["gender"] == "Unknown").sum())
check("'Unknown' city", (df["city"] == "Unknown").sum())
check("'Unknown' preferred_channel", (df["preferred_channel"] == "Unknown").sum())

# --- AOV consistency check (total_spend / total_orders vs stored average_order_value) ---
calc_aov = df["total_spend"] / df["total_orders"].replace(0, pd.NA)
mismatch = ((calc_aov - df["average_order_value"]).abs() > 1).sum()
check("average_order_value mismatch (> 1.0 diff vs calculated)", mismatch)

report_df = pd.DataFrame(report, columns=["Check", "Records Flagged", "% of Dataset"])
print(report_df.to_string(index=False))
report_df.to_csv("/home/claude/project/outputs/validation_report.csv", index=False)

print(f"\nTotal records: {len(df)}")
print("Validation report saved to outputs/validation_report.csv")
