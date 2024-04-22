# ytdlp Server

ytdlp Sever is a API Endpoint for launch yt-dlp on your network.

## Build / Install

### Install as container

Recommend choise install.

```sh
docker build -t ytdlpserver:latest .
```

Attention: Very long to build, wait a moment.

<!-- ### Install as exec // not verified

launch nuitka3 and get exe.

Install python3.11 (not 3.12, nuitka3 not support yet) on your machine.

ex: Git-bash (host install python3)

```sh
pip install -r requirements.txt
nuitka3 --standalone ./main.py
```

generete `main.exe` and launch. -->

## Launch

### Launch as container

Only lauch container with mounting download path.

```sh
docker run --rm --detach -p 5000:5000 --name ytdlpserver -v /mnt/video:/download ytdlpserver:latest
```

<!-- ### Launch as exe // not verified

1. Put exe `Downloads` dir.
2. Launch app. -->

## How to use

1. send request like: `curl -X GET "http://localhost:5000/dl?url=https://www.youtube.com/watch?v=XXXXXXXXXX"`
2. wait a minute and will generate the most quarity `mp4` video.

To make it easy, I recommend create iOS Shortcut like that...

![iOS Shortcut example](./view.png)
