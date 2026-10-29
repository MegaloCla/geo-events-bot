from pydantic import BaseModel


class City(BaseModel):
    id: int
    name: str
    latitude: float
    longitude: float
    admin1: str = ""
    country: str = ""
    feature_code: str = ""

    @property
    def label(self) -> str:
        return ", ".join(
            part for part in (self.name, self.admin1, self.country) if part
        )
