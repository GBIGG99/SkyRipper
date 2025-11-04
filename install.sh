#!/usr/bin/env bash
set -euo pipefail

# SkyRipper installer: sets up a local Python virtual environment and installs dependencies.
# The script is intentionally lightweight so that it can run on Debian-based systems
# without requiring privileged operations beyond package metadata refreshes.

if [[ ${EUID:-$(id -u)} -eq 0 ]]; then
  echo "[SkyRipper] Running as root. Continuing without sudo." >&2
  SUDO=""
else
  SUDO="sudo"
fi

# Refresh package metadata so python3-venv is available when apt-get exists.
if command -v apt-get >/dev/null 2>&1; then
  if [[ ${SKYRIPPER_SKIP_APT:-0} -eq 1 ]]; then
    echo "[SkyRipper] Skipping apt-get steps due to SKYRIPPER_SKIP_APT=1." >&2
  else
    $SUDO apt-get update -y
    $SUDO apt-get install -y python3 python3-venv python3-pip
  fi
else
  echo "[SkyRipper] apt-get not found. Please ensure Python 3, venv, and pip are installed." >&2
fi

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi

source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "[SkyRipper] Installation complete. Activate the environment with 'source .venv/bin/activate'."
