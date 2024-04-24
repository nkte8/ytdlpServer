# https://github.com/yt-dlp/yt-dlp/blob/master/yt_dlp/YoutubeDL.py
from yt_dlp import YoutubeDL


## Process
def download(url: str, param: dict) -> None:
    param["quiet"] = True
    param["noplaylist"] = True
    param["overwrites"] = True
    with YoutubeDL(param) as ydl:
        ydl.download(url)
