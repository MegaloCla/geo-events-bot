from geo_events_bot.models.location_filter import LocationFilter
from geo_events_bot.services.settings_store import SettingsStore


def test_location_settings_survive_reopening(tmp_path):
    location = LocationFilter(city="Roma", latitude=41.9, longitude=12.5, radius_km=50)
    directory = str(tmp_path / "settings")
    store = SettingsStore(directory)
    assert store.load_location_filter() is None  # noqa: S101
    store.save_location_filter(location)
    reopened = SettingsStore(directory)
    assert reopened.load_location_filter() == location  # noqa: S101
    reopened.save_location_filter(None)
    assert reopened.load_location_filter() is None  # noqa: S101
