FROM python:3.10-slim
RUN mkdir /app
COPY /src /app
COPY pyproject.toml /app
WORKDIR /app
ENV PYTHONPATH=${PYTHONPATH}:${PWD}
RUN pip3 install poetry && poetry config virtualenvs.create false && poetry install --no-dev && pip3 uninstall -y poetry && rm /app/poetry.lock && rm /app/pyproject.toml
CMD ["python3", "surv_server.py"]