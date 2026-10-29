from __future__ import annotations

from typing import TYPE_CHECKING

import diskcache as dc

if TYPE_CHECKING:
    from geo_events_bot.models.feature_collection_response import Feature


class EventCache:
    def __init__(
        self,
        cache_dir: str = "/tmp/event-cache-dir",  # noqa: S108
        size_limit: float = 1e6,
    ) -> None:
        self.cache = dc.Cache(directory=cache_dir, size_limit=size_limit)

    def add_event(self, feature: Feature) -> bool:
        event_id = feature.properties.event_id
        cached = self.cache.get(event_id)
        if cached is None or feature.properties.version > cached.properties.version:
            self.cache.set(event_id, feature)
            return True
        return False

    def get_new_events(self, features: list[Feature]) -> list[Feature]:
        new_events = []
        for feature in features:
            cached = self.cache.get(feature.properties.event_id)
            if cached is None or feature.properties.version > cached.properties.version:
                new_events.append(feature)
        return new_events

    def close(self) -> None:
        self.cache.close()
