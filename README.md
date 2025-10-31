# OpenCompete – Saudi Food & Retail Competition Dashboard (MVP)

A Streamlit web app that visualizes **Food CPI** trends for Saudi Arabia and raises simple "market heat" alerts.
It uses **open data** sources and is designed for hackathons: quick to run, easy to extend.

## Data sources (auto-fetched at runtime)
- **FAOSTAT / HDX – Food CPI & General CPI for Saudi Arabia** (CSV):
  https://data.humdata.org/dataset/faostat-food-prices-for-saudi-arabia
- **GASTAT – CPI monthly reports** (context & validation):
  https://www.stats.gov.sa/en/w/cpi-1
- **Saudi Open Data / DataSaudi** (context & future API hooks):
  https://datasaudi.sa/en/data-explorer

> The app will try to fetch the latest CSV from HDX at runtime. If fetching fails (e.g., offline),
> it will fall back to the cached sample file in `data/sample_food_cpi_sa.csv`.

## Quick start (local)
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy (free)
- **Streamlit Community Cloud**: push this folder to GitHub and deploy.
- **Hugging Face Spaces (Streamlit)**: upload repo and select Streamlit template.

## Files
- `app.py` – main Streamlit app
- `data_fetch.py` – helper to download & clean datasets
- `data/sample_food_cpi_sa.csv` – small cached sample (Saudi monthly Food CPI & CPI)
- `pages/01_About.py` – sources & methodology