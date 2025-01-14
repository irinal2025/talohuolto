import os
from datetime import datetime
import pytz

basedir = os.path.abspath(os.path.dirname(__file__))
helsinki_tz = pytz.timezone('Europe/Helsinki')

def get_datetime(tz=helsinki_tz, format='%Y-%m-%d %H:%M:%S'):
    current_time = datetime.now(tz).strftime(format)
    print("current_time: " + current_time)
    return current_time

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT') or 'my_unique_salt'
    #MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.googlemail.com')
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    FLASKY_MAIL_SUBJECT_PREFIX = '[TaloHuolto]'
    #FLASKY_MAIL_SENDER = 'TaloHuolto Admin <flasky@example.com>'
    FLASKY_MAIL_SENDER = 'projektitori@gmail.com'
    MAIL_DEFAULT_SENDER = FLASKY_MAIL_SENDER
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
    TALOHUOLTO_ADMIN = os.environ.get('TALOHUOLTO_ADMIN')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CORS_HEADERS = 'Content-Type'
    GET_TIME = get_datetime

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'sqlite://'
    WTF_CSRF_ENABLED = False


class XamppConfig(Config):
    DEBUG = True
    DB_USERNAME= os.environ.get('DB_USERNAME') or 'root'
    DB_PASSWORD= os.environ.get('DB_PASSWORD') or ''
    DB_HOST= os.environ.get('DB_HOST') or 'localhost'
    DB_PORT= os.environ.get('DB_PORT') or '3306'
    DB_NAME= os.environ.get('DB_NAME') or 'talohuolto'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://'+DB_USERNAME+':'+DB_PASSWORD+'@'+DB_HOST+':'+DB_PORT+'/'+DB_NAME
    print("SQLALCHEMY_DATABASE_URI: "+SQLALCHEMY_DATABASE_URI)

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'data.sqlite')


#class ProductionConfig(XamppConfig):
#    DEBUG = False
#    DIR = '/home'
    #KUVAPOLKU = os.path.join(DIR, Config.UPLOAD_FOLDER)

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'xampp': XamppConfig,
    #'default': DevelopmentConfig
    'default': XamppConfig
}