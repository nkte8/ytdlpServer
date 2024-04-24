from __future__ import annotations

import os

import redis
from flask import Flask, Response, jsonify, request
from function import download
from rq import Queue
from waitress import serve
from yt_dlp import YoutubeDL

app = Flask(__name__)
app.json.ensure_ascii = False

## タスクキュー
q = Queue(connection=redis.from_url(os.environ.get("RQ_REDIS_URL")))

audioext = ["m4a", "mp3", "opus"]


class ParameterError(Exception):
    def __init__(self: Exception) -> None:
        return


@app.route("/dl", methods=["GET"])
def endpoint() -> tuple[Response, int]:
    try:
        query = request.args
        url = query["url"]
        ext = query.get("ext")
        fmt = (
            "bestvideo*+bestaudio/best"
            if query.get("fmt") is None
            else query.get("fmt")
        )
        if ext in audioext:
            fmt = "bestaudio[ext=" + ext + "]"
        elif ext is not None:
            fmt = "bestvideo*[ext=" + ext + "]+bestaudio"

        print("INFO: url =", url, "/ fmt =", fmt, "/ ext =", ext)

        if url is None:
            raise ParameterError
        title = get_title(YoutubeDL({"noplaylist": True}), url)
        ## ydlインスタンスから情報を収集
        ## ダウンロード処理
        q.enqueue(
            download,
            args=(
                url,
                {
                    "format": fmt,
                    "outtmpl": title + ".%(ext)s",
                },
                ext,
            ),
        )

        ## レスポンス
        result_response = (
            jsonify(
                {
                    "title": title,
                    "url": url,
                    "format": fmt,
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


def get_title(ydl: YoutubeDL, url: str) -> str:
    info_dict = ydl.extract_info(url, download=False)
    ydl.list_formats(info_dict)
    return (
        info_dict.get("title").replace("/", "-").replace("\\", "-")
        + " ["
        + info_dict["id"]
        + "]"
    )


if __name__ == "__main__":
    print("INFO: Success up ytdlpServer")

    # dev -> app.run(host="0.0.0.0", port=5000)
    serve(app, host="0.0.0.0", port=5000)
