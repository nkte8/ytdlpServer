# FROM python:3.11-alpine3.18 as builder
FROM python:3.11-alpine3.18

WORKDIR /workspace
ENV DEBIAN_FRONTEND=noninteractive
# RUN apk --no-cache --update add git gcc musl-dev ffmpeg libc-dev g++ python3-dev patchelf
RUN apk --no-cache --update add git musl-dev ffmpeg

COPY requirements.txt .
RUN pip3 install --no-cache --upgrade -r requirements.txt
COPY src/ .
# RUN nuitka3 --standalone --onefile ./main.py

# FROM alpine:3.18.6
# COPY --from=builder /workspace/main.dist/* /usr/local/bin/
WORKDIR /download
ENV TZ=Asia/Tokyo
EXPOSE 5000
# ENTRYPOINT ["/usr/local/bin/main.bin"]
ENTRYPOINT ["python3","-u","/workspace/main.py"]