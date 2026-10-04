"""src/data.py — reusable data loading for the H.S DIESEL consumption model."""

import pandas as pd


def get_monthly_series(df, item_names, uom, dedupe=False):
    """
    Filter to the given item(s) and UOM, optionally drop exact-duplicate rows,
    aggregate to monthly totals, and reindex to a complete monthly range
    (Jun 2021 – Dec 2025) filling missing months with 0.

    Returns
    -------
    monthly : pd.DataFrame
        Columns: Month_Start (MS freq), Consumption_Qty
    neg_zero : pd.DataFrame
        Rows from the raw slice with Consumption_Qty <= 0 (for inspection).
    """
    if isinstance(item_names, str):
        item_names = [item_names]

    mask = df["Item_Name"].isin(item_names) & (df["UOM"] == uom)
    sub = df[mask].copy()

    if dedupe:
        sub = sub.drop_duplicates()

    # Drop partial May 2021 (data begins 28 May)
    sub = sub[sub["Issue_Date"] >= "2021-06-01"]

    neg_zero = sub[sub["Consumption_Qty"] <= 0]

    sub["Month_Start"] = sub["Issue_Date"].dt.to_period("M").dt.to_timestamp()
    monthly = (
        sub.groupby("Month_Start")["Consumption_Qty"]
        .sum()
        .reset_index()
    )

    # Reindex to complete Jun 2021 – Dec 2025 range
    all_months = pd.date_range(start="2021-06-01", end="2025-12-01", freq="MS")
    monthly = (
        monthly.set_index("Month_Start")
        .reindex(all_months)
        .fillna(0)
        .reset_index()
        .rename(columns={"index": "Month_Start"})
    )

    return monthly, neg_zero
