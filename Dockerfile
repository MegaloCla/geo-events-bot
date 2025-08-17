FROM python:3.12-slim

WORKDIR /app

COPY . /app/

RUN pip install poetry && poetry install --without dev,test

CMD ["poetry", "run", "python", "src/geo_events_bot"]
