from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Instagram API OK!"

@app.route("/health")
def health():
    return {
        "status": "ok",
        "service": "instagram-video-api"
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
