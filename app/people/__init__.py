"""Blueprint initializer

This script initializes the 'people' blueprint
"""

from flask import Blueprint
from app.resource import required_string_field, required_number_field, boolean_field, string_field, number_field, \
    list_string_field, list_object_field
from app.db_layer.operations import get_items_from_collection_by_query, create_index


people_bp = Blueprint('people', __name__)
PEOPLE_COLLECTION_NAME = 'people'


schema = {
    "_id": required_string_field,
    "index": required_number_field,
    "guid": string_field,
    "has_died": boolean_field,
    "balance": string_field,
    "picture": string_field,
    "age": number_field,
    "eyeColor": string_field,
    "name": string_field,
    "gender": string_field,
    "company_id": number_field,
    "email": string_field,
    "phone": string_field,
    "address": string_field,
    "about": string_field,
    "registered": string_field,
    "tags": list_string_field,
    "friends": list_object_field,
    "greeting": string_field,
    "favouriteFood": list_string_field,
}


def sanitize_item(items):
    """
    Performs sanitization of input data - splits favoriteForr into [fruits] and [vegetables]
    :param items: items to sanitize
    :return:
    """
    fruits = [f['name'] for f in list(get_items_from_collection_by_query('fruits', {}))]
    vegetables = [v['name'] for v in list(get_items_from_collection_by_query('vegetables', {}))]
    for item in items:
        for food in (item.get('favouriteFood') or []):
            if food in fruits:
                item['fruits'] = (item.get('fruits') or []) + [food]
            elif food in vegetables:
                item['vegetables'] = (item.get('vegetables') or []) + [food]


def create_people_index():
    create_index('people', 'index')
    create_index('people', 'company_id')
    create_index('people', 'eyeColor')
    create_index('people', 'has_died')


def init_app(app):
    """
    Initializes app with resource specific schema map and custom sanitization functions
    :param app:
    :return:
    """
    app.config['RESOURCE_SANITIZATION_MAP']['people'] = sanitize_item
    app.config['RESOURCE_SCHEMA_MAP']['people'] = schema
    app.config['RESOURCE_INDEX_CALLBACK_MAP']['people'] = create_people_index
