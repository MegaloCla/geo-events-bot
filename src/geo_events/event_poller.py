import requests
from models.response import FeatureCollection

URL = "http://webservices.ingv.it/fdsnws/event/1/"

QUERY = "query?starttime=2024-07-24T00:00:00&format=geojson"

response = requests.get(URL + QUERY).json()  # noqa: S113

data = FeatureCollection(**response)

print(len(data.features))  # noqa: T201
