"""Person detection using YOLOv8."""

from dataclasses import dataclass

import numpy as np
from ultralytics import YOLO


PERSON_CLASS_ID = 0  # COCO class id for "person"


@dataclass
class Detection:
    bbox: tuple[int, int, int, int]  # x1, y1, x2, y2
    confidence: float
    center: tuple[int, int]

    @property
    def bottom_center(self) -> tuple[int, int]:
        """Bottom center point (feet), more accurate for zone checking."""
        x1, y1, x2, y2 = self.bbox
        return ((x1 + x2) // 2, y2)


class PersonDetector:
    def __init__(self, model_name: str = "yolov8n.pt", confidence: float = 0.5):
        self.model = YOLO(model_name)
        self.confidence = confidence

    def detect(self, frame: np.ndarray) -> list[Detection]:
        results = self.model(frame, conf=self.confidence, classes=[PERSON_CLASS_ID], verbose=False)
        detections = []
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                conf = float(box.conf[0])
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                detections.append(Detection(
                    bbox=(x1, y1, x2, y2),
                    confidence=conf,
                    center=(cx, cy),
                ))
        return detections
