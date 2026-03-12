FROM python:3.11-slim

WORKDIR /app

# System dependencies for headless OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Use headless OpenCV (no display required in container)
RUN sed 's/^opencv-python>=/opencv-python-headless>=/' requirements.txt > requirements_docker.txt && \
    pip install --no-cache-dir -r requirements_docker.txt

COPY . .

RUN mkdir -p alerts

ENTRYPOINT ["python", "-m", "src.video_pipeline"]
CMD ["--help"]
