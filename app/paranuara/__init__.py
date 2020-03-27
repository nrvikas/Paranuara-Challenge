"""Blueprint initializer

This script initializes the 'paranuara' blueprint
"""

from flask import Blueprint

paranuara_bp = Blueprint('paranuara', __name__)

from app.paranuara.views import paranuara_index  # noqa
