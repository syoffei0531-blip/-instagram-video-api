FROM python:3.12-slim

WORKDIR /app

# FFmpegをインストール
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD gunicorn app:app --bind 0.0.0.0:$PORT
