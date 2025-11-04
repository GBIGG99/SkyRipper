"""Simulated RTL-SDR burst scanner for the SkyRipper demo environment."""

from __future__ import annotations

import os
import subprocess
import time
from typing import Iterator

import numpy as np
import requests

try:
    import torch
    from torch import nn
except ModuleNotFoundError:  # pragma: no cover - optional dependency for the demo
    torch = None  # type: ignore[assignment]
    nn = None  # type: ignore[assignment]


if torch is not None:

    class _TorchDroneCNN(nn.Module):
        """Original Torch architecture for loading the checkpoint."""

        def __init__(self) -> None:
            super().__init__()
            self.conv = nn.Sequential(
                nn.Conv1d(1, 16, 3),
                nn.ReLU(),
                nn.Conv1d(16, 32, 3),
                nn.ReLU(),
                nn.AdaptiveAvgPool1d(1),
            )
            self.fc = nn.Linear(32, 2)

        def forward(self, x: torch.Tensor) -> torch.Tensor:  # type: ignore[override]
            if x.ndim == 1:
                x = x.unsqueeze(0)
            x = x.unsqueeze(1)
            features = self.conv(x).squeeze(-1)
            return self.fc(features)
else:

    class _TorchDroneCNN:  # type: ignore[too-many-ancestors]
        """Stub used when Torch is missing."""

        def __call__(self, _: np.ndarray) -> np.ndarray:
            raise RuntimeError("Torch is required for CNN inference")

ALERT_THRESHOLD_DBM = -50.0
MODEL_PATH = "models/drone_burst_cnn.pth"
SIM_SPECTRUM_LENGTH = 128
SIM_INTERVAL_SECONDS = 1.5


class DroneCNN:
    """CNN wrapper that becomes a stub when Torch is unavailable."""

    def __init__(self) -> None:
        self.model = _TorchDroneCNN() if torch is not None else None

    def load_state(self, path: str) -> None:
        if torch is None or self.model is None:
            return
        state = torch.load(path, map_location="cpu")
        self.model.load_state_dict(state)
        self.model.eval()

    def predict(self, spectrum: np.ndarray) -> bool:
        """Return True when the spectrum resembles a drone burst."""

        peak_power = float(np.max(spectrum))
        if torch is None or self.model is None:
            return peak_power > ALERT_THRESHOLD_DBM

        tensor = torch.tensor(spectrum[:100], dtype=torch.float32)
        logits = self.model(tensor).squeeze(0)
        return bool(int(logits.argmax().item()) == 1 and peak_power > ALERT_THRESHOLD_DBM)


def load_model(path: str = MODEL_PATH) -> DroneCNN:
    """Load the bundled Torch model when available."""

    model = DroneCNN()
    if torch is None:
        print("[!] Torch not available – using threshold-based classifier")
        return model
    try:
        model.load_state(path)
    except FileNotFoundError:
        print("[!] Model checkpoint missing – falling back to threshold detection")
    return model


def iter_simulated_spectra(
    length: int = SIM_SPECTRUM_LENGTH,
    interval: float = SIM_INTERVAL_SECONDS,
) -> Iterator[np.ndarray]:
    """Yield synthetic spectra that occasionally contain a strong burst."""

    rng = np.random.default_rng()
    baseline = np.linspace(-85.0, -80.0, length, dtype=np.float32)
    while True:
        noise = baseline + rng.normal(0.0, 1.5, size=length).astype(np.float32)
        if rng.random() < 0.35:
            centre = rng.integers(10, length - 10)
            width = rng.integers(3, 8)
            amplitude = rng.uniform(20.0, 35.0)
            start = max(0, centre - width)
            stop = min(length, centre + width)
            noise[start:stop] += amplitude * np.hanning(stop - start)
        yield noise
        time.sleep(interval)


def parse_rtl_power_line(line: str) -> np.ndarray | None:
    """Parse a single rtl_power CSV row into a float array."""

    if "2400" not in line:
        return None
    parts = line.split()
    if len(parts) < 7:
        return None
    try:
        return np.array([float(value) for value in parts[6:]], dtype=np.float32)
    except ValueError:
        return None


def post_alert(freqs: np.ndarray, model: DroneCNN) -> None:
    """Send an alert to the Flask API when a drone burst is detected."""

    if freqs.size < 100:
        return
    if not model.predict(freqs):
        return

    peak_index = int(np.argmax(freqs))
    peak_power = float(np.max(freqs))
    alert = {
        "type": "DRONE_BURST",
        "freq": f"{2400 + peak_index * 0.1:.1f}MHz",
        "power": f"{peak_power:.1f}dBm",
        "time": time.time(),
    }

    try:
        requests.post("http://localhost:5000/api/alert", json=alert, timeout=2)
    except requests.RequestException:
        pass


def simulation_loop(model: DroneCNN) -> None:
    """Continuously generate synthetic spectra and emit alerts."""

    for spectrum in iter_simulated_spectra():
        post_alert(spectrum, model)


def hardware_loop(model: DroneCNN) -> None:
    """Attempt to read rtl_power output and emit alerts if bursts are detected."""

    cmd = [
        "rtl_power",
        "-f",
        "2400M:2483M:100k",
        "-g",
        "50",
        "-i",
        "0.25",
        "-1",
        "-",
    ]
    try:
        with subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True) as proc:
            if proc.stdout is None:
                return
            for line in proc.stdout:
                freqs = parse_rtl_power_line(line)
                if freqs is None:
                    continue
                post_alert(freqs, model)
    except FileNotFoundError:
        print("[!] rtl_power not found – falling back to simulation loop")
        simulation_loop(model)


def scan_loop() -> None:
    """Run the scanner using simulation by default."""

    model = load_model()
    use_sim = os.getenv("SKYRIPPER_USE_SIM_DATA", "1") != "0"
    if use_sim:
        print("[+] SkyRipper scanner running in simulation mode")
        simulation_loop(model)
    else:
        print("[+] SkyRipper scanner attempting rtl_power capture")
        hardware_loop(model)


if __name__ == "__main__":
    scan_loop()
