import os

class Config:
    DATABASE_URI = os.environ.get('DATABASE_URI', 'your-default-database-uri')
    S3_BUCKET = os.environ.get('S3_BUCKET', 'provider-data.brighthealth.in')
    API_KEYS = {
        'GOOGLE_GEO_KEY': os.environ.get('GOOGLE_GEO_KEY', ''),
        'apollo': os.environ.get('APOLLO_AUTH_TOKEN', ''),
        'fortis': os.environ.get('FORTIS_API_KEY', ''),
        'manipal': os.environ.get('MANIPAL_API_KEY', ''),
        'medanta': os.environ.get('MEDANTA_API_KEY', ''),
        'maxhealthcare': os.environ.get('MAX_API_KEY', ''),
        'aster': os.environ.get('ASTER_API_KEY', ''),
        'singhealth': os.environ.get('SINGHEALTH_API_KEY', ''),
        'parkway': os.environ.get('PARKWAY_API_KEY', ''),
        'nuhs': os.environ.get('NUHS_API_KEY', ''),
    }
