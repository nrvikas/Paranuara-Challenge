"""Blueprint initializer

This script initializes the 'companies' blueprint
"""

from flask import Blueprint
from app.resource import required_string_field, required_number_field
from app.db_layer.operations import create_index

companies_bp = Blueprint('companies', __name__)
COMPANIES_COLLECTION_NAME = 'companies'

from app.companies.api import *  # noqa

schema = {
    'index': required_number_field,
    'company': required_string_field
}


def create_companies_index():
    create_index('companies', 'index')


def init_app(app):
    app.config['RESOURCE_SCHEMA_MAP']['companies'] = schema
    app.config['RESOURCE_INDEX_CALLBACK_MAP']['companies'] = create_companies_index
