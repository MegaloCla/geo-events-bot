from datetime import datetime
from typing import List

import pytz
from pydantic import BaseModel, Field

_ROME_TZ = pytz.timezone("Europe/Rome")


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

    event_time_raw = feature.properties.time
    if event_time_raw.tzinfo is None:
        event_time_utc = event_time_raw.replace(tzinfo=pytz.utc)
    else:
        event_time_utc = event_time_raw.astimezone(pytz.utc)
    event_time = event_time_utc.astimezone(_ROME_TZ).strftime("%Y-%m-%d %H:%M:%S")
    magnitude = feature.properties.mag
    coordinates = f"Lat: {feature.geometry.coordinates[1]}, Lon: {feature.geometry.coordinates[0]}"
    place = feature.properties.place

    output_lines.append(f"\n📏 **Magnitude:** *{magnitude}*\n\n")
    output_lines.append(f"\n📌 **Location:** \n**{place}**\n")
    output_lines.append(f"\n📅 **Date & Time:** \n{event_time}\n\n")
    output_lines.append(f"\n🌐 **Coordinates:** \n{coordinates}\n")

    return "".join(output_lines)
