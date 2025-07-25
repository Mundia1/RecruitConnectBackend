import os
from dotenv import load_dotenv

load_dotenv()  

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SENTRY_DSN = os.getenv('SENTRY_DSN', '')  

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///' + os.path.join(basedir, 'dev.db'))

class TestingConfig(Config):
    TESTING = True

    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_TEST_URL', 'sqlite:///:memory:')

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_DATABASE_URL')
    CELERY_BROKER_URL = os.getenv('TEST_CELERY_BROKER_URL', 'redis://localhost:6379/1')
    CELERY_RESULT_BACKEND = os.getenv('TEST_CELERY_RESULT_BACKEND', 'redis://localhost:6379/2')
    RATELIMIT_STORAGE_URL = os.getenv('TEST_RATELIMIT_STORAGE_URL', 'redis://localhost:6379/4')
    TALISMAN_FORCE_HTTPS = False
    CELERY_ALWAYS_EAGER = True
    
    def __init__(self):
        if not self.SQLALCHEMY_DATABASE_URI:
            raise ValueError('No TEST_DATABASE_URL set for testing environment')
        super().__init__()

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')

config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}

if os.getenv('TEST_DATABASE_URL'):
    config_by_name['testing'] = TestingConfig
