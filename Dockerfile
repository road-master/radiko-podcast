FROM mstmelody/python-ffmpeg:20210822032000
# sqlite: To cache radiko programs locally
RUN apt-get update && apt-get install -y \
    sqlite \
 && rm -rf /var/lib/apt/lists/*
# see: https://pythonspeed.com/articles/activate-virtualenv-dockerfile/
ENV PIPENV_VENV_IN_PROJECT=1
COPY radikopodcast LICENSE Pipfile pyproject.toml README.md setup.cfg setup.py /workspace/
RUN pip --no-cache-dir install pipenv \
 && pipenv install --deploy --skip-lock --dev
COPY . /workspace
VOLUME ["/workspace/output"]
ENTRYPOINT [ "pipenv", "run", "radiko-podcast" ]
