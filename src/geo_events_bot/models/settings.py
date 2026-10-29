from __future__ import annotations

from pydantic import BaseModel, Field

from geo_events_bot.models.location_filter import LocationFilter


class Settings(BaseModel):
    telegram_token: str = Field(min_length=1, repr=False)
    chat_id: str = Field(min_length=1)
    polling_interval: float = Field(default=5, gt=0, allow_inf_nan=False)
    min_magnitude: float = Field(default=2, ge=0, allow_inf_nan=False)
    default_radius_km: float = Field(default=100, gt=0, allow_inf_nan=False)
    location_choice_ttl: int = Field(default=600, gt=0)
    location_choice_cache_size: int = Field(default=128, gt=0)
    inline_cache_time: int = Field(default=60, ge=0)
    location_filter: LocationFilter | None = None
