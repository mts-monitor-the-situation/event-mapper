import googlemaps
from typing import Dict, TypedDict


gmaps = googlemaps.Client(key="")


class GeocodeResult(TypedDict):
    latitude: float
    longitude: float
    place_id: str


def geocode_location(location: str) -> GeocodeResult:
    """
    Geocode a location using Google Maps API.
    Returns a dictionary with latitude and longitude.
    """
    try:
        geocode_result = gmaps.geocode(location)
        if not geocode_result:
            raise ValueError(f"No results found for location: {location}")

        lat = geocode_result[0]["geometry"]["location"]["lat"]
        lng = geocode_result[0]["geometry"]["location"]["lng"]
        place_id = geocode_result[0]["place_id"]
        return {"latitude": lat, "longitude": lng, "place_id": place_id}
    except Exception as e:
        print(f"Error geocoding {location}: {e}")
        raise ValueError(f"Failed to geocode location: {location}")
