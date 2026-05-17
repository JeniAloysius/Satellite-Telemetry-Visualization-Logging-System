"""
multi_satellite_plotly.py
Interactive multi-satellite tracker (Plotly + Dash) using Skyfield TLEs.

Run:
    python multi_satellite_plotly.py
Then open http://127.0.0.1:8050/ in your browser.

Notes:
 - Default targets: ISS, HUBBLE, NOAA 19 (change TARGETS below).
 - Uses Dash Interval to fetch & update every UPDATE_INTERVAL_S seconds.
"""

from skyfield.api import load, wgs84
import numpy as np
import pandas as pd
import math, time
from datetime import datetime, timezone
import requests

import plotly.graph_objs as go
from dash import Dash, dcc, html, Output, Input

# ---------------- CONFIG ----------------
TLE_URL = "https://celestrak.org/NORAD/elements/active.txt"
TARGETS = ["ISS (ZARYA)", "HUBBLE SPACE TELESCOPE", "NOAA 19"]   # change as needed
UPDATE_INTERVAL_S = 5      # dashboard update interval (seconds)
ORBIT_HISTORY_MINUTES = 30 # how many minutes of orbit path to compute (past+future)
SAMPLES_PER_MIN = 6        # time resolution: samples per minute
EARTH_RADIUS_KM = 6371.0
# ----------------------------------------

# Skyfield setup
ts = load.timescale()

def load_tle_and_select(url=TLE_URL, target_list=TARGETS):
    sats = load.tle_file(url)
    # Build lookup by normalized name and by NORAD id (line1/line2 parsing)
    selected = []
    target_upper = [t.upper() for t in target_list]
    for s in sats:
        if s.name.upper() in target_upper:
            selected.append(s)
        else:
            # also match partial names (e.g., "ISS" in "ISS (ZARYA)")
            for t in target_upper:
                if t in s.name.upper():
                    selected.append(s)
                    break
    return selected

# Preload satellites
try:
    sats_list = load_tle_and_select()
    if len(sats_list) == 0:
        print("Warning: no matching satellites found in TLE file for your TARGETS. Loading first 3 as fallback.")
        all_sats = load.tle_file(TLE_URL)
        sats_list = all_sats[:3]
except Exception as e:
    print("TLE load error:", e)
    sats_list = []

def compute_sat_positions(sat, times):
    """Return dict with arrays: lat, lon, alt_km, x,y,z (unit-sphere scaled)"""
    geocs = sat.at(times)
    subs = wgs84.subpoint(geocs)
    lats = np.array([s.latitude.degrees for s in subs])
    lons = np.array([s.longitude.degrees for s in subs])
    alts = np.array([s.elevation.km for s in subs])
    # ECI positions in km
    pos_km = np.array([p for p in geocs.position.km]).T  # shape (N,3)
    # convert to unit-sphere coords (Earth radius = 1)
    pos_unit = pos_km / EARTH_RADIUS_KM
    xs, ys, zs = pos_unit[:,0], pos_unit[:,1], pos_unit[:,2]
    return {"lat": lats, "lon": lons, "alt_km": alts, "x": xs, "y": ys, "z": zs}

def make_times_window(center_ts, minutes=ORBIT_HISTORY_MINUTES, samples_per_min=SAMPLES_PER_MIN):
    """Return a Skyfield Time array centered on center_ts spanning +/- minutes/2"""
    total_samples = int(minutes * samples_per_min)
    dt_seconds = 60.0 / samples_per_min
    # create times from -half to +half
    half = total_samples//2
    t0 = center_ts - (half * dt_seconds)
    times = ts.utc( *[], jd=[] )  # placeholder: build via ts.utc with arrays
    # easier: build Python datetimes then use ts.utc(list_of_datetimes)
    center_dt = datetime.utcnow().replace(tzinfo=timezone.utc)
    times_dt = [ center_dt + np.timedelta64(int((i-half)*dt_seconds),'s') for i in range(total_samples) ]
    # convert numpy timedelta64 objects to python datetimes
    times_dt_py = []
    for td in times_dt:
        if isinstance(td, np.datetime64):
            # convert numpy datetime64 to python datetime
            ts_py = pd.to_datetime(str(td)).to_pydatetime().replace(tzinfo=timezone.utc)
        else:
            ts_py = td
        times_dt_py.append(ts_py)
    return ts.utc(times_dt_py)

# Utility: create a nice color per satellite
PALETTE = ["#FFDD00","#00CCFF","#FF66AA","#33FF77","#FF8C00","#8A2BE2","#00BFFF"]
def color_for_index(i):
    return PALETTE[i % len(PALETTE)]

# ---------------- Plotly figure factory ----------------
def build_figure(sats_objs):
    now = datetime.utcnow().replace(tzinfo=timezone.utc)
    times = make_times_window(now, minutes=ORBIT_HISTORY_MINUTES, samples_per_min=SAMPLES_PER_MIN)

    # Build traces
    traces = []
    geo_traces = []  # ground track traces (scattergeo)
    for i, sat in enumerate(sats_objs):
        data = compute_sat_positions(sat, times)
        name = sat.name
        clr = color_for_index(i)

        # Orbit path (3D)
        traces.append(go.Scatter3d(
            x=data["x"], y=data["y"], z=data["z"],
            mode="lines",
            line=dict(color=clr, width=2),
            name=f"{name} path",
            hoverinfo="text",
            text=[f"{name}<br>lat={lat:.3f}<br>lon={lon:.3f}<br>alt={alt:.0f}km"
                  for lat,lon,alt in zip(data["lat"], data["lon"], data["alt_km"])]
        ))

        # Current position marker (last sample)
        traces.append(go.Scatter3d(
            x=[data["x"][-1]], y=[data["y"][-1]], z=[data["z"][-1]],
            mode="markers",
            marker=dict(size=4, color=clr),
            name=f"{name} (now)",
            hoverinfo="text",
            text=[f"{name} (now)<br>lat={data['lat'][-1]:.3f}<br>lon={data['lon'][-1]:.3f}<br>alt={data['alt_km'][-1]:.0f} km"]
        ))

        # Ground track (2D map)
        geo_traces.append(go.Scattergeo(
            lon = data["lon"],
            lat = data["lat"],
            mode = "lines",
            line = dict(width=1.5, color=clr),
            name = f"{name} ground track",
            hoverinfo="text",
            text=[f"{name}<br>lat={lat:.3f}<br>lon={lon:.3f}" for lat,lon in zip(data["lat"], data["lon"])]
        ))

    # add an Earth sphere (simple shaded unit sphere)
    # Create sphere mesh coordinates
    th = np.linspace(0, math.pi, 50)   # polar
    ph = np.linspace(0, 2*math.pi, 100) # azimuth
    th_grid, ph_grid = np.meshgrid(th, ph)
    xs = np.sin(th_grid) * np.cos(ph_grid)
    ys = np.sin(th_grid) * np.sin(ph_grid)
    zs = np.cos(th_grid)
    # Basic surface with light shading via colorscale (optionally map image)
    earth_surface = go.Surface(
        x=xs, y=ys, z=zs,
        showscale=False,
        colorscale='Earth',  # builtin continuous map; not a texture
        lighting=dict(ambient=0.8, diffuse=0.5, roughness=0.9),
        name="Earth"
    )

    # Layout for 3D scene
    layout_3d = go.Layout(
        title="3D Globe - Satellite Orbits",
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            aspectmode='data',
            camera=dict(eye=dict(x=1.7, y=1.2, z=1.2))
        ),
        margin=dict(l=0, r=0, t=40, b=0),
        showlegend=True,
        legend=dict(x=0.01, y=0.98)
    )

    fig3d = go.Figure(data=[earth_surface] + traces, layout=layout_3d)

    # 2D map figure (ground tracks)
    fig_map = go.Figure(data=geo_traces)
    fig_map.update_geos(projection_type="natural earth")
    fig_map.update_layout(title="Ground Tracks (2D)", margin=dict(l=0,r=0,t=40,b=0), showlegend=True)

    return fig3d, fig_map

# ---------------- Dash App ----------------
app = Dash(__name__)
app.layout = html.Div([
    html.H2("Multi-Satellite Tracker — Plotly + Dash"),
    html.Div([
        dcc.Graph(id="globe-graph", style={"height":"65vh", "width":"65%", "display":"inline-block"}),
        dcc.Graph(id="map-graph", style={"height":"65vh", "width":"34%", "display":"inline-block", "verticalAlign":"top"})
    ]),
    html.Div(id="status", style={"margin":"6px 10px", "fontSize":"14px"}),
    dcc.Interval(id="interval-component", interval=UPDATE_INTERVAL_S*1000, n_intervals=0)
], style={"fontFamily":"Arial, sans-serif"})

@app.callback(
    Output("globe-graph", "figure"),
    Output("map-graph", "figure"),
    Output("status", "children"),
    Input("interval-component", "n_intervals")
)
def update_all(n):
    # Try refreshing TLE every few updates to pick any TLE updates
    try:
        # reload and filter - this ensures we pick updated TLE lines occasionally
        sats_current = load_tle_and_select()
    except Exception as e:
        print("TLE refresh error:", e)
        sats_current = sats_list if sats_list else []

    if not sats_current:
        return go.Figure(), go.Figure(), f"Error loading satellites at {datetime.utcnow().isoformat()}"

    fig3d, fig_map = build_figure(sats_current)
    status = f"Last update (UTC): {datetime.utcnow().isoformat()} | Satellites: {', '.join([s.name for s in sats_current])}"
    return fig3d, fig_map, status

if __name__ == "__main__":
    print("Starting Dash server at http://127.0.0.1:8050/")
    app.run_server(debug=False)
