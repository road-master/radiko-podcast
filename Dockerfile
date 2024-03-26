FROM mstmelody/python-ffmpeg:20240327020500
# sqlite: To cache radiko programs locally
RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlite=2.8.17-15fakesync1build1 \
 && rm -rf /var/lib/apt/lists/*
# see: https://pythonspeed.com/articles/activate-virtualenv-dockerfile/
ENV PIPENV_VENV_IN_PROJECT=1
COPY radikopodcast LICENSE Pipfile pyproject.toml README.md setup.cfg setup.py /workspace/
RUN pip3 --no-cache-dir install pipenv==2023.12.1 \
 && pipenv install --deploy --skip-lock --dev
COPY . /workspace
VOLUME ["/workspace/output"]
ENTRYPOINT [ "pipenv", "run", "radiko-podcast" ]
