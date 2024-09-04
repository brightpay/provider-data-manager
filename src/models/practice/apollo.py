import json
import boto3
from src.config import Config
from src.models.common.base_models.practice import PracticeBaseDataModel

s3_client = boto3.client('s3')
bucket_name = Config.S3_BUCKET
city_center_file_key = "apollo/static/city_center_lat_lng.json"

class ApolloPracticeDataModel(PracticeBaseDataModel):
    def __init__(self, provider_id, practice):
        super().__init__(Config.API_KEYS['GOOGLE_GEO_KEY'])
        self.provider_id = provider_id
        self.practice = practice

    def __repr__(self):
        return f"<ApolloPracticeDataModel provider_id={self.provider_id}>"

    def process_data(self):
        address = self.practice.get('hospitalAddress')
        lat = self.practice.get('HosptialLatitude')
        lng = self.practice.get('HosptialLongitude')
        city_id = str(self.practice.get('cityId'))

        if lat == "0" or lng == "0":
            # Check S3 for city center coordinates
            lat, lng = self.get_city_center_from_s3(city_id)
            if lat is None or lng is None:
                # Get city center coordinates from Google if not found in S3
                lat, lng = self.get_city_center_coordinates(self.practice.get('cityName'))
                # Store the newly fetched coordinates in S3 for future use
                self.update_city_center_in_s3(city_id, lat, lng)

        # Use base model's method to search in Google Places
        google_place_details = self.search_in_google_places(self.practice.get('hospitalName'), lat, lng)
        print('Google Place Details:', google_place_details)

        return {
            'name': self.practice.get('hospitalName'),
            'type': 'hospital' if self.practice.get('hospitalType') == "1" else "clinic" if self.practice.get('hospitalType') == "2" else 'other',
            'city': self.practice.get('cityName'),
            'address': self.practice.get('HosptialAddress'),
            'google_place_details': google_place_details
        }

    def get_city_center_from_s3(self, city_id):
        """
        Fetch city center coordinates from S3 file by cityId.
        """
        try:
            response = s3_client.get_object(Bucket=bucket_name, Key=city_center_file_key)
            city_center_data = json.loads(response['Body'].read().decode('utf-8'))

            if city_id in city_center_data:
                lat = city_center_data[city_id]['lat']
                lng = city_center_data[city_id]['lng']
                return lat, lng
        except s3_client.exceptions.NoSuchKey:
            print(f"{city_center_file_key} does not exist in S3.")
        except Exception as e:
            print(f"Error fetching city center data from S3: {e}")

        return None, None

    def update_city_center_in_s3(self, city_id, lat, lng):
        """
        Update the S3 file with new city center coordinates.
        """
        try:
            # Fetch existing data
            try:
                response = s3_client.get_object(Bucket=bucket_name, Key=city_center_file_key)
                city_center_data = json.loads(response['Body'].read().decode('utf-8'))
            except s3_client.exceptions.NoSuchKey:
                city_center_data = {}

            # Add new city coordinates
            city_center_data[city_id] = {'lat': lat, 'lng': lng}

            # Upload updated data back to S3
            s3_client.put_object(
                Bucket=bucket_name,
                Key=city_center_file_key,
                Body=json.dumps(city_center_data),
                ContentType='application/json'
            )
            print(f"City center coordinates for {city_id} stored in S3.")
        except Exception as e:
            print(f"Error updating city center data in S3: {e}")
