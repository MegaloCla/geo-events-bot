# AGENTS.md

## Project

Telegram bot polling INGV (Italian seismic agency) APIs for earthquake updates. Python 3.12 + Poetry.

## Commands

| Action | Command |
|--------|---------|
| Install deps | `make install` (runs `poetry install --with dev,test`) |
| Lint | `make lint` (mypy then ruff check --fix + ruff format) |
| Test | `make tests` (runs `poetry run pytest tests`) |
| All | `make all` (install → lint → tests) |
| Single test | `poetry run pytest tests/<file>.py -k <name>` |
| Clean | `make clean` (git clean -Xdf) |

CI (`.github/workflows/actions.yml`) runs `ruff check`, `ruff format`, then `pytest` on push/PR to `master`. No mypy in CI.

## Architecture

```
src/geo_events_bot/
  __main__.py          # Entry point: creates Poller, calls start_polling(interval=5)
  controllers/
    event_poller.py    # Poller - main loop, coordinates services
  services/
    ingv_api.py        # INGV API client
    telegram_bot.py    # Telegram messaging via python-telegram-bot
    event_cache.py     # diskcache-based dedup of seen events
    event_subject.py   # Observer pattern subject
    map_generator.py   # Generates static map PNG with epicenter marker + overlay
  models/
    observer.py        # Observer interface (send_message, send_photo)
    feature_collection_response.py  # Pydantic model for INGV GeoJSON
  utils/
    env_var.py         # Reads TELEGRAM_TOKEN, CHAT_TELEGRAM_ID from env
    logger.py          # Logging setup
```

Entry point requires `TELEGRAM_TOKEN` and `CHAT_TELEGRAM_ID` env vars. Run: `poetry run python src/geo_events_bot`

## Tooling quirks

- **Ruff** config in `pyproject.toml` is strict (many rules enabled). Ignores: `ANN001`, `ANN101`, `ANN201`, `ANN204`, `FA100`, `PLR0913`, `COM812`, `ISC001`, `D206`, `W191`, `Q000`, `D203`, `D212`. Double quotes, space indent.
- **mypy** is lenient: `disallow_untyped_defs = false`, `ignore_missing_imports = true`. Only checks `src/`.
- **pytest** runs with `--doctest-modules` and coverage (HTML + XML to `tests/reports/`).
- **pre-commit** runs ruff + mypy + yaml/trailing-whitespace checks.
- Package is declared as `{ include = "geo_events_bot", from = "src" }` — imports resolve as `geo_events_bot.*` not `src.*`.
- **staticmap** + **Pillow** used for map generation. `generate_event_map()` produces PNG bytes with red marker + text overlay.

## Conventions

- Observer pattern for event notification (EventSubject → Observer)
- Pydantic v2 for data models
- `diskcache` for persistent event dedup
- `.env` file for Docker; raw env vars for local dev
