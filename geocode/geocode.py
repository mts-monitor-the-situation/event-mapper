import googlemaps
from typing import TypedDict, List


class GeocodeResult(TypedDict):
    latitude: float
    longitude: float
    place_id: str


def geocode_location(client: googlemaps.Client, locations: List[str]) -> List[GeocodeResult]:
    """
    Geocode a list of locations using Google Maps API.
    Returns a list of dictionaries with latitude(s), longitude(s), and place_id(s).
    """
    try:
        results = []
        for location in locations:
            geocode_result = client.geocode(location)
            if not geocode_result:
                raise ValueError(f"No results found for location: {location}")

            lat = geocode_result[0]["geometry"]["location"]["lat"]
            lng = geocode_result[0]["geometry"]["location"]["lng"]
            place_id = geocode_result[0]["place_id"]
            results.append({"latitude": lat, "longitude": lng, "place_id": place_id})
        return results
    except Exception as e:
        print(f"Error geocoding {location}: {e}")
        raise ValueError(f"Failed to geocode location: {location}")
