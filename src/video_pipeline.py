"""Main video pipeline for intrusion detection."""

import argparse
import time

import cv2

from .alert_manager import AlertManager
from .detector import PersonDetector
from .utils import draw_detections, draw_stats
from .zone_manager import ZoneManager


class VideoPipeline:
    def __init__(
        self,
        source: str | int,
        zones_path: str,
        model_name: str = "yolov8n.pt",
        confidence: float = 0.5,
        alert_cooldown: float = 5.0,
        display: bool = True,
    ):
        self.source = int(source) if str(source).isdigit() else source
        self.detector = PersonDetector(model_name=model_name, confidence=confidence)
        self.zone_manager = ZoneManager.from_json(zones_path)
        self.alert_manager = AlertManager(cooldown_seconds=alert_cooldown)
        self.display = display

    def run(self) -> None:
        cap = cv2.VideoCapture(self.source)
        if not cap.isOpened():
            raise RuntimeError(f"Could not open video: {self.source}")

        print(f"[INFO] Source: {self.source}")
        print(f"[INFO] Resolution: {int(cap.get(3))}x{int(cap.get(4))}")
        print(f"[INFO] Zones loaded: {len(self.zone_manager.zones)}")
        print("[INFO] Press 'q' to quit\n")

        prev_time = time.time()

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Calculate FPS
            curr_time = time.time()
            fps = 1.0 / max(curr_time - prev_time, 1e-6)
            prev_time = curr_time

            # Detect people
            detections = self.detector.detect(frame)

            # Check intrusions
            intruders: dict[int, list] = {}
            for i, det in enumerate(detections):
                violated_zones = self.zone_manager.check_intrusions(det.bottom_center)
                if violated_zones:
                    intruders[i] = violated_zones
                    for zone in violated_zones:
                        self.alert_manager.trigger(zone.name, zone.severity, det.confidence, frame)

            # Draw
            self.zone_manager.draw_all(frame)
            draw_detections(frame, detections, intruders)
            draw_stats(frame, len(detections), len(intruders), fps)

            if self.display:
                cv2.imshow("Outsider - Intrusion Detection", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

        cap.release()
        if self.display:
            cv2.destroyAllWindows()
        print("\n[INFO] Pipeline finished.")

    def process_frame(self, frame):
        """Process a single frame and return the annotated frame + metadata.

        Useful for Colab / notebook integration.
        """
        detections = self.detector.detect(frame)

        intruders: dict[int, list] = {}
        alerts = []
        for i, det in enumerate(detections):
            violated_zones = self.zone_manager.check_intrusions(det.bottom_center)
            if violated_zones:
                intruders[i] = violated_zones
                for zone in violated_zones:
                    alert = self.alert_manager.trigger(zone.name, zone.severity, det.confidence, frame)
                    if alert:
                        alerts.append(alert)

        self.zone_manager.draw_all(frame)
        draw_detections(frame, detections, intruders)
        draw_stats(frame, len(detections), len(intruders), 0)

        return frame, {
            "detections": len(detections),
            "intruders": len(intruders),
            "alerts": alerts,
        }


def main():
    parser = argparse.ArgumentParser(description="Outsider - Video Intrusion Detection")
    parser.add_argument("--source", required=True, help="Path to video, RTSP URL, or 0 for webcam")
    parser.add_argument("--zones", required=True, help="Path to zones JSON file")
    parser.add_argument("--model", default="yolov8n.pt", help="YOLOv8 model (default: yolov8n.pt)")
    parser.add_argument("--confidence", type=float, default=0.5, help="Confidence threshold (default: 0.5)")
    parser.add_argument("--cooldown", type=float, default=5.0, help="Cooldown between alerts in seconds")
    parser.add_argument("--no-display", action="store_true", help="Disable display window")
    args = parser.parse_args()

    pipeline = VideoPipeline(
        source=args.source,
        zones_path=args.zones,
        model_name=args.model,
        confidence=args.confidence,
        alert_cooldown=args.cooldown,
        display=not args.no_display,
    )
    pipeline.run()


if __name__ == "__main__":
    main()
