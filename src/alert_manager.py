"""Alert system for detected intrusions."""

import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np


@dataclass
class Alert:
    zone_name: str
    severity: str
    timestamp: str
    confidence: float
    snapshot_path: str | None = None


@dataclass
class AlertManager:
    output_dir: Path = field(default_factory=lambda: Path("alerts"))
    cooldown_seconds: float = 5.0
    _last_alert_time: dict[str, float] = field(default_factory=dict, repr=False)

    def __post_init__(self):
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def should_alert(self, zone_name: str) -> bool:
        last = self._last_alert_time.get(zone_name, 0)
        return (time.time() - last) >= self.cooldown_seconds

    def trigger(self, zone_name: str, severity: str, confidence: float, frame: np.ndarray) -> Alert | None:
        if not self.should_alert(zone_name):
            return None

        self._last_alert_time[zone_name] = time.time()
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        filename = f"alert_{zone_name.replace(' ', '_')}_{now.strftime('%Y%m%d_%H%M%S')}.jpg"
        snapshot_path = str(self.output_dir / filename)
        cv2.imwrite(snapshot_path, frame)

        alert = Alert(
            zone_name=zone_name,
            severity=severity,
            timestamp=timestamp,
            confidence=confidence,
            snapshot_path=snapshot_path,
        )
        self._log(alert)
        return alert

    def _log(self, alert: Alert) -> None:
        icon = {"high": "!!!", "medium": "!!", "low": "!"}[alert.severity]
        print(f"[ALERT {icon}] {alert.timestamp} | Zone: {alert.zone_name} | "
              f"Severity: {alert.severity} | Confidence: {alert.confidence:.2f} | "
              f"Snapshot: {alert.snapshot_path}")
