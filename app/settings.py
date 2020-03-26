"""App settings

This script provides settings and configuration for the Flask app
"""

import os

DB_NAME = 'paranuara'
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost/{}'.format(DB_NAME))
URL_PREFIX = '/api/v1'
HOST_ADDRESS = '127.0.0.1'
PORT = 5000
DB_ID_FIELD = '_id',
GLOBAL_ID_FIELD = 'index'
