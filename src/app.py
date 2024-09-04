import json
import logging
# from src.models import db_engine
from .processors.router import get_processor
from .services.practitioner_service import PractitionerService
from .services.practice_service import PracticeService
from .services.provider_service import ProviderService

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Define the AWS Lambda handler
def lambda_handler(event, context):
    logger.info("Received event: %s", json.dumps(event))
    
    # Extract parameters from the event
    action = event.get('action')
    data_type = event.get('data_type')
    health_system = event.get('health_system')
    pull_id = event.get('pull_id')
    
    # Validate inputs
    if not action or not pull_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Missing required parameters: action, Pull ID'})
        }
    
    try:
        if action == 'process_data':
            # Get the appropriate processor for the health system
            processor = get_processor(pull_id, data_type)
            standardized_data = processor.process()
            practitioner_service = PractitionerService()
            practice_service = PracticeService()
            provider_service = ProviderService()

            if not data_type:
                provider_service.process_and_store_provider(standardized_data)
            if data_type == 'practitioner':
                practitioner_service.process_and_store_practitioner(standardized_data)
            elif data_type == 'practice':
                practice_service.process_and_store_practice(standardized_data)
            else:
                raise ValueError(f"Unsupported data type: {data_type}")

            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'Data processed successfully'})
            }
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Invalid action'})
            }
    except Exception as e:
        logger.error("Error processing data: %s", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Internal server error'})
        }
    finally:
        # session.close()
        # db_engine.dispose()
        print('Finally block executed')
