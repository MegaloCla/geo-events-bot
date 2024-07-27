from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class Geometry(BaseModel):
    type: str
    coordinates: List[float]


class Properties(BaseModel):
    event_id: int = Field(alias="eventId")
    origin_id: int = Field(alias="originId")
    time: datetime
    author: str
    mag_type: str = Field(alias="magType")
    mag: float
    mag_author: str = Field(alias="magAuthor")
    type: str
    place: str
    version: int
    geojson_creation_time: datetime = Field(alias="geojson_creationTime")


class Feature(BaseModel):
    type: str
    properties: Properties
    geometry: Geometry


class FeatureCollection(BaseModel):
    type: str
    features: List[Feature]


def format_event_message(feature: Feature) -> str:
    output_lines = []

    event_id = feature.properties.event_id
    event_time = feature.properties.time.strftime("%Y-%m-%d %H:%M:%S")
    magnitude = feature.properties.mag
    coordinates = feature.geometry.coordinates
    place = feature.properties.place
    output_lines.append(
        f"\n- Event ID: {event_id}\n- Event Time: {event_time}\n- Magnitude: {magnitude}\n- Place: {place}\n- "
        f"Coordinates: {coordinates}"
    )

    return "".join(output_lines)
