# src/models/practice/apollo.py
from src.models.common.base_models.practice import PracticeBaseDataModel
from src.services.practice import PracticeService
from src.services.googlemaps import GoogleMapsService
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

       # Use common practice search and processing logic from PracticeBaseDataModel
        search_results = self.process_practice_search(_practice)

        if search_results:
            print('Processed Data:', search_results)
            search_results.pop('name', None)
            search_results.pop('address', None)
            search_results.pop('city', None)
            _practice.update(search_results)
        else:
            print(f"Processing completed for {_practice.get('name')} without any valid results.")

        return _practice
