<div align="center">
  
<img src="./public/logo.png" width="200" height="200" alt="Description">   

# Outsider 

Video Intrusion Detection System

![preview](./public/output_detected.gif)

</div>

Computer vision pipeline for intrusion detection in restricted zones using YOLOv8 + OpenCV.

## Features

- Person detection with YOLOv8 (pre-trained on COCO)
- Real-time visualization with bounding boxes and ROIs
- Google Colab compatible

## Structure

```
outsider/
├── src/
│   ├── detector.py          # Person detection with YOLOv8
│   ├── zone_manager.py      # Restricted zone (ROI) management
│   ├── alert_manager.py     # Alert system
│   ├── video_pipeline.py    # Main video pipeline
│   └── utils.py             # General utilities
├── configs/
│   └── zones.json           # Zone configuration
├── tests/
│   └── test_zones.py        # Unit tests
├── outsider_colab.ipynb     # Google Colab notebook
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Quick start

```bash
uv pip install -r requirements.txt

# Local video
python -m src.video_pipeline --source video.mp4 --zones configs/zones.json

# RTSP stream
python -m src.video_pipeline --source rtsp://ip:port/stream --zones configs/zones.json

# Webcam
python -m src.video_pipeline --source 0 --zones configs/zones.json
```

## Docker

> Containers run in headless mode (`--no-display`). Alerts are saved to the `alerts/` directory via a mounted volume.

### Local video file

Place your video inside a `videos/` folder, then:

```bash
docker compose up --build
```

By default it runs `videos/video.mp4`. To use a different file:

```bash
docker compose run --rm outsider \
  --source videos/other.mp4 \
  --zones configs/zones.json \
  --no-display
```

### RTSP stream

```bash
RTSP_URL=rtsp://ip:port/stream docker compose --profile rtsp up --build
```

### Webcam

```bash
docker compose --profile webcam up --build
```

> Requires `/dev/video0` to be available on the host.

### Custom arguments

Override any pipeline argument directly:

```bash
docker compose run --rm outsider \
  --source videos/video.mp4 \
  --zones configs/zones.json \
  --model yolov8s.pt \
  --confidence 0.6 \
  --cooldown 10 \
  --no-display
```

## Public datasets

- [VIRAT Video Dataset](https://viratdata.org/)
- [COCO Dataset](https://cocodataset.org/)
- [Town Centre Dataset (Oxford)](https://megapixels.cc/oxford_town_centre/)

