# 🛰️ Satellite Telemetry Visualization & Logging System

> Real-time satellite telemetry visualizer and logger for space situational awareness.

![Python](https://img.shields.io/badge/Python-3.12%2B-blue)
![Matplotlib](https://img.shields.io/badge/Matplotlib-Data%20Visualization-orange)

---

# 🛰️ Satellite Telemetry Visualization & Logging System

A real-time ISS telemetry tracker that simulates and visualizes the International Space Station’s orbit in **3D** and **2D** views.  
Built with **Skyfield**, **VPython**, **Pandas**, and **Cartopy**, this system computes live ISS position data, visualizes its orbit, and logs telemetry for analysis.

## Demo

Screenshots and working proof of the system are available in the `demo/` folder.
---

## ⚙️ Features

- Real-time ISS orbit propagation using **Skyfield**
- **3D interactive globe** visualization with **VPython**
- **2D ground track** display with **Cartopy**
- Live telemetry logging to timestamped CSV files
- Modular and extendable structure

---

## 🧭 Installation

Make sure you have **Python 3.9+** installed.

Clone the repository: bash

git clone https://github.com/<your-username>/Satellite-Telemetry-Visualization-Logging-System.git

cd Satellite-Telemetry-Visualization-Logging-System

If any modules fail (especially Cartopy or VPython), install them manually:
pip install skyfield pandas vpython cartopy numpy matplotlib

## 🚀 Usage
Step 1 — Run the real-time ISS tracker

python iss_tracker_final.py

This launches the 3D VPython globe that simulates and visualizes the ISS orbit in real-time.

Step 2 — Run the 2D map viewer

python map_viewer.py

This opens a 2D Cartopy map that displays the ISS ground track as it moves around the Earth.

Telemetry data (latitude, longitude, altitude, velocity) will automatically be logged into a CSV file inside the data/ folder.

## 📂 Project Structure
solar_flare_forecaster/
├── assets/                     # Images or textures 

├── data/                       # Saved telemetry CSV logs

├── earth_texture_files/        # Earth map textures

├── models/                     # Optional model data

├── scripts/                    # Supporting scripts

├── src/                        # Source code modules

├── iss_tracker_final.py        # 3D real-time ISS tracker

├── map_viewer.py               # 2D Cartopy map visualizer

├── requirements.txt            # Dependencies

└── README.md                   # Documentation

## 📊 Sample Output
Timestamp (UTC)	Latitude	Longitude	Altitude (km)	Velocity (km/s)

2025-11-03 10:41:00     	45.12	     -73.22     	420.55	     7.66

2025-11-03 10:42:00	     46.09	     -72.95	     420.58	     7.66

A 3D VPython globe that simulates and visualizes the ISS orbit in real-time.

A 2D Cartopy map that displays the ISS ground track as it moves around the Earth.

Telemetry logs are automatically saved in the /data folder.

## 🧩 Built With
Library	     Purpose
Skyfield	     Orbital mechanics and position calculation
VPython	     3D Earth and ISS visualization
Cartopy	     2D Earth map and orbit plotting
Pandas	     Data logging and CSV management
NumPy	     Mathematical operations
Matplotlib	Optional for static plots



## 🪐 Credits
Developed by Jenifer Aloysius
For educational and research purposes in Space Situational Awareness & Satellite Tracking.

## 📜 License
This project is licensed under the MIT License — feel free to use, modify, and share.

## 👩‍🚀 Author
Jenifer Aloysius
🎓 B.Tech in AI & Data Science | Passionate about SpaceTech & Research
🌌 Exploring how AI can enhance satellite monitoring and prediction

⭐ If you found this project interesting, consider giving it a star! It helps support future open-source work in space tech and AI.
