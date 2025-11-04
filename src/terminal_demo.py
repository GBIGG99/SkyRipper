"""Terminal-only monitor for the SkyRipper demo environment."""
from __future__ import annotations

import argparse
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List

import yaml

from .drone_scanner import DroneScanner
from .kismet_parser import KismetParser


def _load_config(config_path: Path) -> Dict[str, object]:
    with config_path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _format_timestamp(epoch_seconds: float) -> str:
    return datetime.fromtimestamp(epoch_seconds).strftime("%H:%M:%S")


def _render_section(title: str, lines: Iterable[str]) -> str:
    banner = f"=== {title} ==="
    body = "\n".join(lines) if lines else "(none)"
    return f"{banner}\n{body}\n"


def run_terminal_monitor(
    scanner: DroneScanner,
    kismet_parser: KismetParser,
    stale_after_seconds: int,
    interval_seconds: float,
    iterations: int,
    clear_screen: bool,
) -> None:
    iteration_count = 0
    while True:
        detections = scanner.latest(limit=8)
        devices = kismet_parser.latest(stale_after_seconds=stale_after_seconds)

        if clear_screen:
            sys.stdout.write("\033[2J\033[H")

        print("SkyRipper Terminal Monitor (simulated data)")
        print(time.strftime("%Y-%m-%d %H:%M:%S"))

        detection_lines: List[str] = [
            f"{_format_timestamp(item['timestamp'])} | "
            f"{item['frequency_mhz']:7.2f} MHz | "
            f"{item['power_dbm']:6.1f} dBm | "
            f"{item['confidence'] * 100:5.1f}%"
            for item in detections
        ]

        device_lines: List[str] = [
            f"{entry.get('mac', '??:??:??:??:??:??')} | "
            f"{entry.get('ssid') or '(hidden)'} | "
            f"last seen {_format_timestamp(entry.get('last_seen', time.time()))}"
            for entry in devices
        ]

        print(_render_section("Detections", detection_lines))
        print(_render_section("Kismet Devices", device_lines))

        iteration_count += 1
        if iterations and iteration_count >= iterations:
            break

        time.sleep(interval_seconds)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Stream simulated SkyRipper detections to the terminal.",
    )
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to the SkyRipper configuration file (default: config.yaml)",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=3.0,
        help="Seconds to wait between refreshes (default: 3.0)",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=0,
        help="Number of refresh cycles to run before exiting (default: infinite)",
    )
    parser.add_argument(
        "--no-clear",
        action="store_true",
        help="Disable clearing the terminal between refreshes.",
    )
    args = parser.parse_args()

    config_path = Path(args.config)
    config = _load_config(config_path)

    scanner = DroneScanner(config_path)
    kismet_cfg = config.get("kismet", {}) if isinstance(config, dict) else {}
    data_path = kismet_cfg.get("data_path", "data/kismet_devices.jsonl")
    stale_after_seconds = int(kismet_cfg.get("stale_after_seconds", 300))
    kismet_parser = KismetParser(data_path)

    run_terminal_monitor(
        scanner=scanner,
        kismet_parser=kismet_parser,
        stale_after_seconds=stale_after_seconds,
        interval_seconds=args.interval,
        iterations=args.iterations,
        clear_screen=not args.no_clear,
    )


if __name__ == "__main__":
    main()


__all__ = ["run_terminal_monitor", "main"]
