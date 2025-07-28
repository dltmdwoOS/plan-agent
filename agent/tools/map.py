import os
from googlemaps import Client
from agent.tool_registry import common_tool_registry

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
try:
    gmaps = Client(key=GOOGLE_MAPS_API_KEY)
except Exception as e:
    gmaps = None
    print("[tool:skip] GoogleMapsClient init failed → 'get_user_location', 'nearby_search' not registered:", e)

if gmaps:
    @common_tool_registry(
        name_or_callable="get_user_location",
        description="""
        Determines the user's current location. Useful when the user asks questions like 'Where am I?' or 'What is my current location?'.
        
        Args:
            query (str): User's question or request (e.g., "Where am I?", "Tell me my current location")
        
        Returns:
            str: The user's current location information
        """
    )
    def get_user_location(query: str) -> str:
        result = gmaps.geolocate()
        location = result.get('location', {})
        lat = location.get('lat', 'No location info')
        lng = location.get('lng', 'No location info')
        
        return f"Current location: latitude {lat}, longitude {lng}."

    @common_tool_registry(
        name_or_callable="nearby_search",
        description="""
        Searches for nearby places based on the user's current location. Useful when the user asks questions like 'cafes nearby', 'restaurants near me', etc.
        
        Args:
            keyword (str): Keyword for the place to search (e.g., "cafe", "restaurant")
            latlng (dict[str, float]): The user's current location (latitude and longitude)
            radius (int): Search radius (in meters). If the user requests "cafes within 1km", enter 1000. If the user does not specify a radius, the default is 200m.
            
        Returns:
            str: List of nearby places including address and rating for each place
        """
    )
    def nearby_search(keyword: str, latlng: dict[str, float], radius: int=200) -> str:
        places = gmaps.places_nearby(location=latlng, radius=radius,keyword=keyword)
        results = places.get('results', [])
        
        if not results:
            return f"No nearby places found for '{keyword}'."
        
        return "\n".join([f"{place.get('name', 'No name')} ({place.get('vicinity', 'No location info')}) Rating : {place.get('rating', 'No rating')}" for place in results])