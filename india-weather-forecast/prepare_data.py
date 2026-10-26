"""Convert the daily dataset from Notebook 1 into a small monthly file for the app.

Usage:
    python prepare_data.py                              # reads india_weather_daily.csv
    python prepare_data.py path/to/india_weather_daily.csv
"""
import sys
from pathlib import Path

import pandas as pd

src = Path(sys.argv[1] if len(sys.argv) > 1 else "india_weather_daily.csv")
dst = Path("data/monthly_temperature.csv")

if not src.exists():
    sys.exit(f"File not found: {src}\nRun Notebook 1 first, then pass the path to india_weather_daily.csv")

daily = pd.read_csv(src, parse_dates=["date"])

monthly = (
    daily.set_index("date")
    .groupby("city")
    .resample("MS")
    .agg(
        temp_mean=("temp_mean", "mean"),
        temp_max=("temp_max", "mean"),
        temp_min=("temp_min", "mean"),
        rainfall_mm=("rainfall_mm", "sum"),
        days=("temp_mean", "count"),
    )
    .reset_index()
)

# Keep complete months only (the latest month is usually partial)
monthly = monthly[monthly["days"] >= monthly["date"].dt.days_in_month].drop(columns="days")

dst.parent.mkdir(exist_ok=True)
num_cols = ["temp_mean", "temp_max", "temp_min", "rainfall_mm"]
monthly[num_cols] = monthly[num_cols].round(3)
monthly.to_csv(dst, index=False)
print(f"Saved {dst}  ({len(monthly):,} rows, {monthly['city'].nunique()} cities, "
      f"{monthly['date'].min():%b %Y} to {monthly['date'].max():%b %Y})")
