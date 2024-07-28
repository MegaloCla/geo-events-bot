FROM python:3.12-slim

WORKDIR /app

RUN pip install poetry

COPY . /app/

RUN poetry install --no-dev

CMD ["poetry", "run", "python", "src/geo_events_bot"]
