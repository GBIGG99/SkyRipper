"""Simulated RF burst scanner for the SkyRipper demo application."""
from __future__ import annotations

import argparse
import json
import math
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Generator, Iterable, List, Optional

import numpy as np
import yaml


@dataclass
class Detection:
    """Represents a single RF detection event."""

    timestamp: float
    frequency_mhz: float
    power_dbm: float
    confidence: float
    classifier: str

    def as_dict(self) -> Dict[str, float]:
        return asdict(self)


class PlaceholderClassifier:
    """Deterministic classifier that emulates a trained CNN.

    The goal is not to achieve high accuracy but to provide a reproducible
    confidence score for the web demo without shipping a heavyweight model.
    """

    def __init__(self, model_path: Path, min_confidence: float, threshold_dbm: float) -> None:
        self.model_path = model_path
        self.min_confidence = min_confidence
        self.threshold_dbm = threshold_dbm
        self.model_available = model_path.is_file() and model_path.read_text().strip() != ""

    def score(self, frequency_mhz: float, power_dbm: float) -> float:
        normalized_strength = max(0.0, min(1.0, (power_dbm - self.threshold_dbm + 10.0) / 20.0))
        harmonic = 0.5 + 0.5 * math.sin(frequency_mhz / 25.0)
        confidence = 0.35 * normalized_strength + 0.45 * harmonic + 0.2 * (1.0 if self.model_available else 0.5)
        return max(0.0, min(1.0, confidence))

    def classify(self, frequency_mhz: float, power_dbm: float) -> Optional[Detection]:
        confidence = self.score(frequency_mhz, power_dbm)
        if confidence < self.min_confidence:
            return None
        return Detection(
            timestamp=time.time(),
            frequency_mhz=frequency_mhz,
            power_dbm=power_dbm,
            confidence=confidence,
            classifier="placeholder-cnn" if self.model_available else "deterministic-fallback",
        )


class BurstGenerator:
    """Generates synthetic burst measurements around a center frequency."""

    def __init__(self, center_frequency_mhz: float, threshold_dbm: float) -> None:
        self.center_frequency_mhz = center_frequency_mhz
        self.threshold_dbm = threshold_dbm
        self.rng = np.random.default_rng(seed=4242)

    def sample(self, count: int) -> Iterable[Dict[str, float]]:
        for _ in range(count):
            offset = self.rng.normal(loc=0.0, scale=6.0)
            frequency = self.center_frequency_mhz + offset
            noise_floor = self.threshold_dbm - 15.0 + self.rng.normal(scale=3.0)
            burst_power = noise_floor + abs(offset) * 0.8 + self.rng.lognormal(mean=3.0, sigma=0.2)
            yield {
                "frequency_mhz": frequency,
                "power_dbm": burst_power,
            }


class DroneScanner:
    """High-level orchestrator that emulates the RTL-SDR + classifier pipeline."""

    def __init__(self, config_path: Path | str) -> None:
        self.config_path = Path(config_path)
        with self.config_path.open("r", encoding="utf-8") as handle:
            self.config = yaml.safe_load(handle)

        scanner_cfg = self.config.get("scanner", {})
        classifier_cfg = self.config.get("classifier", {})

        self.threshold_dbm = float(scanner_cfg.get("threshold_dbm", -50.0))
        center_frequency = float(scanner_cfg.get("center_frequency_mhz", 2442.0))
        self.generator = BurstGenerator(center_frequency, self.threshold_dbm)

        model_path = Path(classifier_cfg.get("model_path", "models/drone_burst_cnn.pth"))
        min_confidence = float(classifier_cfg.get("min_confidence", 0.5))
        self.classifier = PlaceholderClassifier(model_path, min_confidence, self.threshold_dbm)

    def scan_once(self, batch_size: int = 16) -> List[Detection]:
        detections: List[Detection] = []
        for burst in self.generator.sample(batch_size):
            detection = self.classifier.classify(burst["frequency_mhz"], burst["power_dbm"])
            if detection:
                detections.append(detection)
        return detections

    def stream(self, interval_seconds: float = 3.0, batch_size: int = 16) -> Generator[List[Detection], None, None]:
        """Continuously yield detection batches."""

        while True:
            yield self.scan_once(batch_size=batch_size)
            time.sleep(interval_seconds)

    def latest(self, limit: int = 10) -> List[Dict[str, float]]:
        """Produce a JSON-serializable list of detection dictionaries."""

        results: List[Dict[str, float]] = []
        for detection in self.scan_once(batch_size=limit * 2):
            results.append(detection.as_dict())
            if len(results) >= limit:
                break
        return results


def _format_detections(detections: List[Dict[str, float]]) -> str:
    return json.dumps(detections, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a simulated RF scan and print detections.")
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to the SkyRipper configuration file (default: config.yaml)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum number of detections to emit (default: 10)",
    )
    args = parser.parse_args()

    scanner = DroneScanner(args.config)
    detections = scanner.latest(limit=args.limit)
    print(_format_detections(detections))


if __name__ == "__main__":
    main()


__all__ = ["Detection", "DroneScanner", "main"]
