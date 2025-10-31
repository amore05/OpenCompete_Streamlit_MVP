import os
import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st

from data_fetch import fetch_food_cpi

st.set_page_config(page_title="OpenCompete – KSA Food & Retail", page_icon="🍽️", layout="wide")

st.title("🍽️ OpenCompete – KSA Food & Retail Competition Dashboard (MVP)")

with st.sidebar:
    st.header("Data Controls")
    st.write("This MVP auto-loads Saudi **Food CPI** & **General CPI**.")
    thresh_yoy = st.slider("YoY threshold (%)", 0.0, 10.0, 3.0, 0.1)
    thresh_mom = st.slider("MoM threshold (%)", 0.0, 5.0, 0.6, 0.1)
    st.caption("Alerts trigger when both YoY and MoM exceed thresholds.")

# Load data (fetch or fallback to cache)
cache_csv = os.path.join("data", "sample_food_cpi_sa.csv")
df = fetch_food_cpi(cache_csv)

# Ensure expected columns
if "Date" not in df.columns:
    st.error("Data missing Date column; please update data source.")
    st.stop()

# Pivot to have separate series for Food CPI and General CPI
pivot = df.pivot_table(index="Date", columns="Indicator", values="Value").reset_index()
for col in ["Food CPI", "General CPI"]:
    if col not in pivot.columns:
        pivot[col] = np.nan
pivot = pivot.sort_values("Date")

# Compute changes
for col in ["Food CPI", "General CPI"]:
    pivot[f"{col} MoM %"] = pivot[col].pct_change() * 100
    pivot[f"{col} YoY %"] = pivot[col].pct_change(12) * 100

# Alert logic
alerts = pivot.assign(
    Heat=(
        (pivot["Food CPI YoY %"] - pivot["Food CPI YoY %"].mean()) / (pivot["Food CPI YoY %"].std() + 1e-6) * 0.6
        + (pivot["Food CPI MoM %"] - pivot["Food CPI MoM %"].mean()) / (pivot["Food CPI MoM %"].std() + 1e-6) * 0.4
    ),
    Alert=lambda d: (d["Food CPI YoY %"] > thresh_yoy) & (d["Food CPI MoM %"] > thresh_mom)
)

# KPI cards
latest = pivot.iloc[-1:].copy()
col1, col2, col3 = st.columns(3)
col1.metric("Food CPI (latest)", f"{latest['Food CPI'].values[0]:.1f}")
col2.metric("Food CPI YoY %", f"{latest['Food CPI YoY %'].values[0]:.2f}")
col3.metric("Food CPI MoM %", f"{latest['Food CPI MoM %'].values[0]:.2f}")

# Charts
tab1, tab2, tab3 = st.tabs(["Trend", "Changes", "Alerts"])

with tab1:
    fig = px.line(pivot, x="Date", y=["Food CPI","General CPI"], markers=True, title="CPI Trend (Food vs General)")
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    fig2 = px.bar(pivot.tail(24), x="Date", y=["Food CPI YoY %","Food CPI MoM %"], barmode="group",
                  title="Food CPI – YoY and MoM Changes")
    st.plotly_chart(fig2, use_container_width=True)

with tab3:
    st.write("Rows flagged where **both** YoY and MoM exceed thresholds:")
    st.dataframe(alerts.loc[alerts["Alert"], ["Date","Food CPI","Food CPI YoY %","Food CPI MoM %","Heat"]].round(2))

st.divider()
st.caption("Data: FAOSTAT/HDX (Saudi), GASTAT (context). MVP for hackathon use.")