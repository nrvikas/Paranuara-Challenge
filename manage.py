"""App runner

This script takes a Flask app runs it on the host and port as provided by the setting of this application
"""
from flask_script import Manager
from app import create_app
from app.db_layer.operations import empty_and_insert_into_collection
from app.utils import validate_and_get_file, validate_collection_data, validate_collection_dependencies, \
    validate_data_dependencies
import json
import os

valid_collections = ['companies', 'people', 'fruits', 'vegetables']

app = create_app
manager = Manager(app)


@manager.command
def purge_and_import_collection(collection_name, absolute_file_path):
    if collection_name not in valid_collections:
        print('ERROR: Invalid collection name. Should be one of the following: {}'.format(valid_collections))
        return False

    if not validate_collection_dependencies(collection_name):
        return False

    try:
        file_path = validate_and_get_file(absolute_file_path)
        if not file_path:
            return False

        with file_path.open('r') as f:
            # Load data
            items = json.loads(f.read())

            if not validate_data_dependencies(collection_name, items):
                return False

            # Validate input
            if not validate_collection_data(collection_name, items):
                return False

            # Perform DB Operations
            empty_and_insert_into_collection(collection_name, items)
            print('Success')
            return True
    except Exception as ex:
        print('Error loading {} to DB: {}'.format(file_path, ex))
        return False


@manager.command
def initialze_data_from_directory(directory_path):
    try:
        errored = False
        required_files = ['fruits.json', 'vegetables.json', 'companies.json', 'people.json']
        dir_files = os.listdir(directory_path)
        for required_file in required_files:
            if required_file not in dir_files:
                errored = True
                print('ERROR: {} file missing'.format(required_file))

        if errored:
            return

        for required_file in required_files:
            if not purge_and_import_collection(required_file.replace('.json', ''), '{}/{}'.format(directory_path,
                                                                                                  required_file)):
                return

    except Exception as e:
        print('ERROR: Error loading files from directory. {}'.format(e))


if __name__ == "__main__":
    manager.run()
