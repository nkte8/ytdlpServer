# https://github.com/yt-dlp/yt-dlp/blob/master/yt_dlp/YoutubeDL.py
import os
import re
import subprocess
import unicodedata
from pathlib import Path
from typing import Any

TMP_DIR = Path("/tmpdownload")
SAVEDIR = Path(os.environ.get("DOWNLOAD_DIR", "/download"))
COPY_TIMEOUT = int(os.environ.get("COPY_TIMEOUT", "120"))
VIDEO_EXTS = {"avi", "flv", "mkv", "mov", "mp4", "webm"}
AUDIO_EXTS = {"aac", "alac", "flac", "m4a", "mp3", "opus", "vorbis", "wav"}

MAX_NAME_BYTES = 255

def run_yt_dlp(job: dict[str, Any]) -> tuple[bool, str]:
    url = job.get("url")
    options = job.get("options") or []
    savedir = job.get("savedir") or ""
    subpath = Path(unicodedata.normalize("NFC", savedir))
    Path.mkdir(SAVEDIR / subpath, parents=True, exist_ok=True)

    safe_name = job.get("filename")
    if isinstance(safe_name, list):
        safe_name = "".join(str(x) for x in safe_name)
    # Ensure we never pass None into unicodedata.normalize
    safe_name = str(safe_name or "")
    safe_name = unicodedata.normalize("NFC", safe_name)
    safe_name = Path(safe_name).name
    safe_name = re.sub(r'[\\/¥:*?"<>|]', "_", safe_name)
    safe_name = re.sub(r"\s+", " ", safe_name.replace("\u3000", " ")).strip()

    print("INFO: Filename: ", safe_name)

    job_id = job.get("id")

    # 直接配置方式: 最終保存先に yt-dlp が直接出力する
    # safe_name が空の場合は job_id を利用し、常に拡張子は yt-dlp に決定させる
    base_name = safe_name if safe_name else str(job_id)
    outtmpl = str(SAVEDIR / subpath / (base_name + ".%(ext)s"))

    cmd = ["yt-dlp", "--no-progress", *options, "-o", outtmpl, "--no-playlist", url]
    print("INFO: Running yt-dlp:", " ".join(cmd))

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("INFO: yt-dlp succeeded for:", url)
    except subprocess.CalledProcessError as e:
        print("ERROR: yt-dlp failed (rc=", e.returncode, "):", e.stderr)
        return False, e.stderr or e.stdout or str(e)
    except FileNotFoundError:
        msg = "yt-dlp not found in PATH"
        print("ERROR:", msg)
        return False, msg
    except OSError as e:
        print("ERROR: Unexpected error running yt-dlp:", e)
        return False, str(e)

    # 旧二段階方式（tmp -> copy）は無効化。実行成功をそのまま成功として返す。
    return True, proc.stdout
