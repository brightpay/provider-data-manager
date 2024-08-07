import os

class Config:
    DATABASE_URI = os.environ.get('DATABASE_URI', 'your-default-database-uri')
