FROM python:3.10-slim
RUN mkdir /app
COPY /src /app
COPY pyproject.toml /app
WORKDIR /app
ENV PYTHONPATH=${PYTHONPATH}:${PWD}
RUN apt-get update \
    && apt-get install -y git \
    && pip3 install poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-dev \
    && pip3 uninstall -y poetry \
    && rm /app/poetry.lock \
    && rm /app/pyproject.toml \
    && apt-get remove -y git \
    && apt-get clean autoclean \
    && apt-get autoremove --yes \
    && rm -rf /var/lib/{apt,dpkg,cache,log}/
CMD ["python3", "main.py"]