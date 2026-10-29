import pytest
from pydantic import ValidationError

from geo_events_bot.models.feature_collection_response import Geometry


@pytest.mark.parametrize("coordinates", [[], [12.5], [12.5, 41.9, 10.0, 0.0]])
def test_invalid_coordinate_lengths(coordinates):
    with pytest.raises(ValidationError):
        Geometry(type="Point", coordinates=coordinates)


@pytest.mark.parametrize("coordinates", [[12.5, 41.9], [12.5, 41.9, 10.0]])
def test_supported_coordinates(coordinates):
    geometry = Geometry(type="Point", coordinates=coordinates)
    assert geometry.coordinates == coordinates  # noqa: S101
