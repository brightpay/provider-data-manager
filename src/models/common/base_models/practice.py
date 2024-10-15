# src/models/common/base_models/practice.py

import re
from difflib import SequenceMatcher
from src.services.practice import PracticeService
from src.services.googlemaps import GoogleMapsService

class PracticeBaseDataModel:
    def __init__(self, api_key):
        self.api_key = api_key

    def handle_lat_lng(self, lat, lng, city_id, city_name):
        """
        Handle logic to either fetch lat/lng from S3 or Google API.
        """
        if lat == "0" or lng == "0" or lat == '' or lng == '' or lat is None or lng is None:
            # Check S3 for city center coordinates
            lat, lng = PracticeService.get_city_center_from_s3(city_id)
            print('City Center from S3:', lat, lng)
            if lat is None or lng is None:
                # Get city center coordinates from Google if not found in S3
                lat, lng = GoogleMapsService.get_city_center_coordinates(city_name, self.api_key)
                # Store the newly fetched coordinates in S3 for future use
                PracticeService.update_city_center_in_s3(city_id, lat, lng)

        return lat, lng

    def process_practice_search(self, practice):
        """
        Process the Google Places search and handle different scenarios:
        - No results
        - One result
        - Multiple results
        """
        lat = practice.get('HosptialLatitude')
        lng = practice.get('HosptialLongitude')
        google_place_details = None

        lat, lng = self.handle_lat_lng(lat, lng, practice.get('city_id'), practice.get('city'))

        # Use Google Places API to search for the practice
        google_place_search_results = GoogleMapsService.search_in_google_places(
            practice.get('name'), lat, lng, self.api_key
        )

        print('Google Place Search Results:', google_place_search_results)

        if len(google_place_search_results) == 0:
            # No results found, log an exception
            PracticeService.save_geo_match_exceptions(practice.get('hospital_id'), 'no_results', practice, [])
            return None

        elif len(google_place_search_results) == 1:
            # One result found, validate if it's a valid healthcare practice
            is_valid_result = self.is_valid_practice_result(google_place_search_results[0], practice)
            print('Is Valid Result:', is_valid_result)
            if is_valid_result:
                google_place_details = self.cache_and_save_results(practice, google_place_search_results)
                best_match = google_place_search_results[0]
            else:
                # Invalid result, log an exception
                PracticeService.save_geo_match_exceptions(practice.get('hospital_id'), 'invalid_result', practice, google_place_search_results)

        else:
            # Multiple results, attempt to find the best match
            best_match = self.get_best_match(google_place_search_results, practice)
            if best_match:
                google_place_details = self.cache_and_save_results(practice, [best_match])
            else:
                # No accurate match found, log an exception
                PracticeService.save_geo_match_exceptions(practice.get('hospital_id'), 'no_accurate_match', practice, google_place_search_results)

        if not google_place_details:
            return None

        processed_place_details = {
            'lat': lat,
            'lng': lng,
            'google_place_id': google_place_details['place_id'],
            'rating': google_place_details['rating'],
            'pincode': google_place_details['pincode'],
            'route': google_place_details['route'],
            'locality': google_place_details['locality'],
            'sublocality': google_place_details['sublocality'],
            'city': google_place_details['city'],
            'state': google_place_details['state'],
            'country': google_place_details['country'],
            'address': google_place_details['address']
        }
        
        return processed_place_details

    def cache_and_save_results(self, practice, search_results):
        """
        Cache the Google Place details and save the search results.
        """
        PracticeService.save_geo_search_results(practice.get('hospital_id'), search_results)
        
        for _result in search_results:
            PracticeService.cache_google_place_details(_result.get('place_id'), self.api_key)

    def is_valid_practice_result(self, result, practice):
        """
        Check if the Google Places result is valid by matching the name and place types.
        """
        valid_types = ['hospital', 'health', 'clinic', 'dentist', 'doctor']
        place_types = result.get('types', [])

        if not any(_type in valid_types for _type in place_types):
            print('Invalid Place Type:', place_types)
            return False

        if self.compare_names(result.get('name'), practice.get('name')):
            return True
        print('Name Mismatch:', result.get('name'), practice.get('name'))
        return False

    def get_best_match(self, results, practice):
        """
        Find the best match from multiple Google Places results.
        """
        valid_types = ['hospital', 'clinic', 'dentist', 'doctor']
        best_match = None

        for result in results:
            place_types = result.get('types', [])
            name_similarity = self.compare_names(result.get('name'), practice.get('name'))

            if name_similarity and any(_type in valid_types for _type in place_types):
                best_match = result
                break

        return best_match

    def compare_names(self, google_name, practice_name):
        """
        Compare Google Places name with practice name using a more intelligent match.
        1. Token-based matching for important words (ignore common descriptors).
        2. Levenshtein distance or fuzzy string matching.
        3. Substring matching to handle variations.
        """
        # Normalize the names by removing common descriptors, special characters, and lowercasing
        practice_name_cleaned = self.clean_name(practice_name)
        google_name_cleaned = self.clean_name(google_name)

        # Check if the important tokens match (using token sets to be order-agnostic)
        if self.token_based_match(practice_name_cleaned, google_name_cleaned):
            return True
        
        # Use string similarity (Levenshtein distance or SequenceMatcher) to allow partial match
        similarity_ratio = SequenceMatcher(None, practice_name_cleaned, google_name_cleaned).ratio()
        if similarity_ratio > 0.8:  # A threshold for high similarity
            return True

        # Check if the practice name is a substring in the Google Places name or vice versa
        if practice_name_cleaned in google_name_cleaned or google_name_cleaned in practice_name_cleaned:
            return True

        return False

    def clean_name(self, name):
        """
        Clean the practice or Google name by removing common descriptors, special characters, etc.
        """
        # Remove common descriptors that don't affect the core name (e.g., 'Best', 'Multi Speciality', etc.)
        descriptors = ['best', 'multi speciality', 'hospital', 'clinic', 'center', 'centre']
        # Remove special characters and convert to lowercase
        name = re.sub(r'[^\w\s]', '', name.lower())

        # Remove common descriptors
        name_tokens = name.split()
        cleaned_tokens = [token for token in name_tokens if token not in descriptors]

        # Return the cleaned name as a single string
        return ' '.join(cleaned_tokens)

    def token_based_match(self, practice_name, google_name):
        """
        Token-based matching of important words between practice name and Google name.
        """
        practice_tokens = set(practice_name.split())
        google_tokens = set(google_name.split())

        # Check for token overlap, ensuring that at least 70% of the tokens match
        common_tokens = practice_tokens.intersection(google_tokens)
        if len(common_tokens) / len(practice_tokens) > 0.7:
            return True

        return False

    def process_data_structure(self, provider_id, practice):
        """
        Process the practice data into structured object form (provider, practice, meta mappings).
        """
        # Assuming the Practice class exists in a separate module and processes data as requested
        from src.models.common.practice import Practice  # Adjust the import as necessary

        practice_processor = Practice(provider_id, practice)
        return practice_processor.process_data()
