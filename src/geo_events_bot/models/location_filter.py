from math import asin, cos, radians, sin, sqrt

from pydantic import BaseModel, Field

EARTH_RADIUS_KM = 6371.0


class LocationFilter(BaseModel):
    city: str = Field(min_length=1)
    latitude: float = Field(ge=-90, le=90, allow_inf_nan=False)
    longitude: float = Field(ge=-180, le=180, allow_inf_nan=False)
    radius_km: float = Field(gt=0, allow_inf_nan=False)

    def distance_km(self, latitude: float, longitude: float) -> float:
        """Return the surface distance to the epicenter using the haversine formula."""
        latitude_delta = radians(latitude - self.latitude)
        longitude_delta = radians(longitude - self.longitude)
        haversine = (
            sin(latitude_delta / 2) ** 2
            + cos(radians(self.latitude))
            * cos(radians(latitude))
            * sin(longitude_delta / 2) ** 2
        )
        return 2 * EARTH_RADIUS_KM * asin(sqrt(min(1.0, max(0.0, haversine))))
