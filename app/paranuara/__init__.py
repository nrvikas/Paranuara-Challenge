"""Blueprint initializer

This script initializes the 'paranuara' blueprint
"""

from flask import Blueprint, render_template
paranuara_bp = Blueprint('paranuara', __name__)


@paranuara_bp.route('/')
def paranuara_index():
    """
    Default landing page with API documentation
    """
    return render_template('index.html')
