# src/services/practice.py
import json
import boto3
from src.config import Config
from src.utils import default as default_utils

s3_client = boto3.client('s3')
bucket_name = Config.S3_BUCKET

class PracticeService:
    @staticmethod
    def save_practice(practice_data):
        # Save the practice to the database (example method)
        pass

    @staticmethod
    def get_city_center_coordinates(city_name, api_key):
        """
        Get city center coordinates using Google Geocoding API if lat/lng are unavailable.
        """
        geocode_url = f'https://maps.googleapis.com/maps/api/geocode/json?address={city_name}&key={api_key}'
        geocode_search = default_utils.make_request(
            url=geocode_url, api_key=api_key, method='GET', headers={'Content-Type': 'application/json'}
        )

        if geocode_search.get('status') == 'OK' and geocode_search.get('results'):
            lat = geocode_search['results'][0]['geometry']['location']['lat']
            lng = geocode_search['results'][0]['geometry']['location']['lng']
            return lat, lng
        else:
            raise ValueError(f"Unable to fetch city center coordinates for {city_name}")

    @staticmethod
    def search_in_google_places(name, lat, lng, api_key):
        """
        Search for a place using Google Nearby Places API based on lat/lng.
        """
        place_type = 'hospital|clinic|dentist|doctor'
        nearby_places_url = (
            f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            f"?location={lat},{lng}&radius=5000&type={place_type}&keyword={name}&key={api_key}"
        )
        
        places_search = default_utils.make_request(
            url=nearby_places_url, api_key=api_key, method='GET', headers={'Content-Type': 'application/json'}
        )
        
        if places_search.get('status') == 'OK' and places_search.get('results'):
            # Matching the name to find the correct place
            for place in places_search.get('results'):
                if name.lower() in place.get('name', '').lower():
                    return place
        return None  # Return None if no matching place is found

    @staticmethod
    def get_city_center_from_s3(city_id):
        """
        Fetch city center coordinates from S3 file by cityId.
        """
        try:
            response = s3_client.get_object(Bucket=bucket_name, Key=f'apollo/static/city_center_lat_lng.json')
            city_center_data = json.loads(response['Body'].read().decode('utf-8'))

            if city_id in city_center_data:
                lat = city_center_data[city_id]['lat']
                lng = city_center_data[city_id]['lng']
                return lat, lng
        except s3_client.exceptions.NoSuchKey:
            print(f"City center data file does not exist in S3.")
        except Exception as e:
            print(f"Error fetching city center data from S3: {e}")

        return None, None

    @staticmethod
    def update_city_center_in_s3(city_id, lat, lng):
        """
        Update the S3 file with new city center coordinates.
        """
        try:
            # Fetch existing data
            try:
                response = s3_client.get_object(Bucket=bucket_name, Key=f'apollo/static/city_center_lat_lng.json')
                city_center_data = json.loads(response['Body'].read().decode('utf-8'))
            except s3_client.exceptions.NoSuchKey:
                city_center_data = {}

            # Add new city coordinates
            city_center_data[city_id] = {'lat': lat, 'lng': lng}

            # Upload updated data back to S3
            s3_client.put_object(
                Bucket=bucket_name,
                Key=f'apollo/static/city_center_lat_lng.json',
                Body=json.dumps(city_center_data),
                ContentType='application/json'
            )
            print(f"City center coordinates for {city_id} stored in S3.")
        except Exception as e:
            print(f"Error updating city center data in S3: {e}")
