# src/services/practice.py
import json
import boto3
from src.config import Config
from src.utils import default as default_utils, sql as sql_utils

s3_client = boto3.client('s3')
bucket_name = Config.S3_BUCKET


class GoogleMapsService:

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
            raise ValueError(
                f"Unable to fetch city center coordinates for {city_name}")

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
            return places_search['results']
        return []

    @staticmethod
    def get_google_place_details_to_cache(place_id, api_key):
        """
        Cache the Google Place Details in MySQL DB
        """
        place_details = default_utils.make_request(
            url=f"https://maps.googleapis.com/maps/api/place/details/json?placeid={place_id}&key={Config.API_KEYS['GOOGLE_GEO_KEY']}",
            api_key={api_key}, method='GET', headers={'Content-Type': 'application/json'}
        )
        place_hours_to_insert = []
        photos_to_insert = []
        reviews_to_insert = []
        columns = ['place_id', 'business_status', 'formatted_phone_number', 'international_phone_number',
                   'name', 'rating', 'reference', 'url', 'user_ratings_total', 'utc_offset', 'vicinity', 'website']
        if place_details.get('result'):
            place_obj = {}
            for _col in columns:
                if place_details['result'].get(_col):
                    if isinstance(place_details['result'][_col], str):
                        place_obj.update(
                            {_col: place_details['result'][_col].replace("'", "''")})
                    else:
                        place_obj.update({_col: place_details['result'][_col]})
                else:
                    place_obj.update({_col: None})

            if place_details.get('result').get('opening_hours'):
                for _opening_hour in place_details['result']['opening_hours'].get('periods', []):
                    place_hours_to_insert.append({
                        'place_id': place_id,
                        'day': _opening_hour['open']['day'],
                        'open': _opening_hour['open']['time'],
                        'close': _opening_hour.get('close', {}).get('time')
                    })
                if place_details.get('result').get('opening_hours').get('weekday_text'):
                    place_obj.update({
                        'opening_hours_text': '|'.join(place_details['result']['opening_hours']['weekday_text'])
                    })
                else:
                    place_obj.update({'opening_hours_text': None})
            else:
                place_obj.update({'opening_hours_text': None})

            if place_details.get('result').get('photos'):
                for _photo in place_details['result']['photos']:
                    photos_to_insert.append({
                        'place_id': place_id,
                        'height': _photo['height'],
                        'width': _photo['width'],
                        'contributor': _photo['html_attributions'][0].split('>')[1].split('<')[0].replace("'", "''") if (_photo.get('html_attributions') and len(_photo['html_attributions']) > 0 and '<' in _photo['html_attributions'][0] and '>' in _photo['html_attributions'][0]) else None,
                        'photo_reference': _photo['photo_reference'],
                    })

            if place_details.get('result').get('reviews'):
                for _review in place_details['result']['reviews']:
                    reviews_to_insert.append({
                        'place_id': place_id,
                        'author': _review['author_name'].replace("'", "''") if _review.get('author_name') else None,
                        'language': _review.get('language'),
                        'text': _review['text'].replace("'", "''") if _review.get('text') else None,
                        'rating': _review['rating'],
                        'time': _review['time']
                    })

        return {
            'place': place_obj,
            'hours': place_hours_to_insert,
            'photos': photos_to_insert,
            'reviews': reviews_to_insert
        }
