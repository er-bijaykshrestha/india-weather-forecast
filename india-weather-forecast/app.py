"""India Weather Forecast: Streamlit dashboard.

Reads:
  data/monthly_temperature.csv        
  reports/*.csv                       
"""
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from scipy import stats

st.set_page_config(page_title="India Weather Forecast", page_icon="🌦️", layout="wide")

BASE = Path(__file__).parent
DATA_FILE = BASE / "data" / "monthly_temperature.csv"
REPORTS = BASE / "reports"
REQUIRED = [
    DATA_FILE,
    REPORTS / "forecast_next_12_months.csv",
    REPORTS / "metrics_test_2026_overall.csv",
    REPORTS / "metrics_test_2026_by_city.csv",
    REPORTS / "metrics_backtest_by_city.csv",
    REPORTS / "best_model_per_city.csv",
]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
RED, GREY, BLUE = "#d62728", "#555555", "#1f77b4"

missing = [str(p.relative_to(BASE)) for p in REQUIRED if not p.exists()]
if missing:
    st.error("Some data files are missing:\n\n" + "\n".join(f"- `{m}`" for m in missing))
    st.info("Run `python prepare_data.py` and copy the CSVs from Notebook 3 into `reports/`. See the README.")
    st.stop()


@st.cache_data
def load_all():
    monthly = pd.read_csv(DATA_FILE, parse_dates=["date"])
    forecast = pd.read_csv(REPORTS / "forecast_next_12_months.csv", parse_dates=["date"])
    overall = pd.read_csv(REPORTS / "metrics_test_2026_overall.csv", index_col=0)
    test_city = pd.read_csv(REPORTS / "metrics_test_2026_by_city.csv")
    backtest = pd.read_csv(REPORTS / "metrics_backtest_by_city.csv")
    best = pd.read_csv(REPORTS / "best_model_per_city.csv", index_col=0)
    return monthly, forecast, overall, test_city, backtest, best


monthly, forecast, overall, test_city, backtest, best = load_all()
cities = sorted(monthly["city"].unique())


def full_year_annual(df):
    """Annual mean temperature using complete years only."""
    d = df.assign(year=df["date"].dt.year)
    counts = d.groupby(["city", "year"])["temp_mean"].transform("count")
    return d[counts == 12].groupby(["city", "year"])["temp_mean"].mean().unstack(0)


annual = full_year_annual(monthly)


def trend_stats(series):
    s = series.dropna()
    r = stats.linregress(s.index.values, s.values)
    return r.slope * 10, r.pvalue


# ------------------------------------------------------------------ sidebar
st.sidebar.title("India Weather Forecast")
city = st.sidebar.selectbox("City", cities, index=cities.index("Delhi") if "Delhi" in cities else 0)
history_years = st.sidebar.slider("History shown (years)", 3, 30, 10)
st.sidebar.markdown("---")
st.sidebar.caption(
    "Data: NASA POWER (1981 to 2026), gridded reanalysis. "
    "Values describe a ~50 km grid cell,  a weather station."
)

st.title(f"Temperature outlook: {city}")
st.caption("Monthly mean temperature · SARIMA forecast with 80% prediction interval")

tab_fc, tab_trend, tab_models, tab_about = st.tabs(
    ["📈 Forecast", "🌡️ Climate trends", "🧪 Model comparison", "ℹ️ About & limitations"]
)

# ------------------------------------------------------------------ forecast
with tab_fc:
    hist = monthly[monthly["city"] == city].set_index("date")["temp_mean"]
    recent = hist.iloc[-history_years * 12:]
    fc = forecast[forecast["city"] == city].sort_values("date")
    model_used = fc["model"].iloc[0]

    # typical error of this model for this city (2026 test, then backtest)
    tc = test_city[(test_city["city"] == city) & (test_city["model"] == model_used)]
    bt = backtest[(backtest["city"] == city) & (backtest["model"] == model_used)]
    mae = float(tc["MAE"].iloc[0]) if len(tc) else (float(bt["MAE"].iloc[0]) if len(bt) else np.nan)

    nxt = fc.iloc[0]
    hottest = fc.loc[fc["yhat"].idxmax()]
    coldest = fc.loc[fc["yhat"].idxmin()]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(f"Next month ({nxt['date']:%b %Y})", f"{nxt['yhat']:.1f} °C",
              f"{nxt['lower']:.1f} to {nxt['upper']:.1f} °C", delta_color="off")
    c2.metric("Warmest month ahead", f"{hottest['date']:%b %Y}", f"{hottest['yhat']:.1f} °C", delta_color="off")
    c3.metric("Coolest month ahead", f"{coldest['date']:%b %Y}", f"{coldest['yhat']:.1f} °C", delta_color="off")
    c4.metric("Typical model error", f"± {mae:.2f} °C" if not np.isnan(mae) else "n/a",
              f"{model_used}, 2026 test", delta_color="off")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=recent.index, y=recent.values, name="Observed (grid data)",
                             line=dict(color=GREY, width=2)))
    fig.add_trace(go.Scatter(x=fc["date"], y=fc["upper"], line=dict(width=0),
                             showlegend=False, hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=fc["date"], y=fc["lower"], fill="tonexty",
                             fillcolor="rgba(214,39,40,0.2)", line=dict(width=0), name="80% interval"))
    fig.add_trace(go.Scatter(x=fc["date"], y=fc["yhat"], name="Forecast",
                             line=dict(color=RED, width=3)))
    fig.update_layout(height=450, margin=dict(l=10, r=10, t=30, b=10), hovermode="x unified",
                      yaxis_title="Monthly mean temperature (°C)", legend=dict(orientation="h", y=1.08))
    st.plotly_chart(fig, width="stretch")

    table = fc[["date", "yhat", "lower", "upper"]].copy()
    table["Month"] = table["date"].dt.strftime("%b %Y")
    table = table.rename(columns={"yhat": "Forecast (°C)", "lower": "Lower 80% (°C)", "upper": "Upper 80% (°C)"})
    table = table[["Month", "Forecast (°C)", "Lower 80% (°C)", "Upper 80% (°C)"]].round(1)
    left, right = st.columns([2, 1])
    left.dataframe(table, hide_index=True, width="stretch")
    right.download_button("⬇️ Download forecast (CSV)", table.to_csv(index=False).encode(),
                          file_name=f"{city.lower()}_forecast.csv", mime="text/csv")
    right.info("The 80% interval should contain the true value about 8 months out of 10.")

# ------------------------------------------------------------------ trends
with tab_trend:
    st.warning(
        "Long-term trends from reanalysis data are **source-dependent**: in this project NASA POWER and ERA5 "
        "agreed on year-to-year variability but not on long-term trends in most cities. "
        "Treat the numbers below as descriptive, not as definitive climate trends."
    )
    a = annual[city].dropna()
    slope, pval = trend_stats(a)
    fit = np.polyval(np.polyfit(a.index, a.values, 1), a.index)

    t1, t2 = st.columns([2, 1])
    with t1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=a.index, y=a.values, mode="lines+markers", name="Annual mean",
                                 line=dict(color=BLUE)))
        fig.add_trace(go.Scatter(x=a.index, y=fit, name="Linear trend", line=dict(color=RED, dash="dash")))
        fig.update_layout(height=380, margin=dict(l=10, r=10, t=30, b=10),
                          yaxis_title="Annual mean temperature (°C)", title="Annual mean temperature (full years)")
        st.plotly_chart(fig, width="stretch")
    with t2:
        st.metric("Trend in this dataset", f"{slope:+.2f} °C / decade")
        st.caption(f"p-value {pval:.3f} · {'statistically significant' if pval < 0.05 else 'not statistically significant'} "
                   f"at the 5% level · {a.index.min()} to {a.index.max()}")
        base = a.loc[1981:2010].mean()
        st.metric("Latest full year vs 1981-2010", f"{a.iloc[-1] - base:+.2f} °C", f"{a.index[-1]}", delta_color="off")

    s1, s2 = st.columns(2)
    with s1:
        cm = monthly[monthly["city"] == city].assign(year=lambda d: d["date"].dt.year, month=lambda d: d["date"].dt.month)
        last_full = int(a.index.max())
        early = cm[cm["year"].between(1981, 2010)].groupby("month")["temp_mean"].mean()
        late = cm[cm["year"].between(last_full - 9, last_full)].groupby("month")["temp_mean"].mean()
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=MONTHS, y=early.values, name="1981-2010", line=dict(color=GREY)))
        fig.add_trace(go.Scatter(x=MONTHS, y=late.values, name=f"{last_full - 9}-{last_full}", line=dict(color=RED)))
        fig.update_layout(height=340, margin=dict(l=10, r=10, t=40, b=10), title="Seasonal profile", yaxis_title="°C")
        st.plotly_chart(fig, width="stretch")
    with s2:
        rain = cm[cm["year"] < last_full + 1].groupby("month")["rainfall_mm"].mean()
        fig = go.Figure(go.Bar(x=MONTHS, y=rain.values, marker_color=BLUE))
        fig.update_layout(height=340, margin=dict(l=10, r=10, t=40, b=10),
                          title="Average monthly rainfall", yaxis_title="mm")
        st.plotly_chart(fig, width="stretch")

    st.subheader("All cities: trend in this dataset")
    rows = []
    for c in cities:
        sl, p = trend_stats(annual[c])
        rows.append({"city": c, "slope": sl, "significant": p < 0.05})
    tr = pd.DataFrame(rows).sort_values("slope")
    fig = go.Figure(go.Bar(
        x=tr["slope"], y=tr["city"], orientation="h",
        marker_color=[RED if s else "#aaaaaa" for s in tr["significant"]],
        hovertemplate="%{y}: %{x:+.2f} °C/decade<extra></extra>"))
    fig.update_layout(height=360, margin=dict(l=10, r=10, t=40, b=10), xaxis_title="°C per decade",
                      title="Red = statistically significant (p < 0.05), grey = not significant")
    st.plotly_chart(fig, width="stretch")

# ------------------------------------------------------------------ models
with tab_models:
    st.subheader("How well did each model predict 2026?")
    st.caption("Trained on 1981-2025, tested on the 2026 months that were never used for training or selection. "
               "Lower error is better. Skill = improvement over the seasonal-naive baseline (same month last year).")
    ov = overall.copy()
    ov.index.name = "Model"
    ov = ov.sort_values("MAE").round(2)
    ov = ov.rename(columns={"MAE": "MAE (°C)", "RMSE": "RMSE (°C)", "MAPE": "MAPE (%)",
                            "coverage_80": "80% interval coverage (%)", "skill_vs_seasonal_naive_%": "Skill vs naive (%)"})
    st.dataframe(ov, width="stretch")

    fig = go.Figure(go.Bar(x=ov["MAE (°C)"], y=ov.index, orientation="h",
                           marker_color=[RED if "Selected" in m else BLUE for m in ov.index]))
    fig.update_layout(height=340, margin=dict(l=10, r=10, t=40, b=10), yaxis=dict(autorange="reversed"),
                      xaxis_title="MAE (°C)", title="2026 test error by model (all cities)")
    st.plotly_chart(fig, width="stretch")

    st.subheader(f"{city}: errors by model")
    c_test = test_city[test_city["city"] == city].set_index("model")[["MAE", "RMSE", "MAPE"]].add_suffix(" (2026 test)")
    c_bt = backtest[backtest["city"] == city].set_index("model")[["MAE", "RMSE", "MAPE"]].add_suffix(" (backtest)")
    st.dataframe(c_bt.join(c_test).sort_values("MAE (backtest)").round(2), width="stretch")

    best_bt = best.iloc[:, 0].get(city, "n/a")
    st.info(
        f"Best model in the backtest for {city}: **{best_bt}**. "
        f"The dashboard forecast uses **{model_used}** for every city so that the intervals are consistent and well calibrated."
    )
    st.markdown(
        "**Key takeaway:** monthly temperature is dominated by the seasonal cycle. A simple "
        "'average of the same month over the last 10 years' (Climatology) comes very close to SARIMA, "
        "and complex models such as XGBoost did not help."
    )

# ------------------------------------------------------------------ about
with tab_about:
    st.markdown(
        """
### What this project does
Analyses 45 years of daily weather data for 8 Indian cities (Delhi, Mumbai, Chennai, Kolkata, Bengaluru,
Hyderabad, Jaipur, Shimla), compares forecasting models, and predicts the next 12 months of temperature.

### Method
1. **Data:** NASA POWER daily data, 1981 to 2026, cleaned and aggregated to monthly means
2. **Analysis:** STL decomposition, stationarity tests, warming trends, hot-day counts, monsoon variability
3. **Validation:** NASA POWER compared with ERA5 (a second reanalysis)
4. **Forecasting:** seasonal naive, climatology, linear regression, SARIMA, Prophet, XGBoost
5. **Evaluation:** rolling-origin cross-validation, then a final test on 2026

### Limitations (please read)
- **Gridded model data, not station readings.** Each value represents a ~50 km grid cell. Absolute temperatures can be
  biased, especially in mountain cities such as Shimla, where the grid cell sits well below the town.
- **Trends are source-dependent.** NASA POWER and ERA5 correlate moderately on yearly anomalies, but disagree on
  long-term trends in most cities.
- **Monthly resolution.** These are monthly averages, not daily or weather forecasts.
- **Short test window.** 2026 gives only 9 test months, so small differences between top models are not significant.
- **Not an official forecast.** For official forecasts and warnings, use the India Meteorological Department (IMD).

### Next steps
Validate against IMD station data, add daily forecasting, and extend to more cities.
"""
    )
