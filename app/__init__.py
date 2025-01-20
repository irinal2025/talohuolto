from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError
from flask_login import LoginManager
from flask_migrate import Migrate
from config import config, get_datetime
from flask_wtf import CSRFProtect
from flask_wtf.csrf import CSRFProtect, generate_csrf, CSRFError
import logging
import sys
from datetime import datetime
import pytz
from .filters import format_date
from flask_cors import CORS
import ssl


class FinnishFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        helsinki_tz = pytz.timezone('Europe/Helsinki')
        created_time = datetime.fromtimestamp(record.created, tz=helsinki_tz)
        return created_time.strftime(datefmt or '%Y-%m-%d %H:%M:%S')

csrf = CSRFProtect()
bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
migrate = Migrate()

db = SQLAlchemy(session_options={"autoflush": False})
login_manager = LoginManager()
login_manager.login_view = 'auth.login'


def create_app(config_name='default'):
    app = Flask(__name__)
    #CORS(app, resources={r"/reactapi/*": {"origins": "https://localhost:5173"}})  # Rajoita CORS vain React-sovellukseen
    #CORS(app, resources={r"/reactapi/*": {"origins": "http://localhost:5173"}})  # Rajoita CORS vain React-sovellukseen
    CORS(app, resources={r"/reactapi/*": {"origins": "http://localhost:5173"}}, supports_credentials=True)
    app.config.from_object(config[config_name])

    # Debug-tilan asettaminen
    app.debug = app.config['DEBUG']  # varmistaa, että debug-tila on oikein

    print("Sovellus luotiin ja Blueprint rekisteröidään...")

    # Tarkista debug-asetus
    print(f"Debug mode in create_app: {app.config['DEBUG']}")  # Tämä tulostaa debug-tilan

    # Alustetaan Migrate
    migrate = Migrate(app, db)

    # Configure the logger
    logger = app.logger  # Use Flask's built-in app logger
    # Remove any existing handlers
    logger.handlers.clear()
    logger.setLevel(logging.DEBUG)
    stderr_handler = logging.StreamHandler(sys.stderr)
    formatter = FinnishFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stderr_handler.setFormatter(formatter)
    logger.addHandler(stderr_handler)
    logger.propagate = False
    logger.info("Test log message with Helsinki time.")


    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    # db.init_app(app)
    try:
        db.init_app(app)
    except OperationalError as e:
        app.logger.error(f"VIRHE: Database connection failed: {e}")
        # Handle the error, e.g., show a user-friendly message or retry connection
        return None
    
    csrf.init_app(app)
    
    login_manager.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .reactapi import reactapi as reactapi_blueprint
    app.register_blueprint(reactapi_blueprint, url_prefix='/reactapi')

    # Suodattimen rekisteröinti
    app.jinja_env.filters['format_date'] = format_date

    return app