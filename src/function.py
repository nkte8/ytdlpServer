# https://github.com/yt-dlp/yt-dlp/blob/master/yt_dlp/YoutubeDL.py
from yt_dlp import YoutubeDL


## Process
def download(url: str, param: dict) -> None:
    param["quiet"] = True
    param["noplaylist"] = True
    param["overwrites"] = True
    with YoutubeDL(param) as ydl:
        param["outtmpl"] = get_title(ydl=ydl, url=url) + ".%(ext)s"
        ydl.download(url)


def get_title(ydl: YoutubeDL, url: str) -> str:
    info_dict = ydl.extract_info(url, download=False)
    ydl.list_formats(info_dict)
    return (
        info_dict.get("title").replace("/", "-").replace("\\", "-")
        + " ["
        + info_dict["id"]
        + "]"
    )
