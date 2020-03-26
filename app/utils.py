from pathlib import Path
from app.settings import GLOBAL_ID_FIELD
from distutils.util import strtobool
from flask import current_app as app
from app.db_layer.operations import get_collection, get_items_from_collection_by_query
from collections import Counter


def validate_and_get_file(absolute_file_path):
    """
        This methods validates a file path and returns the Path object to it or an appropriate error message
    """
    if not absolute_file_path.endswith('.json'):
        print('Only \'.json\' files are accepted.')
        return False

    file_path = Path(absolute_file_path)
    if not file_path.exists():
        print('File {} does not exist.'.format(absolute_file_path))
        return False

    return file_path


def validate_and_sanitize_item(item, schema, errors):
    """
        This methods validates an item according to its schema mapping
        It also sanitizes by removing fields not present in the item's schema
    """
    for field, field_description in schema.items():
        index = item.get(GLOBAL_ID_FIELD, 'Unknown Index')

        if field_description.get('required') and field not in item:
            errors.append(' ''{}'': ''{}'' field not present in the JSON description'.format(index, field))
            continue

        if field_description['type'] == 'number':
            try:
                item[field] = int(item[field])
            except ValueError:
                errors.append(' \'{}\': \'{}\' value not a number'.format(index, field))

        if field_description['type'] == 'boolean':
            try:
                item[field] = bool(strtobool(str(item[field])))
            except ValueError:
                errors.append(' \'{}\': \'{}\' value not a boolean value'.format(index, field))

        if field_description['type'] == 'list' and not isinstance(item[field], list):
            errors.append(' \'{}\': \'{}\' value not a list'.format(index, field))

    fields_to_remove = list(item.keys() - schema.keys())
    fields_to_remove.append('_id')  # _id is generated from MongoDB automatically
    for field_to_remove in fields_to_remove:
        item.pop(field_to_remove, None)


def validate_collection_data(collection, items):
    """
        This methods uses other utility functions for validation of input data
        It also prints any error messages during validation
    """
    rv = True
    errors = []
    for item in items:
        # Validate input
        validate_and_sanitize_item(item, app.config['RESOURCE_SCHEMA_MAP'][collection],
                                   errors)

    #  Call custom sanitization:
    if app.config['RESOURCE_SANITIZATION_MAP'].get(collection):
        app.config['RESOURCE_SANITIZATION_MAP'][collection](items)

    if errors:
        print('ERROR')
        print(errors)
        rv = False

    return rv


def validate_collection_dependencies(collection_name):
    rv = True
    if collection_name == 'people':
        if get_collection('fruits').count() == 0:
            print('Dependency collection \'fruits\' empty')
            rv = False

        if get_collection('vegetables').count() == 0:
            print('Dependency collection \'vegetables\' empty')
            rv = False

        if get_collection('companies').count() == 0:
            print('Dependency collection \'companies\' empty')
            rv = False

    return rv


def validate_data_dependencies(collection_name, items):
    indexes = [i.get(GLOBAL_ID_FIELD) for i in items if i.get(GLOBAL_ID_FIELD)]
    if indexes:
        duplicates = [k for k, v in Counter(indexes).items() if v > 1]
        if duplicates:
            print('ERROR: There are duplicate indexes in the imported data: {}'.format(duplicates))
            return False

    if collection_name == 'people':
        companies = [c['index'] for c in list(get_items_from_collection_by_query('companies', {}))]
        missing_companies = []
        for item in items:
            if item.get('company_id') and item['company_id'] not in companies \
                    and item['company_id'] not in missing_companies:
                missing_companies.append(item['company_id'])

        if missing_companies:
            print('ERROR: Referenced companies with these indexes are missing: {}'.format(missing_companies))
            return False

    return True


def get_error(message, type, code, title, detail):
    return {
        "error": {
            "message": message,
            "type": type,
            "code": code,
            "error_title": title,
            "error_msg": detail,
        }
    }


def get_server_error():
    return get_error("Exception occured", "Exception", 500, "Server Error",
                     "There was a server side exception while procesing your request")


def get_index_value_error():
    return get_error("Wrong Index", "ValueError", 404, "Invalid Index",
                     "Not a valid index. Must be a number.")
