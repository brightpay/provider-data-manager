from src.utils import sql as sql_utils

from src.processors.provider.apollo import ApolloProviderProcessor
from src.processors.provider.fortis import FortisProviderProcessor
# Import other health system processors as needed

def get_processor(pull_id, data_type):
    processors = {
        'apollo': ApolloProviderProcessor,
        'fortis': FortisProviderProcessor,
    }

    pull_details = sql_utils.execute_query(
        f"SELECT * FROM provider_connector.data_pulls WHERE pull_id = '%s'" % pull_id,
    )

    if len(pull_details) == 0:
        raise ValueError(f"Pull ID {pull_id} not found")

    print('info', 'Pull details:', pull_details)

    health_system = pull_details[0]['health_system'].lower()
    data_pull_processed = pull_details[0]['processed']
    timestamp = pull_details[0]['timestamp']

    if data_pull_processed:
        raise ValueError(f"Data pull {pull_id} has already been processed")

    if health_system in processors:
        print('info', 'Health system:', health_system)
        return processors[health_system](timestamp, data_type)
    else:
        raise ValueError(f"Unsupported health system: {health_system}")
