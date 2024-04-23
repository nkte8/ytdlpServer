import hashlib
from pathlib import Path

from moviepy.editor import AudioFileClip, VideoFileClip

# https://github.com/yt-dlp/yt-dlp/blob/master/yt_dlp/YoutubeDL.py
from yt_dlp import YoutubeDL


## Process
def download(url: str, param: dict) -> None:
    param["quiet"] = True
    param["noplaylist"] = True
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


def merge(title: str, fmt: str) -> None:
    video_name = get_name(title, "video", fmt)
    audio_name = get_name(title, "audio", fmt)
    output_name = title + "." + fmt
    ## 音声/動画共にある場合のみマージ
    if Path(video_name).exists() and Path(audio_name).exists():
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

    print("INFO: Processes Succeed! ->", output_name)


def get_name(title: str, kind: str, fmt: str) -> str:
    return str(
        title + "_" + kind + "." + format_set.get(fmt).get(kind),
    )


format_set = {
    "mp4": {"video": "mp4", "audio": "m4a"},
    "webm": {"video": "webm", "audio": "webm"},
    "mp3": {"video": None, "audio": "mp3"},
    "opus": {"video": None, "audio": "opus"},
}
