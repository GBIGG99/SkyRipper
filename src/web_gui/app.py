"""Flask web interface for the SkyRipper demo."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict

from flask import Flask, jsonify, render_template
import yaml

from ..drone_scanner import DroneScanner
from ..kismet_parser import KismetParser


def _load_config(config_path: Path) -> Dict[str, Any]:
    with config_path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def create_app() -> Flask:
    config_path = Path(os.environ.get("SKYRIPPER_CONFIG", "config.yaml"))
    config = _load_config(config_path)

    scanner = DroneScanner(config_path)
    kismet_cfg = config.get("kismet", {})
    parser = KismetParser(kismet_cfg.get("data_path", "data/kismet_devices.jsonl"))
    stale_after = int(kismet_cfg.get("stale_after_seconds", 300))

    geo_cfg = config.get("geo", {})
    default_geo = {
        "lat": float(geo_cfg.get("default_latitude", 0.0)),
        "lon": float(geo_cfg.get("default_longitude", 0.0)),
        "radius": float(geo_cfg.get("alert_radius_m", 250.0)),
    }

    app = Flask(__name__, template_folder="templates", static_folder="static")

    @app.get("/")
    def index() -> str:
        return render_template("index.html", default_geo=default_geo)

    @app.get("/api/detections")
    def api_detections():
        return jsonify({"detections": scanner.latest(limit=15)})

    @app.get("/api/kismet")
    def api_kismet():
        return jsonify({"devices": parser.latest(stale_after_seconds=stale_after)})

    @app.get("/api/health")
    def api_health():
        return jsonify({"status": "ok", "config": {"geo": default_geo}})

    return app


app = create_app()


__all__ = ["create_app", "app"]
