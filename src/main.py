from __future__ import annotations

import hashlib
from pathlib import Path

from flask import Flask, Response, jsonify, request
from moviepy.editor import AudioFileClip, VideoFileClip

# https://github.com/yt-dlp/yt-dlp/blob/master/yt_dlp/YoutubeDL.py
from yt_dlp import YoutubeDL

app = Flask(__name__)
app.json.ensure_ascii = False


class ParameterError(Exception):
    def __init__(self: Exception) -> None:
        return


## Downloader
def ytdlp_download(url: str, param: dict) -> None:
    param["quiet"] = True
    ydl = YoutubeDL(param)
    ydl.extract_info(url, download=True)


def merge_video(video: str, audio: str, out: str) -> None:
    print("INFO: [ffmpeg] Start convert video: ", out)
    hash_md5 = hashlib.sha256(out.encode()).hexdigest()
    clip = VideoFileClip(video)
    audioclip = AudioFileClip(audio)
    new_videoclip = clip.set_audio(audioclip)
    new_videoclip.write_videofile(
        out,
        verbose=False,
        logger=None,
        codec="libx264",
        audio_codec="aac",
        temp_audiofile=hash_md5 + ".m4a",
        remove_temp=True,
    )
    print("INFO: [ffmpeg] Finished convert video: ", out)


## GET Endpoint
@app.route("/dl", methods=["GET"])
async def endpoint() -> tuple[Response, int]:
    try:
        url = request.args.get("url")
        fmt = "mp4"
        if url is None:
            raise ParameterError
        ydl = YoutubeDL()
        ## ydlインスタンスから情報を収集
        info_dict = get_info(ydl, url)
        video, audio = get_best_format(info_dict, fmt)
        ## ダウンロード処理
        for param in video, audio:
            ytdlp_download(url, param)

        # ファイル名
        video_name = video["outtmpl"]["default"]
        audio_name = audio["outtmpl"]["default"]
        output_name = info_dict["title"] + "." + fmt
        # 残骸があった場合は削除
        if Path(output_name).exists():
            Path(output_name).unlink()

        if (audio["format"] is not None) and (video["format"] is not None):
            merge_video(
                video=video_name,
                audio=audio_name,
                out=output_name,
            )
        for file in video_name, audio_name:
            Path(file).unlink()

        ## レスポンス
        result_response = (
            jsonify(
                {
                    "result": {
                        "title": info_dict["title"],
                        "url": url,
                        "format": fmt,
                    },
                },
            ),
            200,
        )
    except ParameterError:
        result_response = (
            jsonify(
                {
                    "error": "Invalid Request",
                    "message": "Invalid request requested.",
                },
            ),
            400,
        )
    return result_response


format_set = {
    "mp4": {"video": "mp4", "audio": "m4a"},
    "webm": {"video": "webm", "audio": "webm"},
}


def get_info(ydl: YoutubeDL, url: str) -> dict:
    info_dict = ydl.extract_info(url, download=False)
    ydl.list_formats(info_dict)
    info_dict["title"] = (
        info_dict.get("title").replace("/", " - ").replace("\\", " - ")
        + " ["
        + info_dict["id"]
        + "]"
    )
    return info_dict


def get_best_format(info_dict: dict, fmt: str) -> tuple[dict, dict]:
    # 品質リストの下の方が品質が良いと仮定して取得
    title = "downloaded" if info_dict.get("title") is None else info_dict["title"]
    best_video = {
        "format": None,
        "outtmpl": str(title + " video." + format_set.get(fmt).get("video")),
    }
    best_audio = {
        "format": None,
        "outtmpl": str(title + " audio." + format_set.get(fmt).get("audio")),
    }
    # 結果の作成
    for dlfmt in info_dict["formats"]:
        if dlfmt.get("video_ext") == format_set.get(fmt).get("video"):
            best_video["format"] = dlfmt.get("format_id")
        if dlfmt.get("audio_ext") == format_set.get(fmt).get("audio"):
            best_audio["format"] = dlfmt.get("format_id")
    return best_video, best_audio


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
