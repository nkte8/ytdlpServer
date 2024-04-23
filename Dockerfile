FROM ubuntu:22.04 as builder

WORKDIR /workspace
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y \
    python3 python3-pip build-essential \
    git musl-dev ffmpeg gcc libcurl4-openssl-dev && \
    apt-get autoremove -y && \
    apt-get clean

COPY requirements.txt .
RUN pip3 install --no-cache --upgrade -r requirements.txt
COPY src/ src/
RUN pyinstaller --onefile --clean ./src/main.py

FROM ubuntu:22.04
COPY --from=builder /workspace/dist/main /usr/local/bin/ytdlpserver
WORKDIR /download
ENV TZ=Asia/Tokyo
EXPOSE 5000
ENTRYPOINT ["/usr/local/bin/ytdlpserver"]