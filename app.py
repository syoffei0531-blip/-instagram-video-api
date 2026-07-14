from flask import Flask, request, jsonify, send_file

import requests
import os
import time
import traceback
import subprocess
import json

app = Flask(__name__)

print("===== ROUTES =====")
print(app.url_map)
print("==================")

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

@app.route("/routes")
def routes():
    return str(app.url_map)

@app.route("/video")
def video():

    print("VIDEO EXISTS =", os.path.exists("output/reel.mp4"))
    print("VIDEO PATH =", os.path.abspath("output/reel.mp4"))

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
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-shortest",
            "-t", "10",              # ← まず30秒固定でテスト
            "-vf", "scale=1080:1920",
            output_path
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        print(result.stdout)
        print(result.stderr)

        result.check_returncode()
        
        print("Exists =", os.path.exists(output_path))
        
        print("Size =", os.path.getsize(output_path) if os.path.exists(output_path) else 0)

        print("Video Size:", os.path.getsize(output_path))

        print("Video Created :", output_path)

        print("Exists =", os.path.exists(output_path))
        
        print("Absolute =", os.path.abspath(output_path))
        
        print("========== Instagram Upload ==========")
       
        print("Caption:", caption)

        print("========== ENV ==========")
        print("IG_USER_ID =", repr(IG_USER_ID))
        print("ACCESS_TOKEN exists =", ACCESS_TOKEN is not None)
        print("ACCESS_TOKEN first 20 =", ACCESS_TOKEN[:20] if ACCESS_TOKEN else None)
        
        create_url = f"https://graph.facebook.com/v23.0/{IG_USER_ID}/media"

        print("Create URL =", create_url)
        
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

        print("★★★★ creation_id =", creation_id)
        
        return jsonify({
            "success": True,
            "creation_id": creation_id
        })
        
    except Exception as e:

        traceback.print_exc()

        return jsonify({
            "success": False,
            "error": str(e)
            
        }), 500 

@app.route("/publish-instagram", methods=["POST"])
def publish_instagram():
        
    try:

        data = request.get_json()

        creation_id = data["creation_id"]

        print("Publish creation_id =", creation_id)

        status_url = f"https://graph.facebook.com/v23.0/{creation_id}"

        status = requests.get(
            status_url,
            params={
                "fields": "status_code",
                "access_token": ACCESS_TOKEN
            }
        ).json()

        print("Status =", status)

        if status.get("status_code") != "FINISHED":

            return jsonify({
                "success": False,
                "status": status
            })

        publish_url = f"https://graph.facebook.com/v23.0/{IG_USER_ID}/media_publish"

        publish = requests.post(
            publish_url,
            data={
                "creation_id": creation_id,
                "access_token": ACCESS_TOKEN
            }
        ).json()

        print("Publish =", publish)

        return jsonify(publish)

    except Exception as e:

        traceback.print_exc()

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
            
if __name__ == "__main__":
    app.run(
        host="0.0.0.0", 
        port=int(os.environ.get("PORT", 8080))
    )
