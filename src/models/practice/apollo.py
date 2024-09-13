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
        _practice = {
            'name': self.practice.get('hospitalName'),
            'type': 'hospital' if self.practice.get('hospitalType') == "1" else "clinic" if self.practice.get('hospitalType') == "2" else 'other',
            'city': self.practice.get('cityName'),
            'address': self.practice.get('HosptialAddress'),
            'city_id': self.practice.get('cityId'),
            'hospital_id': self.practice.get('hospitalId')
        }
        lat = self.practice.get('HosptialLatitude')
        lng = self.practice.get('HosptialLongitude')

        # Use common methods from PracticeBaseDataModel
        lat, lng = self.handle_lat_lng(lat, lng, _practice.get('city_id'), _practice.get('city'))

        # Use Practice Service to search in Google Places
        google_place_search_results = PracticeService.search_in_google_places(
            _practice.get('name'), lat, lng, Config.API_KEYS['GOOGLE_GEO_KEY']
        )
        if len(google_place_search_results) == 0:
            print(f"No results found for {_practice.get('name')} in Google Places API")
            PracticeService.save_geo_match_exceptions(_practice.get('hospital_id'), 'no_results', _practice, [])
            return
        
        PracticeService.save_geo_search_results(_practice.get('hospital_id'), google_place_search_results, health_system='apollo')
        print('Google Place Details:', google_place_search_results)
        self.match_geo_search_results(_practice, google_place_search_results)

        _processed = self.process_data(provider_id=self.provider_id, practice=_practice)
        print('Processed Data:', _processed)
        return _processed
