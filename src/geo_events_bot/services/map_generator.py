from __future__ import annotations

import io
from datetime import UTC
from http import HTTPStatus
from pathlib import Path
from tempfile import gettempdir
from typing import TYPE_CHECKING

import diskcache
from PIL import Image, ImageDraw, ImageFont
from requests import RequestException
from staticmap import CircleMarker, StaticMap
from zoneinfo import ZoneInfo

if TYPE_CHECKING:
    from geo_events_bot.models.feature_collection_response import Feature

MAP_WIDTH = 1000
MAP_HEIGHT = 460
HEADER_HEIGHT = 190
FOOTER_HEIGHT = 130
ZOOM_LEVEL = 8
TILE_CACHE_SECONDS = 7 * 24 * 60 * 60
_BACKGROUND = "#f4f7fb"
_INK = "#12243a"
_MUTED = "#607086"
_ACCENT = "#e84d4d"
_PLACE_WIDTH = 770
_DEPTH_COORDINATE_COUNT = 3


class MapGenerationError(Exception):
    """The map renderer could not obtain or read its tiles."""


class _CachedStaticMap(StaticMap):
    def get(self, url, **kwargs: object) -> tuple[int, bytes]:
        with diskcache.Cache(str(Path(gettempdir()) / "geo-events-map-tiles")) as cache:
            cached = cache.get(url)
            if cached is not None:
                return cached
            status, content = super().get(url, **kwargs)
            if status == HTTPStatus.OK:
                cache.set(url, (status, content), expire=TILE_CACHE_SECONDS)
            return status, content


def generate_event_map(feature: Feature, distance_km: float | None = None) -> bytes:
    lon, lat, *_ = feature.geometry.coordinates
    static_map = _CachedStaticMap(
        MAP_WIDTH,
        MAP_HEIGHT,
        url_template="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
        headers={"User-Agent": "geo-events-bot/0.1.0"},
        tile_request_timeout=10,
    )
    for color, width in [("white", 32), (_ACCENT, 24), ("white", 8)]:
        static_map.add_marker(CircleMarker((lon, lat), color, width))
    try:
        map_image = static_map.render(zoom=ZOOM_LEVEL)
    except (RequestException, OSError, RuntimeError) as err:
        # staticmap reports exhausted tile downloads as RuntimeError.
        msg = "Unable to render event map"
        raise MapGenerationError(msg) from err

    image = _build_event_card(map_image, feature, distance_km)
    output = io.BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()


def _font(
    size: int, *, bold: bool = False
) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    try:
        return ImageFont.truetype(name, size)
    except OSError:
        return ImageFont.load_default(size=size)


def _place_lines(draw: ImageDraw.ImageDraw, place: str) -> list[str]:
    font = _font(28, bold=True)
    lines = [""]
    for word in place.split():
        candidate = f"{lines[-1]} {word}".strip()
        if not lines[-1] or draw.textlength(candidate, font=font) <= _PLACE_WIDTH:
            lines[-1] = candidate
        else:
            lines.append(word)
    lines = lines[:2]
    if len(" ".join(lines)) < len(" ".join(place.split())):
        lines[-1] += "…"
    for index in range(len(lines)):
        while draw.textlength(lines[index], font=font) > _PLACE_WIDTH:
            lines[index] = lines[index][:-2] + "…"
    return lines


def _build_event_card(
    map_image: Image.Image, feature: Feature, distance_km: float | None
) -> Image.Image:
    image = Image.new(
        "RGB", (MAP_WIDTH, HEADER_HEIGHT + MAP_HEIGHT + FOOTER_HEIGHT), _BACKGROUND
    )
    image.paste(map_image.convert("RGB"), (0, HEADER_HEIGHT))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, MAP_WIDTH, HEADER_HEIGHT - 1), fill=_INK)
    draw.rectangle((0, 0, 7, HEADER_HEIGHT - 1), fill=_ACCENT)
    draw.text(
        (32, 20), "GEO EVENTS  /  TERREMOTO", font=_font(16, bold=True), fill="#b9cadc"
    )
    draw.text(
        (MAP_WIDTH - 32, 20), "DATI INGV", font=_font(16), fill="#b9cadc", anchor="ra"
    )
    draw.rounded_rectangle((32, 62, 164, 162), radius=18, fill=_ACCENT)
    draw.text(
        (98, 76), "MAGNITUDO", font=_font(14, bold=True), fill="white", anchor="ma"
    )
    draw.text(
        (98, 99),
        f"{feature.properties.mag:.1f}",
        font=_font(42, bold=True),
        fill="white",
        anchor="ma",
    )
    for index, line in enumerate(_place_lines(draw, feature.properties.place)):
        draw.text((196, 63 + index * 35), line, font=_font(28, bold=True), fill="white")
    event_time = feature.properties.time
    if event_time.tzinfo is None:
        event_time = event_time.replace(tzinfo=UTC)
    local_time = event_time.astimezone(ZoneInfo("Europe/Rome"))
    draw.text(
        (196, 148),
        local_time.strftime("%d/%m/%Y  ·  %H:%M:%S %Z"),
        font=_font(18),
        fill="#b9cadc",
    )

    footer_y = HEADER_HEIGHT + MAP_HEIGHT
    draw.text((32, footer_y + 18), "PROFONDITÀ", font=_font(13, bold=True), fill=_MUTED)
    coordinates = feature.geometry.coordinates
    depth = (
        f"{coordinates[2]:.1f} km"
        if len(coordinates) == _DEPTH_COORDINATE_COUNT
        else "Non disponibile"
    )
    draw.text((32, footer_y + 40), depth, font=_font(24, bold=True), fill=_INK)
    label = "DISTANZA DAL TUO PUNTO" if distance_km is not None else "EPICENTRO"
    value = (
        f"{distance_km:.1f} km"
        if distance_km is not None
        else f"{coordinates[1]:.4f}, {coordinates[0]:.4f}"
    )
    draw.text((400, footer_y + 18), label, font=_font(13, bold=True), fill=_MUTED)
    draw.text((400, footer_y + 40), value, font=_font(24, bold=True), fill=_INK)
    draw.line((32, footer_y + 84, MAP_WIDTH - 32, footer_y + 84), fill="#dce3ed")
    draw.text(
        (32, footer_y + 98),
        "Fonte: INGV  ·  Distanza riferita all'epicentro",
        font=_font(14),
        fill=_MUTED,
    )
    draw.text(
        (MAP_WIDTH - 32, footer_y + 98),
        "© OpenStreetMap contributors",
        font=_font(14),
        fill=_MUTED,
        anchor="ra",
    )
    return image
