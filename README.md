# 🛰️ Satellite Telemetry Visualization & Logging System

> Real-time satellite telemetry visualizer and logger for space situational awareness.

![Python](https://img.shields.io/badge/Python-3.12%2B-blue)
![Matplotlib](https://img.shields.io/badge/Matplotlib-Data%20Visualization-orange)
![Tkinter](https://img.shields.io/badge/Tkinter-GUI-lightgrey)
![Status](https://img.shields.io/badge/Status-Active-success)

---

## 🚀 Overview

The **Satellite Telemetry Visualization & Logging System** is a Python-based application designed to visualize and monitor real-time satellite data streams.  
It provides an interactive GUI for plotting altitude, velocity, and other telemetry metrics, while also logging data for later analysis.

This project demonstrates how **AI & data science techniques** can be used in **space research and operations**, bridging analytical modeling and visualization.

---

## ✨ Features

- 📡 **Real-Time Telemetry Parsing** – Simulates incoming satellite data streams.  
- 📊 **Dynamic Visualization** – Live plotting using Matplotlib integrated with Tkinter GUI.  
- 💾 **Data Logging** – Saves telemetry data in structured CSV files for analysis.  
- 🧭 **Orbit Parameter Display** – Altitude, velocity, and timestamp tracking in real time.  
- 🌐 **Modular Architecture** – Easily extendable for integration with APIs like CelesTrak or NORAD.

---

## 🧠 Tech Stack

| Component | Technology Used |
|------------|----------------|
| Language | Python |
| GUI | Tkinter |
| Plotting | Matplotlib |
| Data Handling | Pandas, NumPy |
| Logging | CSV-based persistent storage |

---

## 🧩 Project Structure
📁 solar_flare_forecaster/
│
├── main.py # Entry point for GUI and visualization
├── telemetry_generator.py # Simulates satellite data
├── telemetry_plotter.py # Handles Matplotlib live plotting
├── data_logger.py # Logs telemetry to CSV
├── utils.py # Helper functions
├── requirements.txt # Dependencies
└── README.md # You’re reading it :)


---

## ⚙️ Installation

bash
# Clone the repository
git clone https://github.com/JeniAloysius/Satellite-Telemetry-Visualization-Logging-System.git

# Navigate into the project
cd Satellite-Telemetry-Visualization-Logging-System

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # or on Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

🧭 Usage
python main.py

Once the app launches:
Click Start Simulation to generate satellite data.
Watch live telemetry plots update in real-time.
Data is automatically logged to data_logs/telemetry.csv.


📜 License

This project is released under the MIT License.

👩‍🚀 Author

Jenifer Aloysius
🎓 B.Tech in AI & Data Science | Passionate about SpaceTech & Research
🌌 Exploring how AI can enhance satellite monitoring and prediction
🔗 LinkedIn
 · GitHub

⭐ If you found this project interesting, consider giving it a star! It helps support future open-source work in space tech and AI.
