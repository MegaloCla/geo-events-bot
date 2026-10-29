from __future__ import annotations

from pathlib import Path

from geo_events_bot.models.location_filter import LocationFilter


class SettingsStore:
    def __init__(self, directory: str):
        self._path = Path(directory) / "location_filter.json"

    def load_location_filter(self) -> LocationFilter | None:
        if not self._path.exists():
            return None
        return LocationFilter.model_validate_json(
            self._path.read_text(encoding="utf-8")
        )

    def save_location_filter(self, location_filter: LocationFilter | None) -> None:
        if location_filter is None:
            self._path.unlink(missing_ok=True)
        else:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            temporary = self._path.with_suffix(".tmp")
            temporary.write_text(location_filter.model_dump_json(), encoding="utf-8")
            temporary.replace(self._path)
