# src/processors/provider/apollo.py:
import json
import boto3

from src.config import Config
from .common.base_processor import ProviderBaseProcessor
from src.models.common.practitioner import Practitioner as DefaultPractitionerModel
from src.models.common.practice import Practice as DefaultPracticeModel
from src.models.common.provider import Provider as DefaultProviderModel
from src.models.common.provider_relation import ProviderRelation as DefaultProviderRelationModel

from src.models.practice.apollo import ApolloPracticeDataModel

s3_client = boto3.client('s3')
bucket_name = Config.S3_BUCKET

class ApolloProviderProcessor(ProviderBaseProcessor):
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
        for _practice in practices:
            self._process_practice(_practice)
        for _practitioner in practitioners:
            self._process_practitioner(_practitioner)

    def _process_practitioner(self, practitioner_data):
        # Custom processing logic specific to Apollo health system
        provider_id = self._generate_provider_id()
        print('Provider ID:', provider_id)
        practitioner = DefaultProviderModel(provider_id, practitioner_data)
        self.save_to_db(practitioner)

    def _process_practice(self, practice):
        # Custom processing logic specific to Apollo health system
        provider_id = self._generate_provider_id()
        print('Provider ID:', provider_id)
        apollo_practice_data_model = ApolloPracticeDataModel(provider_id, practice)
        processed_practice_data = apollo_practice_data_model.process_data()
        print('Processed Practice Data:', processed_practice_data)
        practice_data_model = DefaultPracticeModel(provider_id, processed_practice_data)
        processed_practice_objects = practice_data_model.process_data()
        print('Processed Practice:', processed_practice_objects)
