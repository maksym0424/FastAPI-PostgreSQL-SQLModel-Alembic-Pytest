FROM python:3.12-slim as builder
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
RUN apt update
RUN pip install poetry
RUN apt install python3-dev libpq-dev gcc -y
WORKDIR /app
COPY . .
RUN poetry install

FROM python:3.12-slim as base
COPY --from=builder /app /app
RUN apt update
RUN apt install libpq5 -y
WORKDIR /app
ENV PATH="/app/.venv/bin:$PATH"
CMD [ "python3", "main.py" ]
