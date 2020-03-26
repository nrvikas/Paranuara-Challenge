from functools import wraps
from flask import jsonify
from app.utils import get_index_value_error


def int_index(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if kwargs and kwargs.get('id'):
            try:
                kwargs['id'] = int(kwargs['id'])
            except ValueError:
                return jsonify(get_index_value_error()), 400
        return f(*args, **kwargs)
    return decorated_function
