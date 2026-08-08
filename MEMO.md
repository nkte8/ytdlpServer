# yt-dlpへの引数メモ

youtubeが採用しているav01ビデオコーデックは対応していないデバイスも存在するため、互換性を考慮して"avc1"を指定下ほうがよい。
例: 
```sh
yt-dlp -f "bestvideo[vcodec^=avc1][ext=mp4]+bestaudio[ext=m4a]" --merge-output-format mp4 "URL"
```