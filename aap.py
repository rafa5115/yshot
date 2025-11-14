from flask import Flask, request, jsonify, send_from_directory
import yt_dlp
import uuid
import os

app = Flask(__name__)

# Pasta onde os vídeos serão salvos
DOWNLOAD_FOLDER = "/root/videos"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

FFMPEG_PATH = "/usr/bin/ffmpeg"

def download_youtube_video(url):
    try:
        video_id = str(uuid.uuid4())
        output_name = f"video_{video_id}.mp4"
        output_path = os.path.join(DOWNLOAD_FOLDER, output_name)

        ydl_opts = {
            "format": "bv*+ba/b",
            "outtmpl": output_path,
            "merge_output_format": "mp4",
            "ffmpeg_location": FFMPEG_PATH,
            "quiet": True,
            "noprogress": True,
            "cookiefile": "cookies.txt",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        return True, output_name, None

    except Exception as e:
        return False, None, str(e)


@app.route("/download", methods=["POST"])
def api_download():
    data = request.get_json()

    if not data or "url" not in data:
        return jsonify({"error": "Missing 'url'"}), 400

    url = data["url"]

    success, output, error = download_youtube_video(url)

    if not success:
        return jsonify({"error": error}), 500

    # URL pública para acessar o vídeo
    base_url = request.host_url.replace("http://", "https://")

    public_url = f"{base_url}video/{output}"

    return jsonify({
        "file": output,
        "url": public_url
    }), 200


@app.route("/video/<path:filename>", methods=["GET"])
def serve_video(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=False)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
