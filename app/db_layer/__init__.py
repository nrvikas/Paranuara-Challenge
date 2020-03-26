"""MongoDB Initializer

This script initializes the pymongo driver for the API to perform DB 0perations
"""

from flask_pymongo import PyMongo


def get_mongo():
    mongo = PyMongo()
    return mongo
