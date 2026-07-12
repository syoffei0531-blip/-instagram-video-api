from flask import Flask, request, jsonify, send_file

import requests
import os
import time
import traceback
import subprocess
import json

app = Flask(__name__)

ACCESS_TOKEN = os.getenv("IG_ACCESS_TOKEN")
IG_USER_ID = os.getenv("IG_USER_ID")

@app.route("/")
def home():
    return "Instagram API OK!"

@app.route("/health")
def health():
    return {
        "status": "ok",
        "service": "instagram-video-api"
    }
    
@app.route("/video")
def video():

    return send_file(
        "output/reel.mp4",
        mimetype="video/mp4"
    )

@app.route("/create-instagram", methods=["POST"])
def create_instagram():

    try:

        print("")
        print("========================================")
        print("Instagram Reel Upload Started")
        print("========================================")
        
     
        data = request.get_json()

        caption = data["caption"]
        image = data["image"]
        bgm = data["bgm"]

        image_path = os.path.join("images", image)
        bgm_path = os.path.join("bgm", bgm)

        output_path = os.path.join("output", "reel.mp4")
        
        print("Caption :", caption)
        print("Image :", image_path)
        print("BGM :", bgm_path)
        print("Output :", output_path)

        cmd = [
            "ffmpeg",
            "-y",
            "-loop", "1",
            "-i", image_path,
            "-i", bgm_path,
            "-c:v", "libx264",
            "-tune", "stillimage",
            "-c:a", "aac",
            "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            "-shortest",
            "-vf", "scale=1080:1920",
            output_path
        ]

        subprocess.run(cmd, check=True)

        print("Video Created :", output_path)
        
        print("========== Instagram Upload ==========")
       
        print("Caption:", caption)

        create_url = f"https://graph.facebook.com/v23.0/{IG_USER_ID}/media"

        video_url = request.url_root.rstrip("/") + "/video"

        payload = {
            "media_type": "REELS",
            "video_url": video_url,
            "caption": caption,
            "access_token": ACCESS_TOKEN
        }

        response = requests.post(create_url, data=payload)

        result = response.json()

        print("========== Create Container ==========")
        print("Status Code:", response.status_code)
        print("Response:", result)
        
        if "id" not in result:
            return jsonify(result), 500
            
        creation_id = result["id"]

        # -----------------------------
        # Containerの処理完了待ち
        # -----------------------------
        status_url = f"https://graph.facebook.com/v23.0/{creation_id}"

        for _ in range(30):

            status = requests.get(
                status_url,
                params={
                    "fields": "status_code",
                    "access_token": ACCESS_TOKEN
                }
            ).json()

            print(status)

            if status.get("status_code") == "FINISHED":
                break

            if status.get("status_code") == "ERROR":
                return jsonify(status), 500

            time.sleep(5)

        # -----------------------------
        # Publish
        # -----------------------------
        publish_url = f"https://graph.facebook.com/v23.0/{IG_USER_ID}/media_publish"

        publish = requests.post(
            publish_url,
            data={
                "creation_id": creation_id,
                "access_token": ACCESS_TOKEN
            }
        ).json()
        
        print("========== Publish ==========")
        print(publish)
        print("Publish ID:", publish.get("id"))        
        if "id" not in publish:
            return jsonify(publish), 500

        return jsonify({
            "success": True,
            "instagram_post_id": publish["id"]
        })

    except Exception as e:

        traceback.print_exc()

        return jsonify({
            "success": False,
            "error": str(e)
            
    }), 500 
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
