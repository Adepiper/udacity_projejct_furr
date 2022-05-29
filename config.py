import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# TODO IMPLEMENT DATABASE URL
# DONE IMPLEMENT DATABASE URL


class Config(object):
    DEBUG = True
    TESTING = True
    CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI=os.environ.get("DATABASE_URL")


class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI=os.environ.get("DATABASE_URL")


class TestingConfig(Config):
    TESTING = True


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': Config,
    'testing': TestingConfig
}