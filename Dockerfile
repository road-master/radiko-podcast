FROM futureys/claude-code-python-development:20260407212500
RUN apt-get update && apt-get install --no-install-recommends -y \
    curl/stable \
    xz-utils/stable \
    # sqlite: To cache radiko programs locally
    sqlite3/stable \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN curl --location https://github.com/BtbN/FFmpeg-Builds/releases/download/autobuild-2026-02-28-12-59/ffmpeg-n8.0.1-66-g27b8d1a017-linuxarm64-gpl-shared-8.0.tar.xz | tar --extract --xz --strip-components 2 --directory=/usr/bin
# To prevent following error:
#   ffmpeg: error while loading shared libraries: libavdevice.so.62: cannot open shared object file: No such file or directory
COPY libavdevice_so.conf /etc/ld.so.conf.d/
RUN ldconfig
COPY radikopodcast LICENSE pyproject.toml README.md /workspace/
RUN uv sync --python 3.13
COPY . /workspace/
VOLUME ["/workspace/output"]
ENTRYPOINT [ "uv", "run" ]
CMD ["pytest"]
