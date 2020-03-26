"""App Initializer

This script
    1 - creates a Flask app.
    2 - instantiates and stores the database driver for the MongoDB
    3 - registers the blueprints of the application
    4 - initializes all core apps
"""

from flask import Flask
from app.paranuara import paranuara_bp
from app.companies import companies_bp
from app.people import people_bp
from app.db_layer import get_mongo
import importlib

core_apps = ['app.companies', 'app.people', 'app.fruits', 'app.vegetables']


def create_app(config_object='app.settings', config=None):
    app = Flask(__name__)
    app.config.from_object(config_object)

    if config:
        app.config.update(config or {})

    # Initialise DB
    mongo = get_mongo()
    mongo.init_app(app)
    app.extensions['data'] = mongo # handle for the DB Operations

    # Register all Blueprints
    app.register_blueprint(paranuara_bp)
    app.register_blueprint(companies_bp)
    app.register_blueprint(people_bp)

    if not app.config.get('RESOURCE_SANITIZATION_MAP'):
        app.config['RESOURCE_SANITIZATION_MAP'] = {}

    if not app.config.get('RESOURCE_SCHEMA_MAP'):
        app.config['RESOURCE_SCHEMA_MAP'] = {}

    if not app.config.get('RESOURCE_INDEX_CALLBACK_MAP'):
        app.config['RESOURCE_INDEX_CALLBACK_MAP'] = {}

    for core_app in core_apps:
        mod = importlib.import_module(core_app)
        if hasattr(mod, 'init_app'):
            mod.init_app(app)

    return app
