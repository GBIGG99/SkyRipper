# SkyRipper 🦅💥

SkyRipper is a **simulated** drone detection and situational awareness showcase for research and education. The project demonstrates how software-defined radio (SDR) tooling, classical signal processing, and lightweight web dashboards can be combined to explore hobbyist airspace monitoring scenarios inside an isolated lab environment.

> ⚠️ **Safety first:** The repository ships with mock assets, replay data, and non-transmitting stubs only. Do **not** attempt to transmit, jam, or otherwise interfere with radio services. Always comply with your local laws and operate inside a shielded test bench.

## Features

- 🔍 **Simulated RTL-SDR pipeline** – The provided scanner replays sample RTL power logs to highlight how burst detection could work without touching real hardware.
- 🧠 **Deterministic classifier** – A tiny Torch model illustrates how spectral snapshots can be categorized for experimentation.
- 🗺️ **Flask + Leaflet dashboard** – Visualize alerts, device telemetry, and sample geolocation overlays from the included dataset.
- 🛡️ **No-TX jammer stub** – `src/jammer_stub.py` documents how a responsible countermeasure loop might be structured while keeping RF transmission disabled.
- 🧪 **Terminal demo** – `src/terminal_demo.py` streams faux detections for quick CLI-only walkthroughs.

## Getting Started

### Requirements

- Python 3.9+ with `pip`
- A POSIX-compatible shell (macOS, Linux, or WSL)
- Optional: `virtualenv` for isolated experiments

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/terminal_demo.py
```

The terminal demo prints a steady stream of simulated detections alongside parsed device sightings. Use it to verify your environment before experimenting with the Flask dashboard.

## Quick Launch Script

```bash
./run.sh
```

The launcher boots the Flask dashboard and simulated scanner in one step. To explore the CLI showcase instead, run `SKYRIPPER_MODE=terminal ./run.sh`.

## Launching the Web Dashboard

```bash
export SKYRIPPER_USE_SIM_DATA=1
python src/web_gui/app.py
```

Then open <http://127.0.0.1:5000> in your browser. The map renders demo detections supplied by the repository.

Want to experiment with real hardware? Explicitly opt in by running `SKYRIPPER_USE_SIM_DATA=0 python src/drone_scanner.py`. The default configuration intentionally sticks to the bundled simulation to keep the project safe for lab-only exploration.

## Project Layout

```
SkyRipper/
├── data/                  # Sample JSONL device feed
├── src/
│   ├── drone_scanner.py   # Simulated RTL power scanner + classifier
│   ├── kismet_parser.py   # Example log ingestion helpers
│   ├── terminal_demo.py   # Console showcase
│   └── web_gui/           # Flask server + Leaflet map
├── config.yaml            # Configuration defaults
├── run.sh                 # Convenience launcher (simulated)
└── install.sh             # Optional dependency helper (no TX tooling)
```

## License

SkyRipper is released under the MIT License – see [`LICENSE`](LICENSE) for details.
