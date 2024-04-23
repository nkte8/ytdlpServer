from __future__ import annotations

import os
from pathlib import Path

import redis
from flask import Flask, Response, jsonify, request
from function import download, format_set, get_name, merge
from rq import Queue
from waitress import serve
from yt_dlp import YoutubeDL

app = Flask(__name__)
app.json.ensure_ascii = False

## タスクキュー
q = Queue(connection=redis.from_url(os.environ.get("RQ_REDIS_URL")))


class ParameterError(Exception):
    def __init__(self: Exception) -> None:
        return


@app.route("/dl", methods=["GET"])
def endpoint() -> tuple[Response, int]:
    try:
        query = request.args
        url = query["url"]
        fmt = "mp4" if query.get("fmt") is None else query.get("fmt")
        print("INFO: url =", url, " / fmt =", fmt)

        if url is None:
            raise ParameterError

        ## ydlインスタンスから情報を収集
        ydl = YoutubeDL(params={"noplaylist": True})
        info_dict = get_info(ydl, url)
        [video, audio, title] = get_best_format(info_dict, fmt)

        # ファイル名
        output_name = title + "." + fmt
        ## ダウンロード処理
        [
            q.enqueue(download, args=(url, param))
            for param in [video, audio]
            if param.get("format") is not None
        ]
        # 前の処理の残骸がある場合は削除
        if Path(output_name).exists():
            Path(output_name).unlink()

        q.enqueue(merge, args=(title, fmt))

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
            best_video["outtmpl"] = get_name(title, "video", fmt)
        if (format_set.get(fmt).get("audio") is not None) and (
            dlfmt.get("audio_ext") == format_set.get(fmt).get("audio")
        ):
            best_audio["format"] = dlfmt.get("audio_ext")
            best_audio["outtmpl"] = get_name(title, "audio", fmt)
    return best_video, best_audio, title


if __name__ == "__main__":
    print("INFO: Success up ytdlpServer")

    # dev -> app.run(host="0.0.0.0", port=5000)
    serve(app, host="0.0.0.0", port=5000)
