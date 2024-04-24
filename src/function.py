# https://github.com/yt-dlp/yt-dlp/blob/master/yt_dlp/YoutubeDL.py
from yt_dlp import YoutubeDL


## Process
def download(url: str, param: dict, ext: str) -> None:
    param["quiet"] = True
    param["noplaylist"] = True
    if ext is not None:
        param["merge_output_format"] = ext
    with YoutubeDL(param) as ydl:
        ydl.download(url)
