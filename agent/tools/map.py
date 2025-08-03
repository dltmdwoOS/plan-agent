import os
from googlemaps import Client
from agent.tool_registry import common_tool_registry
from agent.utils import load_locale_const

const = load_locale_const()

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
try:
    gmaps = Client(key=GOOGLE_MAPS_API_KEY)
except Exception as e:
    gmaps = None
    print("[tool:skip] GoogleMapsClient init failed → 'get_user_location', 'nearby_search' not registered:", e)

if gmaps:
    @common_tool_registry(
        name_or_callable="get_user_location",
        description=const.GET_USER_LOCATION_CONST['desc']
    )
    def get_user_location(query: str) -> str:
        result = gmaps.geolocate()
        location = result.get('location', {})
        lat = location.get('lat', const.GET_USER_LOCATION_CONST['no_location'])
        lng = location.get('lng', const.GET_USER_LOCATION_CONST['no_location'])
        return const.GET_USER_LOCATION_CONST['desc'].format(
            lat=lat,
            lng=lng
        )

    @common_tool_registry(
        name_or_callable="nearby_search",
        description=const.NEARBY_SEARCH_CONST['desc']
    )
    def nearby_search(keyword: str, latlng: dict[str, float], radius: int=200) -> str:
        places = gmaps.places_nearby(location=latlng, radius=radius,keyword=keyword)
        results = places.get('results', [])
        
        if not results:
            return const.NEARBY_SEARCH_CONST['no_result'].format(keyword=keyword)
        return "\n".join([
            const.NEARBY_SEARCH_CONST['result_format'].format(
                name=place.get('name', 'No name'),
                vicinity=place.get('vicinity', const.GET_USER_LOCATION_CONST['no_location']),
                rating=place.get('rating', 'No rating')
            ) for place in results
        ])