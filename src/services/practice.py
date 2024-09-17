# src/services/practice.py
import json
import boto3
from src.config import Config
from src.utils import default as default_utils, sql as sql_utils
from src.services.googlemaps import GoogleMapsService

s3_client = boto3.client('s3')
bucket_name = Config.S3_BUCKET

class PracticeService:
    @staticmethod
    def save_practice(practice_data):
        # Save the practice to the database (example method)
        pass
    
    @staticmethod
    def save_geo_search_results(practice_id, data, health_system=None, directory=None):
        """
        Log the results of geo search in a database table.
        """
        places_to_insert = []
        for _result in data:
            geocode_data = {
                'directory': directory,
                'health_system': health_system,
                'practice_id': practice_id,
                'lat': _result['geometry']['location']['lat'],
                'lng': _result['geometry']['location']['lng'],
                'name': _result['name'].replace("'","''"),
                'place_id': _result['place_id'],
                'plus_code': _result.get('plus_code',{}).get('global_code'),
                'rating': _result.get('rating'),
                'user_ratings_total': _result.get('user_ratings_total'),
                'vicinity': _result['vicinity'].replace("'","''"),
                'place_types': '|'.join(_result['types'])
            }
            places_to_insert.append(geocode_data)
        sql_utils.bulk_insert('provider_connector.practice_google_places_search_results', places_to_insert)

    @staticmethod
    def cache_google_place_details(place_id, api_key):
        """
        Cache the Google Place Details in MySQL DB
        """
        google_place_details = GoogleMapsService.get_google_place_details_to_cache(place_id, api_key)
        print(f"Google Place Details: {google_place_details}")
        if google_place_details:
            sql_utils.bulk_insert('bright.google_place_details_cache', [google_place_details['place']])
            sql_utils.bulk_insert('bright.google_place_opening_hours', google_place_details['hours'])
            sql_utils.bulk_insert('bright.google_place_photos', google_place_details['photos'])
            sql_utils.bulk_insert('bright.google_place_reviews', google_place_details['reviews'])

        return

    @staticmethod
    def save_geo_match_exceptions(practice_id, exception, practice_data, geo_results, health_system=None, directory=None):
        """
        Log the results of geo search in a database table.
        """
        exception_base_data = {
            'directory': directory,
            'health_system': health_system,
            'practice_id': practice_id,
            'exception': exception,
            'practice_data': json.dumps(practice_data),
            'lat': practice_data.get('lat'),
            'lng': practice_data.get('lng'),
            'name': practice_data.get('name'),
            'city': practice_data.get('city'),
            'address': practice_data.get('address'),
        }
        if exception == 'no_results':
            sql_utils.bulk_insert('provider_connector.practice_geo_match_exceptions', [exception_base_data])
        

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
