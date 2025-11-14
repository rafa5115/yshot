from flask import Flask, request, jsonify
from pytubefix import YouTube
import re
import moviepy.editor as mp
import yt_dlp
import os
import uuid
import ffmpeg_static



app = Flask(__name__)

# -----------------------------
# Valida qualquer link do YouTube
# -----------------------------
def is_valid_youtube_url(url):
    pattern = r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/"
    return re.match(pattern, url) is not None



def download_youtube_video(url):
    try:
        video_id = str(uuid.uuid4())
        output_name = f"video_{video_id}.mp4"

        ydl_opts = {
            "format": "bv*+ba/b",  # vídeo + áudio
            "outtmpl": output_name,
            "merge_output_format": "mp4",
            "ffmpeg_location": ffmpeg_static.path,  # usa ffmpeg portátil
            "quiet": True,
            "noprogress": True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        return True, output_name, None

    except Exception as e:
        return False, None, str(e)


# -----------------------------
# Rotas
# -----------------------------
@app.route("/download", methods=["POST"])
def download():
    data = request.get_json()
    url = data.get("url")

    if not url:
        return jsonify({"error": "Missing URL."}), 400

    if not is_valid_youtube_url(url):
        return jsonify({"error": "Invalid YouTube URL."}), 400

    success, filename, error = download_youtube_video(url)

    if not success:
        return jsonify({"error": error}), 500

    return jsonify({
        "message": "Download concluído com sucesso.",
        "file": filename
    }), 200


@app.route("/")
def home():
    return "API está rodando.<br>Use POST /download para baixar vídeos."



if __name__ == "__main__":
    app.run(debug=True)
