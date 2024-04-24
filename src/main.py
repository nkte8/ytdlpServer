from __future__ import annotations

import os

import redis
from flask import Flask, Response, jsonify, request
from function import download
from rq import Queue
from waitress import serve

app = Flask(__name__)
app.json.ensure_ascii = False

## タスクキュー
q = Queue(connection=redis.from_url(os.environ.get("RQ_REDIS_URL")))


class ParameterError(Exception):
    def __init__(self: Exception) -> None:
        return


@app.route("/ytdlp", methods=["POST"])
def endpoint() -> tuple[Response, int]:
    try:
        form = request.json
        url = form.get("url")
        fmt = (
            "bestvideo*+bestaudio/best"
            if form.get("format") is None
            else form.get("format")
        )

        print("INFO: url =", url, "/ format =", fmt)

        if url is None:
            raise ParameterError
        ## ydlインスタンスから情報を収集
        ## ダウンロード処理
        q.enqueue(
            download,
            args=(
                url,
                {
                    "format": fmt,
                },
            ),
        )

        ## レスポンス
        result_response = (
            jsonify(
                {
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


if __name__ == "__main__":
    print("INFO: Success up ytdlpServer")

    # dev -> app.run(host="0.0.0.0", port=5000)
    serve(app, host="0.0.0.0", port=5000)
