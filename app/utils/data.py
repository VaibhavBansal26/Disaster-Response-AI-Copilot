import os, pandas as pd

def load_events():
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "data", "events.csv")
    path = os.path.abspath(path)
    if not os.path.exists(path):
        return pd.DataFrame(columns=["event_id","date","disaster_type","latitude","longitude","location_text","description","source_url"])
    try:
        df = pd.read_csv(path)
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
        for col in ["latitude","longitude"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        return df.dropna(subset=["latitude","longitude"])
    except Exception:
        return pd.DataFrame(columns=["event_id","date","disaster_type","latitude","longitude","location_text","description","source_url"])
