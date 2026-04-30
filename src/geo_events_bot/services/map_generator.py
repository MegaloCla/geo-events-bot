import io

from PIL import Image, ImageDraw, ImageFont
from staticmap import CircleMarker, StaticMap

from geo_events_bot.models.feature_collection_response import Feature

MAP_WIDTH = 800
MAP_HEIGHT = 600
ZOOM_LEVEL = 8


def generate_event_map(feature: Feature) -> bytes:
    lon, lat, *_ = feature.geometry.coordinates

    static_map = StaticMap(MAP_WIDTH, MAP_HEIGHT)
    marker = CircleMarker((lon, lat), "#FF0000", 12)
    static_map.add_marker(marker)

    map_image = static_map.render()

    overlay_text = _build_overlay_text(feature)
    image_with_overlay = _add_overlay(map_image, overlay_text)

    output = io.BytesIO()
    image_with_overlay.save(output, format="PNG")
    output.seek(0)
    return output.getvalue()


def _build_overlay_text(feature: Feature) -> str:
    props = feature.properties
    return (
        f"Magnitudo: {props.mag}\n"
        f"Luogo: {props.place}\n"
        f"Lat: {feature.geometry.coordinates[1]:.4f}, Lon: {feature.geometry.coordinates[0]:.4f}"
    )


def _add_overlay(base_image: Image.Image, text: str) -> Image.Image:
    img = base_image.copy()
    draw = ImageDraw.Draw(img)

    font: ImageFont.FreeTypeFont | ImageFont.ImageFont
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
    except OSError:
        font = ImageFont.load_default()

    lines = text.split("\n")
    line_height = 22
    padding = 12
    box_width = max(draw.textlength(line, font=font) for line in lines) + padding * 2
    box_height = len(lines) * line_height + padding * 2

    x = 10
    y = img.height - box_height - 10

    draw.rounded_rectangle(
        (x, y, x + box_width, y + box_height),
        radius=8,
        fill=(0, 0, 0, 180),
    )

    for i, line in enumerate(lines):
        draw.text(
            (x + padding, y + padding + i * line_height),
            line,
            fill="white",
            font=font,
        )

    return img
