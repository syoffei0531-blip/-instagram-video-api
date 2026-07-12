from flask import Flask, request, jsonify

import requests
import os
import time
import traceback

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
@app.route("/create-instagram", methods=["POST"])
def create_instagram():

    try:

        print("")
        print("========================================")
        print("Instagram Reel Upload Started")
        print("========================================")
        
     
        image = request.files["image"] 
        
        audio = request.files["audio"]
        
        bgm = request.files["bgm"]
       
        script = request.files["script"]

        caption = request.form.get("caption","")

            os.makedirs("/tmp/instagram", exist_ok=True)

            image_path = "/tmp/instagram/image.png"
            audio_path = "/tmp/instagram/audio.mp3"
            bgm_path = "/tmp/instagram/bgm.mp3"
            script_path = "/tmp/instagram/script.txt"
            subtitle_path = "/tmp/instagram/subtitle.srt"

            image.save(image_path)
            audio.save(audio_path)
            bgm.save(bgm_path)
            script.save(script_path)
        
        print("========== Instagram Upload ==========")
        print("Video URL:", video_url)
        print("Caption:", caption)
        
        create_url = f"https://graph.facebook.com/v23.0/{IG_USER_ID}/media"

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
            "creation_id": creation_id,
            return jsonify(publish), 500

        return jsonify({
            "success": True,
            "instagram_post_id": publish["id"],
            "message": "Instagram Reel published successfully"
        })

    except Exception as e:

        traceback.print_exc()

        return jsonify({
            "success": False,
            "error": str(e)
            
    }), 500 
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
