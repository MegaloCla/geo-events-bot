from geo_events.controllers.event_poller import URL
from geo_events.services.ingv_api import get_earthquake_data


def test_get_earthquake_data():
    assert get_earthquake_data(URL) is not None  # noqa: S101
