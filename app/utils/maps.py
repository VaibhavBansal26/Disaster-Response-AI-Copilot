# import os
# import pydeck as pdk

# def azure_maps_tile_layer():
#     """
#     Returns a PyDeck TileLayer that uses Azure Maps as the base map.
#     Requires AZURE_MAPS_KEY in env or st.session_state['maps_key'] (passed in by caller).
#     """
#     key = os.getenv("AZURE_MAPS_KEY", "").strip()
#     if not key:
#         return None

#     # Docs: Azure Maps Raster Tiles v2
#     # Styles: road, grayscale_dark, satellite (satellite requires separate tileset; keep road for MVP)
#     url = (
#         "https://atlas.microsoft.com/map/tile/png"
#         "?api-version=2.1&tilesetId=microsoft.base.road&zoom={z}&x={x}&y={y}"
#         f"&subscription-key={key}"
#     )

#     return pdk.Layer(
#         "TileLayer",
#         data=None,
#         tile_size=256,
#         min_zoom=0,
#         max_zoom=19,
#         get_tile_data=None,
#         elevation_scale=1,
#         pickable=False,
#         opacity=1.0,
#         parameters={"depthTest": False},
#         # deck.gl accepts data URL templates via "data" for v8; pydeck maps it.
#         # For compatibility, we pass it as "data" in the constructor below:
#         # (pydeck will attach as 'data' prop on the Layer)
#         data=url,
#         id="azure-maps-tiles",
#     )

# def deck_with_base(layers, latitude, longitude, zoom=4):
#     """
#     Builds a Deck with Azure Maps tiles if key is set, otherwise plain deck.
#     """
#     base = azure_maps_tile_layer()
#     all_layers = [base] + layers if base else layers
#     return pdk.Deck(
#         layers=all_layers,
#         initial_view_state=pdk.ViewState(latitude=latitude, longitude=longitude, zoom=zoom),
#         map_style=None  # we supply our own tile base when Azure Maps key is present
#     )

# app/utils/maps.py
from __future__ import annotations
import pydeck as pdk
import pandas as pd


_SEVERITY_COLORS = {
    "critical": [220, 20, 60, 200],   # crimson
    "high":     [255, 99, 71, 200],   # tomato
    "medium":   [255, 165, 0, 180],   # orange
    "low":      [34, 139, 34, 170],   # forest green
}


def _color_row(sev: str) -> list[int]:
    if not isinstance(sev, str):
        return _SEVERITY_COLORS["low"]
    return _SEVERITY_COLORS.get(sev.strip().lower(), _SEVERITY_COLORS["low"])


def build_deck(
    df: pd.DataFrame,
    lat_col: str = "lat",
    lon_col: str = "lon",
    severity_col: str = "severity",
    show_heatmap: bool = True,
    radius_m: int = 900,
):
    """
    Returns a pydeck.Deck with a scatter layer (colored by severity)
    and an optional heatmap layer.
    """
    if df is None or df.empty:
        # Safe empty frame to avoid pydeck errors
        df = pd.DataFrame({lat_col: [], lon_col: [], severity_col: []})

    # Precompute colors once to avoid JS expressions
    df = df.copy()
    df["__color__"] = df[severity_col].apply(_color_row)

    # ---- Scatter points (NO duplicate 'data=' kw!) ----
    scatter = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position=f"[{lon_col}, {lat_col}]",
        get_fill_color="__color__",
        get_radius=radius_m,
        pickable=True,
        auto_highlight=True,
    )

    layers = [scatter]

    if show_heatmap and not df.empty:
        heat = pdk.Layer(
            "HeatmapLayer",
            data=df,
            get_position=f"[{lon_col}, {lat_col}]",
            aggregation='"MEAN"',
            get_weight="1",
            radiusPixels=60,
        )
        layers.append(heat)

    # Initial view — center on data if present
    if not df.empty:
        center_lat = float(df[lat_col].astype(float).mean())
        center_lon = float(df[lon_col].astype(float).mean())
    else:
        # CONUS as a reasonable default
        center_lat, center_lon = 39.5, -98.35

    view = pdk.ViewState(latitude=center_lat, longitude=center_lon, zoom=5)

    deck = pdk.Deck(
        layers=layers,
        initial_view_state=view,
        tooltip={
            "text": "{name}\nSeverity: {" + severity_col + "}\n({"
            + lat_col + "}, {" + lon_col + "})"
        },
        # If you have MAPBOX_API_KEY in env, you can use a map style like:
        # map_style="mapbox://styles/mapbox/light-v11",
        map_style=None,  # works without a Mapbox token
    )
    return deck
