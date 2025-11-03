# Satellite Telemetry Visualization & Logging System

A real-time ISS telemetry tracker that logs live telemetry and visualizes the ground track on a world map.

## Features
- Real-time ISS telemetry fetch & CSV logging
- 3D VPython globe visualization
- Live 2D ground-track map with Cartopy
- Modular code for future ML/solar-weather extensions

## Tech stack
Python, Pandas, Skyfield, VPython, Matplotlib, Cartopy, Requests

## Run (local)
1. Create & activate venv: `python -m venv venv && venv\Scripts\activate`
2. Install deps: `pip install -r requirements.txt`
3. Run tracker: `python iss_tracker_final.py`
4. Run map viewer (separate terminal): `python map_viewer.py`
