# ytdlp Server

ytdlp Sever is a API Endpoint for launch yt-dlp on your network.

## Build / Install

### Install as container

Recommend choise install.

```sh
docker compose build
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

Edit `docker-compose.yml` set your directory to `volumes` for download.

```yml
worker:
  build:
    dockerfile: ./Dockerfile_worker
  depends_on:
    - redis
  environment:
    RQ_REDIS_URL: redis://redis
  volumes:
    - /path/to/your/video/dir:/download
  working_dir: /download
```

Lauch container with mounting download path.

```sh
## set scale of workers. 
docker compose up -d --scale worker=2
## show log
docker compose logs -f
```

<!-- ### Launch as exe // not verified

1. Put exe `Downloads` dir.
2. Launch app. -->

## How to use

1. send request like:
    ```
    curl -X POST "http://localhost:5000/ytdlp" -d "{\"url\": "https://www.youtube.com/watch?v=XXXXXXXXXX", \"format\": \"bv*+ba/best\"}
    ```

2. wait a minute and will generate video to your directory.

To make it easy, I recommend create iOS Shortcut like that...

![iOS Shortcut example](./view.png)
