#!/usr/bin/env bash
set -euo pipefail

if [[ ! -d .venv ]]; then
  echo "[SkyRipper] Virtual environment not found. Please run ./install.sh first." >&2
  exit 1
fi

source .venv/bin/activate
export FLASK_APP=src.web_gui.app
export SKYRIPPER_CONFIG=${SKYRIPPER_CONFIG:-config.yaml}

exec python -m flask run --host=0.0.0.0 --port=5000
