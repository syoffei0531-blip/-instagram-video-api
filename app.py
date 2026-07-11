from flask import Flask, request, jsonify
import requests
import os
import time

app = Flask(__name__)

ACCESS_TOKEN = os.getenv("IG_ACCESS_TOKEN")
IG_USER_ID = os.getenv("IG_USER_ID")

@app.route("/")
def home():
    return "Instagram API OK!"

@app.route("/health")
def health():

@app.route("/create-instagram", methods=["POST"])
def create_instagram():

    try:

        # n8nから受信
        video = request.files["video"]
        caption = request.form.get("caption", "")

        # 保存フォルダ
        os.makedirs("/tmp/instagram", exist_ok=True)

        video_path = "/tmp/instagram/video.mp4"

        video.save(video_path)

        return jsonify({
            "success": True,
            "caption": caption,
            "video": video_path
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
    
    return {
        "status": "ok",
        "service": "instagram-video-api"
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
