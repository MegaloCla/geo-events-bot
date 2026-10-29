import pytest
from pydantic import ValidationError

from geo_events_bot.models.location_filter import LocationFilter


def test_distance_uses_latitude_longitude_in_order():
    location = LocationFilter(city="Roma", latitude=41.9, longitude=12.5, radius_km=100)
    assert location.distance_km(41.9, 12.5) == 0  # noqa: S101
    assert location.distance_km(40.85, 14.27) == pytest.approx(187.5, abs=1)  # noqa: S101


def test_distance_across_date_line():
    location = LocationFilter(city="Test", latitude=0, longitude=179.9, radius_km=50)
    assert location.distance_km(0, -179.9) == pytest.approx(22.24, abs=0.1)  # noqa: S101


@pytest.mark.parametrize(
    "changes",
    [
        {"latitude": 91},
        {"longitude": -181},
        {"radius_km": 0},
        {"radius_km": -1},
        {"radius_km": float("nan")},
        {"radius_km": float("inf")},
        {"city": ""},
    ],
)
def test_invalid_location(changes):
    values = {"city": "Roma", "latitude": 41.9, "longitude": 12.5, "radius_km": 100}
    with pytest.raises(ValidationError):
        LocationFilter.model_validate({**values, **changes})
