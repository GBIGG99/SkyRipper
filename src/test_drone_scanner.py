"""Tests for the drone_scanner module."""
import unittest
from unittest.mock import patch
from pathlib import Path

from src.drone_scanner import DroneScanner, Detection


class DroneScannerTest(unittest.TestCase):
    def setUp(self):
        """Set up a dummy config for testing."""
        self.config_path = Path("test_config.yaml")
        with self.config_path.open("w", encoding="utf-8") as f:
            f.write(
                """
                scanner:
                  threshold_dbm: -50.0
                  center_frequency_mhz: 2442.0
                classifier:
                  model_path: "models/drone_burst_cnn.pth"
                  min_confidence: 0.95
                """
            )
        self.scanner = DroneScanner(self.config_path)

    def tearDown(self):
        """Clean up the dummy config file."""
        if self.config_path.exists():
            self.config_path.unlink()

    @patch("src.drone_scanner.DroneScanner.scan_once")
    def test_latest_gathers_enough_detections(self, mock_scan_once):
        """Verify that the latest method retries until the limit is reached."""
        # Simulate scan_once returning results in chunks
        mock_scan_once.side_effect = [
            [Detection(1, 1, 1, 1, "test")],
            [Detection(2, 2, 2, 2, "test"), Detection(3, 3, 3, 3, "test")],
            [Detection(4, 4, 4, 4, "test"), Detection(5, 5, 5, 5, "test")],
        ]

        limit = 5
        detections = self.scanner.latest(limit=limit)
        self.assertEqual(len(detections), limit)
        self.assertEqual(mock_scan_once.call_count, 3)

    @patch("src.drone_scanner.DroneScanner.scan_once")
    def test_latest_returns_up_to_limit(self, mock_scan_once):
        """Verify that the latest method respects the limit and doesn't overshoot."""
        # Simulate scan_once returning more than enough results at once
        mock_scan_once.return_value = [Detection(i, i, i, i, "test") for i in range(10)]

        limit = 5
        detections = self.scanner.latest(limit=limit)
        self.assertEqual(len(detections), limit)
        mock_scan_once.assert_called_once()

    @patch("src.drone_scanner.DroneScanner.scan_once")
    def test_latest_handles_no_detections(self, mock_scan_once):
        """Verify that latest exits after max_retries if no detections are found."""
        # Simulate scan_once never returning detections
        mock_scan_once.return_value = []

        limit = 5
        max_retries = 3
        # This test will fail until the max_retries logic is implemented
        detections = self.scanner.latest(limit=limit, max_retries=max_retries)
        self.assertEqual(len(detections), 0)
        self.assertEqual(mock_scan_once.call_count, max_retries)


if __name__ == "__main__":
    unittest.main()
