# src/processors/apollo_processor.py
import json
import boto3

from src.config import Config
from .common.base_processor import ProviderBaseProcessor
from src.models.common.practitioner import Practitioner as DefaultPractitionerModel
from src.models.common.practice import Practice as DefaultPracticeModel
from src.models.common.provider import Provider as DefaultProviderModel
from src.models.common.provider_relation import ProviderRelation as DefaultProviderRelationModel

s3_client = boto3.client('s3')
bucket_name = Config.S3_BUCKET

class FortisProviderProcessor(ProviderBaseProcessor):
    def __init__(self, timestamp, data_type):
        self.timestamp = timestamp
        self.data_type = data_type
    
    def process(self):
        print('TimeStamp:', self.timestamp)
        s3_prefix = f'apollo/datapulls/{self.timestamp}/by_city/'
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=s3_prefix)

        if 'Contents' in response:
            for obj in response['Contents']:
                s3_key = obj['Key']
                city_name = s3_key.split('/')[-1].replace('.json', '')
                city_data = s3_client.get_object(Bucket=bucket_name, Key=s3_key)['Body'].read().decode('utf-8')
                city_data = json.loads(city_data)
                print(f"Processing data for city {city_name}")
                print(city_data.keys())
        else:
            print("No objects found in the specified path.")

        practitioners = city_data.get('doctors', [])
        practices = city_data.get('hospitals', [])
        for _practitioner in practitioners:
            self._process_practitioner(_practitioner)
        for _practice in practices:
            self._process_practice(_practice)

    def _process_practitioner(self, practitioner_data):
        # Custom processing logic specific to Apollo health system
        provider_id = self._generate_provider_id(practitioner_data['doctorId'])
        practitioner = Practitioner(
            provider_id=provider_id,
            name=practitioner_data['doctorName'],
            # additional fields...
        )
        self.save_to_db(practitioner)

    def _process_practice(self, practice_data):
        # Custom processing logic specific to Apollo health system
        practice = Practice(
            name=practice_data['practiceName'],
            address=practice_data['practiceAddress'],
            # additional fields...
        )
        self.save_to_db(practice)
