"""Utility helpers for working with Kismet JSON exports."""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Iterator, List, Optional


@dataclass
class KismetDevice:
    mac: str
    ssid: Optional[str]
    lat: Optional[float]
    lon: Optional[float]
    last_seen: float

    def as_dict(self) -> Dict[str, Optional[float]]:
        return asdict(self)


class KismetParser:
    """Parses newline-delimited JSON exported from Kismet."""

    def __init__(self, data_path: Path | str) -> None:
        self.data_path = Path(data_path)

    def _parse_timestamp(self, raw: object) -> float:
        if isinstance(raw, (int, float)):
            return float(raw)
        if isinstance(raw, str):
            try:
                return time.mktime(time.strptime(raw.split("+", 1)[0], "%Y-%m-%dT%H:%M:%SZ"))
            except ValueError:
                pass
        return time.time()

    def _parse_line(self, line: str) -> Optional[KismetDevice]:
        if not line.strip():
            return None
        payload = json.loads(line)
        return KismetDevice(
            mac=payload.get("mac", ""),
            ssid=payload.get("ssid"),
            lat=payload.get("lat"),
            lon=payload.get("lon"),
            last_seen=self._parse_timestamp(payload.get("last_seen")),
        )

    def iter_devices(self) -> Iterator[KismetDevice]:
        if not self.data_path.exists():
            return iter(())
        with self.data_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                device = self._parse_line(line)
                if device:
                    yield device

    def latest(self, stale_after_seconds: int = 300) -> List[Dict[str, Optional[float]]]:
        now = time.time()
        return [
            device.as_dict()
            for device in self.iter_devices()
            if now - device.last_seen <= stale_after_seconds
        ]


__all__ = ["KismetDevice", "KismetParser"]
