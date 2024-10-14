# Provider Data Manager

## Overview
The Provider Data Manager is responsible for processing healthcare provider data collected from various health systems. It standardizes, stores, and processes practitioner, practice, and provider details to integrate into a healthcare ecosystem.

## Key Components

### 1. Processors
Processors handle the extraction, transformation, and loading (ETL) of data from different sources. They are responsible for converting raw data into a unified, structured format that can be stored in a database.

### 2. Models
Models represent the data entities, such as providers, practitioners, and practices. They define the structure of these entities for the purpose of data processing and interaction.

### 3. Services
Services provide utility functions that support different processes. These include interactions with external APIs (e.g., Google Places API), handling file operations, and connecting to the database for CRUD operations.

## How It Works
Upon receiving an input, like:

```json
{
  "pull_id": "f3e51f05-6517-4099-b216-d7850fd6a418",
  "action": "process_data"
}
```

The system performs the following:

1. **Identify the Action**: Based on `"action": "process_data"`, it identifies that data processing is required.
2. **Invoke the Processor**: The appropriate processor is invoked to handle the processing of the data associated with the provided `"pull_id"`.
3. **Data Transformation**: The processor extracts data, standardizes it, and makes it ready for further storage or usage.

## Setup Instructions

### Setting Up Virtual Environment
To set up a virtual environment and install necessary dependencies:

```bash
python3.12 -m venv provider-data-manager
source provider-data-manager/venv/bin/activate
pip install -r requirements.txt
```

### Deploying to AWS Lambda
To deploy the provider data manager to AWS Lambda:

```bash
rm -rf provdatamgr.zip
zip -r "provdatamgr.zip" *
aws lambda update-function-code --function-name provider-data-manager --region ap-south-1 --zip-file "fileb://provdatamgr.zip"
```

## Directory Structure

- **src/**: Contains all the source code for models, processors, services, and utilities.
- **README.md**: Documentation for setting up and using the application.
- **directory_structure.md**: Describes the organization of the repository files.

---

## Step-by-Step Flow

### Entry Point (Lambda Handler - app.py)

1. **Lambda Handler**: The `lambda_handler` function receives the input and extracts the following key parameters:
   - `action`: "process_data"
   - `pull_id`: "f3e51f05-6517-4099-b216-d7850fd6a418"

2. If the `action` is "process_data", it calls the `get_processor` function from `router.py`.

### Routing Logic (router.py)

1. **Get Processor Function**: The `get_processor` function retrieves pull details from a SQL database using:
   ```sql
   SELECT * FROM provider_connector.data_pulls WHERE pull_id = 'f3e51f05-6517-4099-b216-d7850fd6a418'
   ```
2. **Verification**:
   - Checks whether the pull ID exists.
   - Verifies if the pull has already been processed (raises an exception if it has).
   - Extracts the relevant health system (e.g., Apollo or Fortis).
3. **Return Processor**: Based on the health system, it returns the appropriate processor class (e.g., `ApolloProviderProcessor` or `FortisProviderProcessor`).

### Processor Execution (apollo.py or fortis.py)

1. **Processor Class**: The processor class (`ApolloProviderProcessor` or `FortisProviderProcessor`) is instantiated with the timestamp and `data_type`.
2. **Data Processing**:
   - The processor fetches data from S3 using:
     ```bash
     S3 Prefix: 'apollo/datapulls/<timestamp>/by_city/'
     ```
   - If data is available, it iterates over cities and extracts data (doctors, hospitals).
   - Calls methods to process each practitioner and practice.

### Processing Practitioners and Practices

1. **Practitioner**:
   - Creates a `Provider` or `Practitioner` object with relevant fields.
   - Saves it to the database.

2. **Practice**:
   - Creates a `Practice` object and processes it using custom logic.
   - Saves it to the database.

### Returning the Response (Lambda Handler)

1. If the processing completes successfully:
   ```json
   {
     "statusCode": 200,
     "body": {"message": "Data processed successfully"}
   }
   ```
2. If there’s an error during the flow, a 500 error is returned.