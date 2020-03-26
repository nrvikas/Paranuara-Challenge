"""MongoDB Initializer

This script abstracts implmentation details and provides interface for DB operations to be used by the API
"""

from functools import wraps
from flask import current_app as app


def with_collection(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        args = list(args)
        collection_name = args[0]
        args[0] = get_collection(collection_name)
        return f(*args, **kwargs)
    return decorated_function


def get_collection(collection_name):
    """
    Common utility function to return the MongoDB collection requested
    """
    data_handle = app.extensions['data']
    collection = data_handle.db[collection_name]
    return collection


@with_collection
def insert_data(collection, items):
    """
    Method to insert data into a collection
    """
    collection.insert(items)


@with_collection
def get_item_from_collection_by_field(collection, field, value, enhance_hateoas=None):
    """
    Simple method to get an item by ID from any collection requested
    """
    result = collection.find_one({field: value}, {'_id': 0})
    if enhance_hateoas:
        enhance_hateoas(result)
    return result


@with_collection
def get_items_from_collection_by_query(collection, query, enhance_hateoas=None):
    """
    Simple method to get an item by ID from any collection requested
    """
    result = list(collection.find(query, {'_id': 0}))
    if enhance_hateoas:
        enhance_hateoas(result)
    return result


@with_collection
def empty_collection(collection):
    if collection:
        collection.remove({})


def empty_and_insert_into_collection(collection_name, items):
    # Empty collection
    empty_collection(collection_name)

    if app.config['RESOURCE_INDEX_CALLBACK_MAP'].get(collection_name):
        app.config['RESOURCE_INDEX_CALLBACK_MAP'][collection_name]()

    # Insert to DB
    insert_data(collection_name, items)


@with_collection
def get_items_from_collection_by_aggregation(collection, pipeline):
    """
    Method to get data from collection based on aggregation
    """
    return collection.aggregate(pipeline)


@with_collection
def create_index(collection, index_name):
    collection.create_index(index_name)
