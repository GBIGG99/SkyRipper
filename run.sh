#!/bin/bash
# SkyRipper launcher script for the simulated demo environment.
# Defaults to the safe, GUI-driven workflow documented in the README.
set -euo pipefail

MODE="${SKYRIPPER_MODE:-gui}"

if [[ "${MODE}" == "terminal" ]]; then
    echo "[+] SkyRipper terminal showcase"
    exec python3 src/terminal_demo.py
fi

export SKYRIPPER_USE_SIM_DATA="${SKYRIPPER_USE_SIM_DATA:-1}"

echo "[+] Starting SkyRipper Flask dashboard (simulation mode)"
python3 src/web_gui/app.py &
APP_PID=$!
trap 'kill ${APP_PID} >/dev/null 2>&1 || true' EXIT

sleep 1
echo "[+] Launching simulated scanner"
python3 src/drone_scanner.py
