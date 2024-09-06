# src/models/practice/apollo.py
from src.models.common.base_models.practice import PracticeBaseDataModel
from src.services.practice import PracticeService
from src.config import Config

class ApolloPracticeDataModel(PracticeBaseDataModel):
    def __init__(self, provider_id, practice):
        super().__init__(Config.API_KEYS['GOOGLE_GEO_KEY'])
        self.provider_id = provider_id
        self.practice = practice

    def __repr__(self):
        return f"<ApolloPracticeDataModel provider_id={self.provider_id}>"

    def process_data(self):
        # Apollo-specific logic for processing the data (if any)
        address = self.practice.get('hospitalAddress')
        lat = self.practice.get('HosptialLatitude')
        lng = self.practice.get('HosptialLongitude')
        city_id = str(self.practice.get('cityId'))

        # Use common methods from PracticeBaseDataModel
        lat, lng = self.handle_lat_lng(lat, lng, city_id, self.practice.get('cityName'))

        # Use base method to search in Google Places
        google_place_search_results = PracticeService.search_in_google_places(
            self.practice.get('hospitalName'), lat, lng, Config.API_KEYS['GOOGLE_GEO_KEY']
        )
        PracticeService.save_geo_search_results('apollo', self.practice.get('hospitalId'), google_place_search_results)
        print('Google Place Details:', google_place_search_results)

        return {
            'name': self.practice.get('hospitalName'),
            'type': 'hospital' if self.practice.get('hospitalType') == "1" else "clinic" if self.practice.get('hospitalType') == "2" else 'other',
            'city': self.practice.get('cityName'),
            'address': self.practice.get('HosptialAddress')
        }
