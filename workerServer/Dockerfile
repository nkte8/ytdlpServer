FROM alpine:3.21

WORKDIR /workspace
ENV DEBIAN_FRONTEND=noninteractive
RUN apk --no-cache --update add python3 py3-pip gcc ffmpeg mutagen~=1.47.0
RUN curl -fsSL https://deno.land/install.sh | sh
COPY requirements.txt .

RUN pip3 install --break-system-packages --no-cache --upgrade -r requirements.txt
COPY src/ .
COPY entrypoint.sh .
RUN chmod +x /workspace/entrypoint.sh

WORKDIR /tmpdownload
ENTRYPOINT ["/workspace/entrypoint.sh"]