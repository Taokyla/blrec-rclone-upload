FROM python:3.10-slim

LABEL org.opencontainers.image.source="https://github.com/Taokyla/blrec-rclone-upload"

VOLUME ["/rec"]

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/pysetup"\
    VENV_PATH="/opt/pysetup/.venv"

ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

RUN apt-get update \
  && apt-get -y upgrade \
  && apt-get install --no-install-recommends -y curl rclone \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

ENV POETRY_VERSION=1.8.2
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=${POETRY_HOME} python3 - --version ${POETRY_VERSION} && \
    chmod a+x /opt/poetry/bin/poetry

WORKDIR /app

COPY ./poetry.lock ./pyproject.toml ./

RUN poetry install --only main --no-dev

COPY . .

ENV RECORD_REPLACE_DIR=/rec
ENV RECORD_SOURCE_DIR=/rec
ENV RECORD_DESTINATION_DIR=onedrive:record
ENV XDG_CONFIG_HOME=/config
ENV TZ="Asia/Shanghai"


EXPOSE 8000
ENTRYPOINT ["poetry", "run", "uvicorn", "--reload", "--host=0.0.0.0", "--port=8000", "app.main:app"]
CMD []