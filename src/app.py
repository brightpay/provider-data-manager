import json
import logging
import boto3
from processors import practitioner_processor, practice_processor

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Define the AWS Lambda handler
def lambda_handler(event, context):
    logger.info("Received event: %s", json.dumps(event))
    
    # Extract parameters from the event
    action = event.get('action')
    data_type = event.get('data_type')
    
    if action == 'process_data':
        if data_type == 'practitioner':
            practitioner_processor.process_data(event['data'])
        elif data_type == 'practice':
            practice_processor.process_data(event['data'])
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
