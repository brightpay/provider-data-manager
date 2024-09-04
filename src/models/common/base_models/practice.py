# src/models/common/base_models/practice.py
from src.utils import default as default_utils

class PracticeBaseDataModel:
    def __init__(self, api_key, **kwargs):
        self.api_key = api_key
        self.address = kwargs.get('address')
        self.lat = kwargs.get('lat')
        self.lng = kwargs.get('lng')
    
    def search_in_google_places(self, name, lat, lng):
        """
        Search for a place using Google Nearby Places API based on lat/lng.
        """
        place_type = 'hospital|clinic|dentist|doctor'
        nearby_places_url = (
            f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            f"?location={lat},{lng}&radius=5000&type={place_type}&keyword={name}&key={self.api_key}"
        )
        
        places_search = default_utils.make_request(
            url=nearby_places_url, api_key=self.api_key, method='GET', headers={'Content-Type': 'application/json'}
        )
        
        if places_search.get('status') == 'OK' and places_search.get('results'):
            # Matching the name to find the correct place
            for place in places_search.get('results'):
                if name.lower() in place.get('name', '').lower():
                    return place
        return None  # Return None if no matching place is found
    
    def get_city_center_coordinates(self, city_name):
        """
        Get city center coordinates using Google Geocoding API if lat/lng are unavailable.
        """
        geocode_url = f'https://maps.googleapis.com/maps/api/geocode/json?address={city_name}&key={self.api_key}'
        geocode_search = default_utils.make_request(
            url=geocode_url, api_key=self.api_key, method='GET', headers={'Content-Type': 'application/json'}
        )

        print('Geocode Search:', geocode_search)
        
        if geocode_search.get('status') == 'OK' and geocode_search.get('results'):
            lat = geocode_search['results'][0]['geometry']['location']['lat']
            lng = geocode_search['results'][0]['geometry']['location']['lng']
            return lat, lng
        else:
            raise ValueError(f"Unable to fetch city center coordinates for {city_name}")
