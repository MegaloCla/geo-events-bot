from typing import List

import diskcache as dc

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
        if event_id not in self.cache:
            self.cache.add(event_id, feature)
            return True
        return False

    def get_new_events(self, features: List[Feature]) -> List[Feature]:
        return [feature for feature in features if self.add_event(feature)]

    def close(self) -> None:
        self.cache.close()
