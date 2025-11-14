from flask import Flask, request, jsonify
import yt_dlp
import uuid

app = Flask(__name__)

FFMPEG_PATH = "/usr/bin/ffmpeg"  # Linux

def download_youtube_video(url):
    try:
        video_id = str(uuid.uuid4())
        output_name = f"video_{video_id}.mp4"

        ydl_opts = {
            "format": "bv*+ba/b",              # melhor vídeo + melhor áudio
            "outtmpl": output_name,
            "merge_output_format": "mp4",
            "ffmpeg_location": FFMPEG_PATH,    # ffmpeg oficial do Linux
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
def download():
    data = request.get_json()

    if not data or "url" not in data:
        return jsonify({"error": "Missing 'url'"}), 400

    url = data["url"]

    success, output, error = download_youtube_video(url)

    if not success:
        return jsonify({"error": error}), 500

    return jsonify({"file": output}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
