# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the pipeline
python -m src.video_pipeline --source video.mp4 --zones configs/zones.json
python -m src.video_pipeline --source rtsp://ip:port/stream --zones configs/zones.json
python -m src.video_pipeline --source 0 --zones configs/zones.json  # webcam

# Run tests
python -m pytest
python -m pytest tests/test_zones.py  # single test file
```

### Pipeline arguments
| Argument | Default | Description |
|---|---|---|
| `--source` | required | Video file path, RTSP URL, or `0` for webcam |
| `--zones` | required | Path to zones JSON config |
| `--model` | `yolov8n.pt` | YOLOv8 model variant |
| `--confidence` | `0.5` | Detection confidence threshold |
| `--cooldown` | `5.0` | Alert cooldown in seconds |
| `--no-display` | false | Disable OpenCV window (for headless/Colab) |

## Architecture

The system detects persons entering restricted polygon zones in video streams.

**Data flow:**
```
Video Input → VideoPipeline → PersonDetector → ZoneManager → AlertManager → alerts/ dir
```

**Modules:**
- `detector.py` — YOLOv8 inference (COCO class 0 = person); returns `Detection` dataclass with `bottom_center` (feet position used for zone checking)
- `zone_manager.py` — Polygon-based restricted zones loaded from JSON; each zone has name, polygon coords, and severity (`high`/`medium`/`low`); uses `cv2.pointPolygonTest`
- `alert_manager.py` — Cooldown-based alert trigger; saves snapshots to `alerts/` directory; returns `Alert` dataclass
- `video_pipeline.py` — Orchestrator; two modes: `run()` for live display, `process_frame()` for single-frame (Colab/notebook use)
- `utils.py` — Drawing helpers for bounding boxes and HUD stats

**Zone config format** (`configs/zones.json`):
```json
{
  "zones": [
    {
      "name": "Zone A",
      "polygon": [[x1,y1], [x2,y2], [x3,y3], [x4,y4]],
      "severity": "high"
    }
  ]
}
```
Severity color coding: `high` → red, `medium` → orange, `low` → cyan.

**Colab compatibility:** Use `--no-display` flag and call `process_frame()` directly in the notebook (`outsider_colab.ipynb`). Use `opencv-python-headless` instead of `opencv-python` in cloud environments.
