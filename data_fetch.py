import io
import os
import re
import requests
import pandas as pd

HDX_PAGE = "https://data.humdata.org/dataset/faostat-food-prices-for-saudi-arabia"

# Known direct resource patterns sometimes exposed by HDX for FAOSTAT (subject to change)
CANDIDATE_URLS = [
    # Try a likely CSV resource path; if HDX changes, the app will still work with cache.
    "https://proxy.hxlstandard.org/data/download?url=https%3A%2F%2Ffenixservices.fao.org%2Ffaostat%%2Fapi%2Fv1%2Fen%2FFBS%2F",
]

def _clean(df: pd.DataFrame) -> pd.DataFrame:
    # Expect columns like: Area, Item, Year, Month or Date, Value
    df = df.rename(columns={c: c.strip().title() for c in df.columns})
    if "Date" not in df.columns and {"Year", "Month"}.issubset(df.columns):
        df["Date"] = pd.to_datetime(dict(year=df["Year"].astype(int), month=df["Month"].astype(int), day=1))
    if "Indicator" not in df.columns:
        # Try to infer indicator from Item
        df["Indicator"] = df.get("Item", "Food CPI")
    # Filter Saudi Arabia if Area exists
    if "Area" in df.columns:
        df = df[df["Area"].str.contains("Saudi", case=False, na=False)]
    # Keep relevant columns
    keep = [c for c in ["Area","Indicator","Item","Year","Month","Date","Value"] if c in df.columns]
    df = df[keep].dropna(subset=["Date","Value"])
    df = df.sort_values("Date")
    return df

def fetch_food_cpi(cache_path: str) -> pd.DataFrame:
    # Try each candidate URL; fall back to cache on failure
    for url in CANDIDATE_URLS:
        try:
            r = requests.get(url, timeout=30)
            if r.ok and ("csv" in r.headers.get("Content-Type","").lower() or r.text.count(",")>5):
                df = pd.read_csv(io.StringIO(r.text))
                return _clean(df)
        except Exception:
            pass
    # Fallback to cache
    return pd.read_csv(cache_path, parse_dates=["Date"])