"""General utilities."""

import cv2
import numpy as np

from .detector import Detection
from .zone_manager import Zone


def draw_detections(frame: np.ndarray, detections: list[Detection], intruders: dict[int, list[Zone]]) -> None:
    """Draw bounding boxes and mark intruders in red."""
    for i, det in enumerate(detections):
        x1, y1, x2, y2 = det.bbox
        is_intruder = i in intruders
        color = (0, 0, 255) if is_intruder else (0, 255, 0)
        label = f"INTRUDER {det.confidence:.0%}" if is_intruder else f"Person {det.confidence:.0%}"

        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.circle(frame, det.bottom_center, 5, color, -1)

        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(frame, (x1, y1 - th - 8), (x1 + tw, y1), color, -1)
        cv2.putText(frame, label, (x1, y1 - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)


def draw_stats(frame: np.ndarray, total: int, intruders_count: int, fps: float) -> None:
    """Draw stats in the top-left corner."""
    stats = [
        f"FPS: {fps:.1f}",
        f"People: {total}",
        f"Intruders: {intruders_count}",
    ]
    for i, text in enumerate(stats):
        color = (0, 0, 255) if "Intruders" in text and intruders_count > 0 else (255, 255, 255)
        cv2.putText(frame, text, (10, 30 + i * 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
