"""Restricted zone (ROI) management."""

import json
from dataclasses import dataclass, field
from pathlib import Path

import cv2
import numpy as np


@dataclass
class Zone:
    name: str
    polygon: np.ndarray  # shape (N, 2)
    severity: str = "medium"

    def contains_point(self, point: tuple[int, int]) -> bool:
        result = cv2.pointPolygonTest(self.polygon, point, False)
        return result >= 0

    def draw(self, frame: np.ndarray, color: tuple[int, int, int] | None = None) -> None:
        if color is None:
            color = {"high": (0, 0, 255), "medium": (0, 165, 255), "low": (0, 255, 255)}[self.severity]
        overlay = frame.copy()
        cv2.fillPoly(overlay, [self.polygon], (*color, 50))
        cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)
        cv2.polylines(frame, [self.polygon], True, color, 2)
        cv2.putText(frame, self.name, tuple(self.polygon[0]), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)


@dataclass
class ZoneManager:
    zones: list[Zone] = field(default_factory=list)

    @classmethod
    def from_json(cls, path: str | Path) -> "ZoneManager":
        data = json.loads(Path(path).read_text())
        zones = []
        for z in data["zones"]:
            polygon = np.array(z["polygon"], dtype=np.int32)
            zones.append(Zone(name=z["name"], polygon=polygon, severity=z.get("severity", "medium")))
        return cls(zones=zones)

    def check_intrusions(self, point: tuple[int, int]) -> list[Zone]:
        """Returns the zones that contain the given point."""
        return [z for z in self.zones if z.contains_point(point)]

    def draw_all(self, frame: np.ndarray) -> None:
        for zone in self.zones:
            zone.draw(frame)
