# 🛰️ Satellite Telemetry Visualization & Logging System

> Real-time satellite telemetry visualizer and logger for space situational awareness.

![Python](https://img.shields.io/badge/Python-3.12%2B-blue)
![Matplotlib](https://img.shields.io/badge/Matplotlib-Data%20Visualization-orange)
![Tkinter](https://img.shields.io/badge/Tkinter-GUI-lightgrey)
![Status](https://img.shields.io/badge/Status-Active-success)

---

# 🛰️ ISS Live Tracker — Real-Time Space Visualization

A real-time ISS (International Space Station) tracker that simulates satellite telemetry, visualizes its orbit, and plots the ground track dynamically on a 3D globe 🌍 and 2D map 🗺️.  
Built using **Python**, **Plotly**, and **Dash**.

---

## 🚀 Features

✅ Real-time ISS position and velocity tracking  
✅ 3D globe visualization of orbit  
✅ 2D map viewer for ground track and path  
✅ Automatic telemetry logging (CSV format)  
✅ Modular architecture — easy to extend for other satellites  
✅ Simple, clean UI  

---

## ⚙️ Installation

Make sure you have **Python 3.9+** installed.  
Clone the repository and install the dependencies:

bash
git clone https://github.com/<your-username>/ISS-Live-Tracker.git
cd ISS-Live-Tracker
pip install -r requirements.txt
🧭 Usage
Run the real-time ISS simulation and visualization using the following commands:

🛰️ Step 1 — Start the simulation engine
This script generates live satellite telemetry and updates position data dynamically. 

bash
python ISS_tracker_final.py

Once launched, it will:

Generate real-time ISS position and velocity.

Log telemetry into a timestamped .csv file inside the /data folder.

🌍 Step 2 — Launch the interactive globe & map viewer
To visualize the real-time orbit and ground track:

bash
python map_viewer.py
You’ll see:

A 2D map showing the ground path traced dynamically.

📊 Sample Output
Time (UTC)	Latitude	Longitude	Altitude (km)	Velocity (km/s)
2025-11-03T10:41:00Z	45.12	-73.22	420.55	7.66
2025-11-03T10:42:00Z	46.09	-72.95	420.58	7.66
2025-11-03T10:43:00Z	47.05	-72.68	420.61	7.66

🗂️ CSV logs are saved automatically inside the /data directory for later analysis.

🧠 Project Structure

Copy code
ISS-Live-Tracker/
├── ISS_tracker_final.py     # Core simulation & telemetry generator
├── map_viewer.py            # Visualization dashboard (3D + 2D map)
├── data/                    # Orbit/TLE or sample data
     ├── iss_telemetry.csv   # Telemetry CSV outputs
├── requirements.txt         # Dependencies
└── README.md                # You are here!
🧩 Tech Stack
Python

Plotly / Dash

Pandas

SGP4

Matplotlib

📈 Future Improvements
Integrate real-time NASA / Celestrak API

Add multi-satellite support

Include anomaly detection using AI models

Export orbit visualizations as video

🪐 Credits
Developed by Jenifer Aloysius
For educational and research purposes in Space Situational Awareness & Satellite Tracking.

📜 License
This project is licensed under the MIT License — feel free to use, modify, and share.

👩‍🚀 Author

Jenifer Aloysius
🎓 B.Tech in AI & Data Science | Passionate about SpaceTech & Research
🌌 Exploring how AI can enhance satellite monitoring and prediction

⭐ If you found this project interesting, consider giving it a star! It helps support future open-source work in space tech and AI.
