from geo_events_bot.services.event_cache import EventCache


def test_checking_events_does_not_mark_them_delivered(event_cache, feature):
    assert event_cache.get_new_events([feature]) == [feature]  # noqa: S101
    assert event_cache.get_new_events([feature]) == [feature]  # noqa: S101


def test_delivered_version_survives_reopening(tmp_path, feature):
    cache_dir = str(tmp_path / "persistent-events")
    cache = EventCache(cache_dir=cache_dir)
    try:
        cache.add_event(feature)
    finally:
        cache.close()
    reopened = EventCache(cache_dir=cache_dir)
    try:
        assert reopened.get_new_events([feature]) == []  # noqa: S101
        revised = feature.model_copy(
            update={"properties": feature.properties.model_copy(update={"version": 2})}
        )
        assert reopened.get_new_events([revised]) == [revised]  # noqa: S101
        reopened.add_event(revised)
        reopened.add_event(feature)
        assert reopened.get_new_events([revised, feature]) == []  # noqa: S101
    finally:
        reopened.close()
