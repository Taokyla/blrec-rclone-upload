ARG python_version=3.10-slim

FROM python:$python_version

ENV POETRY_VERSION=1.6.1 \
  POETRY_HOME="/opt/poetry/home" \
  POETRY_CACHE_DIR="/opt/poetry/cache" \
  POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_IN_PROJECT=false

ENV PATH="$POETRY_HOME/bin:$PATH"

ENV APP_HOME /app

RUN apt-get update \
  && apt-get -y upgrade \
  && apt-get install --no-install-recommends -y curl \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python

WORKDIR $APP_HOME

COPY pyproject.toml ./

RUN poetry install

ADD main.py .

EXPOSE 3000

ENTRYPOINT ["poetry", "run"]

CMD ["python", "main.py"]
