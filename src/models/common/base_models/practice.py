# src/models/common/base_models/practice.py
from src.services.practice import PracticeService

class PracticeBaseDataModel:
    def __init__(self, api_key):
        self.api_key = api_key

    def handle_lat_lng(self, lat, lng, city_id, city_name):
        """
        Handle logic to either fetch lat/lng from S3 or Google API.
        """
        if lat == "0" or lng == "0":
            # Check S3 for city center coordinates
            lat, lng = PracticeService.get_city_center_from_s3(city_id)
            if lat is None or lng is None:
                # Get city center coordinates from Google if not found in S3
                lat, lng = PracticeService.get_city_center_coordinates(city_name, self.api_key)
                # Store the newly fetched coordinates in S3 for future use
                PracticeService.update_city_center_in_s3(city_id, lat, lng)

        return lat, lng
    
    def match_geo_search_results(self, practice, geo_search_results):
        """
        Match the geo search results with the practice data.
        """
        pass
