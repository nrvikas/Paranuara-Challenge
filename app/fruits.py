from app.resource import required_string_field

schema = {
    'name': required_string_field
}


def init_app(app):
    app.config['RESOURCE_SCHEMA_MAP']['fruits'] = schema
