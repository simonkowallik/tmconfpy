# build-python-poetry
FROM cgr.dev/chainguard/python:latest-dev as build-python-poetry

WORKDIR /build

COPY pyproject.toml /build/pyproject.toml
COPY poetry.lock /build/poetry.lock
COPY tmconfpy /build/tmconfpy
COPY LICENSE /build/LICENSE
COPY README.md /build/README.md

RUN pip install poetry poetry-plugin-export --user

RUN /home/nonroot/.local/bin/poetry export --format=requirements.txt --output=/build/requirements.txt --extras=apiserver

RUN /home/nonroot/.local/bin/poetry build --format=sdist --no-interaction

# build-apiserver
FROM cgr.dev/chainguard/python:latest-dev as build-apiserver

WORKDIR /build

COPY --from=build-python-poetry /build/requirements.txt /build/requirements.txt
COPY --from=build-python-poetry /build/dist/tmconfpy-*.tar.gz /build/

RUN pip install -r requirements.txt --user
RUN pip install /build/tmconfpy-*.tar.gz --user

# container
FROM cgr.dev/chainguard/python:latest

WORKDIR /app

COPY --from=build-apiserver /home/nonroot/.local /home/nonroot/.local

ENV PATH="/home/nonroot/.local/bin:${PATH}"

EXPOSE 8000

ENTRYPOINT ["uvicorn", "tmconfpy.apiserver:app", "--no-server-header", "--host", "0.0.0.0", "--port", "8000"]
