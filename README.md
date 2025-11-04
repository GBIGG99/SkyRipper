
SkyRipper is a demonstration toolkit that showcases how radio-frequency telemetry, Wi-Fi device tracking, and a simple web dashboard can be combined to monitor drone activity. The project is intentionally designed for educational purposes and **does not transmit or jam any signals**. All SDR and classification components are simulated to make the codebase safe to run on commodity hardware without any external equipment.

## Features

- **RF burst scanner** – Emulates RTL-SDR spectrum sweeps and applies a rolling threshold detector to highlight suspicious transmissions.
- **Burst classifier** – Loads a placeholder CNN checkpoint (or a deterministic fallback) to score signal bursts as drone-like or benign.
- **Kismet parser** – Streams sightings from a newline-delimited JSON export to correlate MAC addresses with RF hits.
- **Flask web UI** – Displays detections on a Leaflet map and serves JSON APIs for integrations.
- **Self-contained installer** – Creates a Python virtual environment and installs dependencies with a single command.

## Quick start

```bash
# 1. Install dependencies (creates .venv)
#    Set `SKYRIPPER_SKIP_APT=1` if you prefer to manage system packages yourself.
./install.sh

# 2. Launch the dashboard
./run.sh

# 3. (Optional) Print a batch of simulated detections to the console
source .venv/bin/activate
python -m src.drone_scanner --limit 5
```

The web interface will be available at <http://127.0.0.1:5000>. Because the RF scanner is simulated, detections will cycle through deterministic demo data. If you want to experiment with your own data, edit `config.yaml` and drop newline-delimited JSON entries into `data/kismet_devices.jsonl`.

## Project layout

```
SkyRipper/
├── install.sh              # Virtual environment bootstrapper
├── run.sh                  # Convenience launcher for the Flask UI
├── config.yaml             # Runtime configuration (frequencies, thresholds, geo fences)
├── requirements.txt        # Python dependencies
├── data/                   # Sample Kismet export
├── models/
│   └── drone_burst_cnn.pth # Placeholder checkpoint (text stub)
├── sigdigger/
│   └── SigDigger.AppImage  # Placeholder reference to external spectrum tool
└── src/
    ├── drone_scanner.py    # RF scan + classification pipeline
    ├── jammer_stub.py      # Explicitly non-transmitting jammer placeholder
    ├── kismet_parser.py    # Kismet export ingestion helpers
    └── web_gui/
        ├── app.py          # Flask application factory
        ├── templates/
        │   └── index.html
        └── static/js/
            └── map.js
```

## Safety notice

The repository does **not** contain any transmission-capable code. `jammer_stub.py` logs the channels that would be targeted but never opens or drives RF hardware. The intent is to encourage responsible research, signal visualization, and security hardening.

## License

This project is released under the MIT License. See [LICENSE](LICENSE) for details.
