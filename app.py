import os
import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st

from data_fetch import fetch_food_cpi

st.set_page_config(page_title="OpenCompete – KSA Food & Retail", page_icon="???", layout="wide")

# ---------- i18n ----------
T = {
    "en": {
        "app": "??? OpenCompete – KSA Food & Retail Competition Dashboard (MVP)",
        "data_controls": "Data Controls",
        "auto_load": "This MVP auto-loads Saudi Food CPI & General CPI.",
        "yoy": "YoY threshold (%)",
        "mom": "MoM threshold (%)",
        "alert_note": "Alerts trigger when both YoY and MoM exceed thresholds.",
        "kpi_food": "Food CPI (latest)",
        "kpi_yoy": "Food CPI YoY %",
        "kpi_mom": "Food CPI MoM %",
        "tab_trend": "Trend",
        "tab_changes": "Changes",
        "tab_alerts": "Alerts",
        "trend_title": "CPI Trend (Food vs General)",
        "changes_title": "Food CPI – YoY and MoM Changes",
        "alert_table_note": "Rows flagged where both YoY and MoM exceed thresholds:",
        "caption": "Data: FAOSTAT/HDX (Saudi), GASTAT (context). MVP for hackathon use.",
        "series_food": "Food CPI",
        "series_gen": "General CPI",
        "lang_label": "Language",
        "lang_en": "English",
        "lang_ar": "ÇáÚÑÈíÉ",
    },
    "ar": {
        "app": "??? OpenCompete – áæÍÉ ãÄÔÑÇÊ ÇáãäÇİÓÉ áŞØÇÚ ÇáÃÛĞíÉ æÇáÊÌÒÆÉ (äãæĞÌ Ãæáí)",
        "data_controls": "ÇáÊÍßã ÈÇáÈíÇäÇÊ",
        "auto_load": "åĞÇ ÇáäãæĞÌ íÌáÈ ÊáŞÇÆíÇğ ãÄÔÑ ÃÓÚÇÑ ÇáÛĞÇÁ æÇáÑŞã ÇáŞíÇÓí ÇáÚÇã İí ÇáÓÚæÏíÉ.",
        "yoy": "ÍÏ ÇáÊÛíÑ ÇáÓäæí (%)",
        "mom": "ÍÏ ÇáÊÛíÑ ÇáÔåÑí (%)",
        "alert_note": "íÊã ÅØáÇŞ ÇáÊäÈíå ÚäÏãÇ íÊÌÇæÒ ÇáÊÛíÑ ÇáÓäæí æÇáÔåÑí ÇáÍÏøíä ãÚğÇ.",
        "kpi_food": "ÃÍÏË ŞíãÉ áãÄÔÑ ÃÓÚÇÑ ÇáÛĞÇÁ",
        "kpi_yoy": "ÊÛíÑ Óäæí áãÄÔÑ ÃÓÚÇÑ ÇáÛĞÇÁ (%)",
        "kpi_mom": "ÊÛíÑ ÔåÑí áãÄÔÑ ÃÓÚÇÑ ÇáÛĞÇÁ (%)",
        "tab_trend": "ÇáÇÊÌÇå",
        "tab_changes": "ÇáÊÛíÑÇÊ",
        "tab_alerts": "ÇáÊäÈíåÇÊ",
        "trend_title": "ÇÊÌÇå ÇáãÄÔÑ (ÇáÛĞÇÁ ãŞÇÈá ÇáÚÇã)",
        "changes_title": "ãÄÔÑ ÇáÛĞÇÁ – ÇáÊÛíÑ ÇáÓäæí æÇáÔåÑí",
        "alert_table_note": "ÇáÕİæİ ÇáãÚáøóãÉ ÚäÏãÇ íÊÌÇæÒ ÇáÓäæí æÇáÔåÑí ÇáÍÏøíä:",
        "caption": "ÇáãÕÏÑ: FAOSTAT/HDX (ÇáÓÚæÏíÉ)¡ GASTAT (ááÓíÇŞ). äãæĞÌ ááåÇßËæä.",
        "series_food": "ãÄÔÑ ÃÓÚÇÑ ÇáÛĞÇÁ",
        "series_gen": "ÇáÑŞã ÇáŞíÇÓí ÇáÚÇã",
        "lang_label": "ÇááÛÉ",
        "lang_en": "English",
        "lang_ar": "ÇáÚÑÈíÉ",
    },
}

def tr(key):
    lang = st.session_state.get("lang", "ar")
    return T[lang][key]

# ---------- Sidebar: language & thresholds ----------
with st.sidebar:
    st.selectbox(
        tr("lang_label"),
        options=["ar","en"],
        format_func=lambda x: "ÇáÚÑÈíÉ" if x=="ar" else "English",
        key="lang",
        index=0
    )

# Inject RTL when Arabic
if st.session_state.get("lang","ar") == "ar":
    st.markdown("""
    <style>
      html, body, [class*="css"]  { direction: rtl; text-align: right; }
    </style>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.header(tr("data_controls"))
    st.write(tr("auto_load"))
    yoy = st.slider(tr("yoy"), 0.0, 10.0, 3.0, 0.1)
    mom = st.slider(tr("mom"), 0.0, 5.0, 0.6, 0.1)
    st.caption(tr("alert_note"))

st.title(tr("app"))

# ---------- Data ----------
cache_csv = os.path.join("data", "sample_food_cpi_sa.csv")
df = fetch_food_cpi(cache_csv)

if "Date" not in df.columns:
    st.error("Data missing Date column; please update data source.")
    st.stop()

pivot = df.pivot_table(index="Date", columns="Indicator", values="Value").reset_index()
for col in ["Food CPI", "General CPI"]:
    if col not in pivot.columns:
        pivot[col] = np.nan
pivot = pivot.sort_values("Date")

for col in ["Food CPI", "General CPI"]:
    pivot[f"{col} MoM %"] = pivot[col].pct_change() * 100
    pivot[f"{col} YoY %"] = pivot[col].pct_change(12) * 100

alerts = pivot.assign(
    Heat=(
        (pivot["Food CPI YoY %"] - pivot["Food CPI YoY %"].mean()) / (pivot["Food CPI YoY %"].std() + 1e-6) * 0.6
        + (pivot["Food CPI MoM %"] - pivot["Food CPI MoM %"].mean()) / (pivot["Food CPI MoM %"].std() + 1e-6) * 0.4
    ),
    Alert=lambda d: (d["Food CPI YoY %"] > yoy) & (d["Food CPI MoM %"] > mom)
)

latest = pivot.iloc[-1:].copy()
c1, c2, c3 = st.columns(3)
c1.metric(tr("kpi_food"), f"{latest['Food CPI'].values[0]:.1f}")
c2.metric(tr("kpi_yoy"), f"{latest['Food CPI YoY %'].values[0]:.2f}")
c3.metric(tr("kpi_mom"), f"{latest['Food CPI MoM %'].values[0]:.2f}")

# ---------- Tabs ----------
tab1, tab2, tab3 = st.tabs([tr("tab_trend"), tr("tab_changes"), tr("tab_alerts")])

food_label = tr("series_food")
gen_label  = tr("series_gen")

with tab1:
    # Rename series for localized legend
    plot_df = pivot.rename(columns={
        "Food CPI": food_label,
        "General CPI": gen_label
    })
    fig = px.line(plot_df, x="Date", y=[food_label, gen_label], markers=True, title=tr("trend_title"))
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    ch_df = pivot.tail(24).rename(columns={
        "Food CPI YoY %": "YoY %",
        "Food CPI MoM %": "MoM %"
    })
    fig2 = px.bar(ch_df, x="Date", y=["YoY %","MoM %"], barmode="group", title=tr("changes_title"))
    st.plotly_chart(fig2, use_container_width=True)

with tab3:
    st.write(tr("alert_table_note"))
    st.dataframe(
        alerts.loc[alerts["Alert"], ["Date","Food CPI","Food CPI YoY %","Food CPI MoM %","Heat"]].round(2)
        .rename(columns={
            "Date": "ÇáÊÇÑíÎ" if st.session_state["lang"]=="ar" else "Date",
            "Food CPI": food_label,
            "Food CPI YoY %": "ÊÛíÑ Óäæí %" if st.session_state["lang"]=="ar" else "YoY %",
            "Food CPI MoM %": "ÊÛíÑ ÔåÑí %" if st.session_state["lang"]=="ar" else "MoM %",
            "Heat": "ÇáÍÑÇÑÉ" if st.session_state["lang"]=="ar" else "Heat"
        })
    )

st.divider()
st.caption(tr("caption"))