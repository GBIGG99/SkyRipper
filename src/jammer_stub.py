"""A non-transmitting jammer stub used for educational purposes."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

import yaml

logger = logging.getLogger(__name__)


@dataclass
class JammerConfig:
    hop_frequencies_mhz: List[float]
    dwell_time_ms: int
    legal_notice: str


class JammerStub:
    """Logs the channels that would be jammed instead of transmitting."""

    def __init__(self, config_path: Path | str) -> None:
        config_data = yaml.safe_load(Path(config_path).read_text(encoding="utf-8"))
        jammer_cfg = config_data.get("jammer", {})
        self.config = JammerConfig(
            hop_frequencies_mhz=[float(f) for f in jammer_cfg.get("hop_frequencies_mhz", [2420.0, 2440.0, 2460.0])],
            dwell_time_ms=int(jammer_cfg.get("dwell_time_ms", 250)),
            legal_notice=jammer_cfg.get("legal_notice", "Transmission is disabled in the demo environment."),
        )
        logger.info("Jammer stub initialized – transmission is permanently disabled.")
        logger.info("Legal notice: %s", self.config.legal_notice)

    def plan_hops(self) -> Iterable[str]:
        for frequency in self.config.hop_frequencies_mhz:
            yield f"Would hop to {frequency:.3f} MHz for {self.config.dwell_time_ms} ms"

    def run(self) -> None:
        for message in self.plan_hops():
            logger.info(message)
        logger.info("End of hop plan. No RF hardware was activated.")


__all__ = ["JammerStub"]
