from unittest.mock import patch

import pytest
from requests import RequestException

from geo_events_bot.services.map_generator import MapGenerationError, generate_event_map


@pytest.mark.parametrize(
    "error", [OSError("Image"), RequestException("Tiles"), RuntimeError("Download")]
)
def test_rendering_failures_are_translated(feature, error):
    with (
        patch(
            "geo_events_bot.services.map_generator.StaticMap.render", side_effect=error
        ),
        pytest.raises(MapGenerationError) as exc_info,
    ):
        generate_event_map(feature)
    assert exc_info.value.__cause__ is error  # noqa: S101


def test_unexpected_rendering_error_propagates(feature):
    with (
        patch(
            "geo_events_bot.services.map_generator.StaticMap.render",
            side_effect=TypeError("Bug"),
        ),
        pytest.raises(TypeError, match="Bug"),
    ):
        generate_event_map(feature)


def test_card_is_valid_png_with_distance_and_long_place(feature):
    import io

    from PIL import Image

    from geo_events_bot.services.map_generator import MAP_HEIGHT, MAP_WIDTH

    feature.properties.place = "Una località con un nome molto lungo " * 8
    with patch(
        "geo_events_bot.services.map_generator.StaticMap.render",
        return_value=Image.new("RGB", (MAP_WIDTH, MAP_HEIGHT), "#aabbcc"),
    ) as render:
        result = generate_event_map(feature, distance_km=42.5)
    image = Image.open(io.BytesIO(result))
    assert image.format == "PNG"  # noqa: S101
    assert image.size == (1000, 780)  # noqa: S101
    render.assert_called_once_with(zoom=8)


def test_card_handles_missing_depth_and_font(feature):
    import io

    from PIL import Image, ImageFont

    feature.geometry.coordinates = [12.5, 41.9]
    fallback = ImageFont.load_default(size=18)
    with (
        patch(
            "geo_events_bot.services.map_generator.StaticMap.render",
            return_value=Image.new("RGB", (1000, 460)),
        ),
        patch(
            "geo_events_bot.services.map_generator.ImageFont.truetype",
            side_effect=OSError("Font missing"),
        ),
        patch(
            "geo_events_bot.services.map_generator.ImageFont.load_default",
            return_value=fallback,
        ),
    ):
        result = generate_event_map(feature)
    assert Image.open(io.BytesIO(result)).size == (1000, 780)  # noqa: S101


@pytest.mark.parametrize("status", [200, 404])
def test_tiles_are_cached_only_on_success(tmp_path, status):
    from geo_events_bot.services import map_generator

    tile_map = map_generator._CachedStaticMap(100, 100)  # noqa: SLF001
    with (
        patch.object(map_generator, "gettempdir", return_value=str(tmp_path)),
        patch(
            "geo_events_bot.services.map_generator.StaticMap.get",
            return_value=(status, b"tile"),
        ) as get,
    ):
        tile_map.get("https://example.com/tile.png")
        tile_map.get("https://example.com/tile.png")
    expected_calls = 1 if status == 200 else 2  # noqa: PLR2004
    assert get.call_count == expected_calls  # noqa: S101
