# import os, pandas as pd, streamlit as st, pydeck as pdk
# from app.utils.data import load_events
# from app.utils.maps import deck_with_base

# st.title("📍 Dashboard")

# df = load_events()

# if df.empty:
#     st.info("No events found. Add rows to data/events.csv")
# else:
#     # Sidebar filters
#     with st.sidebar:
#         types = sorted(df['disaster_type'].dropna().unique().tolist())
#         sel_types = st.multiselect("Disaster types", types, default=types)
#         date_min, date_max = pd.to_datetime(df['date']).min(), pd.to_datetime(df['date']).max()
#         sel_range = st.date_input("Date range", (date_min.date(), date_max.date()))
#     # Filter
#     m = df.copy()
#     if sel_types: m = m[m['disaster_type'].isin(sel_types)]
#     if isinstance(sel_range, (list, tuple)) and len(sel_range)==2:
#         s,e = pd.to_datetime(sel_range[0]), pd.to_datetime(sel_range[1])
#         m = m[(pd.to_datetime(m['date'])>=s) & (pd.to_datetime(m['date'])<=e)]

#     st.write(f"Showing **{len(m)}** incidents")

#     # Layers
#     color_expr = '[disaster_type == "wildfire" ? 220 : 30, 60, disaster_type == "flood" ? 220 : 30, 200]'
#     points = pdk.Layer(
#         "ScatterplotLayer",
#         m,
#         get_position='[longitude, latitude]',
#         get_radius=700,
#         get_fill_color=color_expr,
#         pickable=True,
#         id="incidents"
#     )

#     # Build deck: if AZURE_MAPS_KEY is set, base tiles are Azure Maps
#     lat = m['latitude'].mean() if len(m)>0 else 37.5
#     lon = m['longitude'].mean() if len(m)>0 else -96.5
#     deck = deck_with_base([points], latitude=lat, longitude=lon, zoom=4)

#     st.pydeck_chart(deck, use_container_width=True)

#     st.subheader("Events")
#     st.dataframe(m[['date','disaster_type','location_text','description','source_url']].sort_values('date', ascending=False), use_container_width=True)

# app/pages/dashboard.py
# app/pages/dashboard.py
import streamlit as st
import pandas as pd

from app.utils.data import load_events  # your loader
from app.utils.maps import build_deck

st.set_page_config(page_title="Incident Dashboard", page_icon="📊", layout="wide")
st.title("📊 Incident Dashboard")

# ---------------- Controls ----------------
col1, col2 = st.columns([1, 3])
with col1:
    show_heatmap = st.toggle("Heatmap", value=True)
with col2:
    severity_filter = st.multiselect(
        "Severity",
        ["critical", "high", "medium", "low"],
        default=["critical", "high", "medium", "low"],
    )

# ---------------- Data --------------------
df: pd.DataFrame = load_events()

def detect_geo_columns(df: pd.DataFrame):
    # search case-sensitively and insensitively
    cols = list(df.columns)
    lower = {c.lower(): c for c in cols}

    lat_candidates = ["lat", "latitude", "y"]
    lon_candidates = ["lon", "lng", "longitude", "x"]

    lat_col = next((lower[c] for c in lat_candidates if c in lower), None)
    lon_col = next((lower[c] for c in lon_candidates if c in lower), None)

    return lat_col, lon_col

if df is None or df.empty:
    st.info("No incidents available yet.")
    st.stop()

lat_col, lon_col = detect_geo_columns(df)
if not lat_col or not lon_col:
    st.error(
        "Your data is missing latitude/longitude columns. "
        f"Found columns: {list(df.columns)}. "
        "Expected one of: lat/latitude (for latitude) and lon/lng/longitude (for longitude)."
    )
    st.stop()

# Normalize severity + optional date
if "severity" not in df.columns:
    df["severity"] = "low"
else:
    df["severity"] = df["severity"].astype(str).str.lower().str.strip()

if "date" in df.columns:
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

if severity_filter:
    df = df[df["severity"].isin([s.lower() for s in severity_filter])]

# ---------------- Map ---------------------
deck = build_deck(
    df=df,
    lat_col=lat_col,
    lon_col=lon_col,
    severity_col="severity",
    show_heatmap=show_heatmap,
    radius_m=900,
)
st.pydeck_chart(deck, use_container_width=True)

# ---------------- Table -------------------
with st.expander("Show incident table"):
    # Try to show a nice minimal set of columns if present
    preferred = [c for c in ["name", "summary", "severity", "date", lat_col, lon_col] if c in df.columns]
    show_cols = preferred if preferred else df.columns
    st.dataframe(
        df[show_cols].sort_values(by="date", ascending=False, na_position="last") if "date" in df.columns else df[show_cols],
        use_container_width=True,
        hide_index=True,
    )
