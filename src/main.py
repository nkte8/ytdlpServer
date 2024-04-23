from __future__ import annotations

import hashlib
from pathlib import Path

from flask import Flask, Response, jsonify, request
from moviepy.editor import AudioFileClip, VideoFileClip
from waitress import serve

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
    with YoutubeDL(param) as ydl:
        ydl.download(url)


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
        query = request.args
        url = query["url"]
        fmt = "mp4" if query.get("fmt") is None else query.get("fmt")
        print("INFO: url =", url, " / fmt =", fmt)

        if url is None:
            raise ParameterError

        ## ydlインスタンスから情報を収集
        ydl = YoutubeDL()
        info_dict = get_info(ydl, url)
        [video, audio, title] = get_best_format(info_dict, fmt)

        # ファイル名
        video_name = video["outtmpl"]
        audio_name = audio["outtmpl"]
        output_name = title + "." + fmt

        ## ダウンロード処理
        [
            ytdlp_download(url, param)
            for param in [video, audio]
            if param.get("format") is not None
        ]

        # 前の処理の残骸がある場合は削除
        if Path(output_name).exists():
            Path(output_name).unlink()

        ## 音声/動画共にある場合のみマージ
        if (
            video_name is not None
            and audio_name is not None
            and Path(video_name).exists()
            and Path(audio_name).exists()
        ):
            merge_video(
                video=video_name,
                audio=audio_name,
                out=output_name,
            )
            ## マージ前のメディアを削除
            for file in video_name, audio_name:
                if file is not None and Path(file).exists():
                    Path(file).unlink()
        ## データが片方しか取得できなかった場合は、リネーム
        elif video_name is not None and Path(video_name).exists():
            Path(video_name).rename(output_name)
        elif audio_name is not None and Path(audio_name).exists():
            Path(audio_name).rename(output_name)

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
        print("INFO: Processes Succeed! ->", output_name)
    except ParameterError:
        print("Error: Invalid request requested.")
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
    "mp3": {"video": None, "audio": "mp3"},
    "opus": {"video": None, "audio": "opus"},
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


def get_best_format(info_dict: dict, fmt: str) -> tuple[dict | None, dict | None, str]:
    # 品質リストの下の方が品質が良いと仮定して取得
    title = "downloaded" if info_dict.get("title") is None else info_dict["title"]
    ## ytdlpに受け渡す情報を作成する
    best_video = {
        "format": None,
        "outtmpl": None,
    }
    best_audio = {
        "format": None,
        "outtmpl": None,
    }
    # 結果の作成
    for dlfmt in info_dict["formats"]:
        if (format_set.get(fmt).get("video") is not None) and (
            dlfmt.get("video_ext") == format_set.get(fmt).get("video")
        ):
            best_video["format"] = dlfmt.get("video_ext")
            best_video["outtmpl"] = str(
                title + " video." + format_set.get(fmt).get("video"),
            )

        if (format_set.get(fmt).get("audio") is not None) and (
            dlfmt.get("audio_ext") == format_set.get(fmt).get("audio")
        ):
            best_audio["format"] = dlfmt.get("audio_ext")
            best_audio["outtmpl"] = str(
                title + " audio." + format_set.get(fmt).get("audio"),
            )
    return best_video, best_audio, title


if __name__ == "__main__":
    print("INFO: Success up ytdlpServer")

    # dev -> app.run(host="0.0.0.0", port=5000)
    serve(app, host="0.0.0.0", port=5000)
