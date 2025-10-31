import streamlit as st

st.title("About & Sources")
st.markdown(
    '''
**OpenCompete – Saudi Food & Retail Competition Dashboard (MVP)**

**Primary data sources:**
- FAOSTAT / HDX – Food CPI & General CPI for Saudi Arabia (CSV).  
- GASTAT – CPI monthly reports and Average Prices of Goods & Services.  
- Saudi Open Data (DataSaudi) – Explorer for economic/social indicators.  

**Methodology (MVP):**
- Load monthly **Food CPI** and **General CPI** for Saudi Arabia.
- Compute **YoY** and **MoM** changes and a simple **Market Heat** score:
  - Heat = weighted z-score of (Food CPI YoY, Food CPI MoM).
  - Flags sectors/months when both YoY and MoM exceed thresholds.

**Roadmap:**
- Add **commodity-level average prices** (rice, chicken, tomatoes...) from GASTAT.
- Add **retail establishment counts** by activity (Retail trade) via KSA data portals.
- Provide public **REST API** for charts and CSV downloads.

**Disclaimer:** This MVP is for demonstration. Always validate figures with official releases.
''')