from pathlib import Path
from bson import ObjectId
from manage import purge_and_import_collection, valid_collections
from app.db_layer.operations import get_item_from_collection_by_field
import json

root = (Path(__file__).parent / 'test_files').resolve()


def test_get_wrong_person_index(client, app, capsys):
    with app.app_context():
        purge_and_import_collection('fruits', '{}/fruits.json'.format(root))
        purge_and_import_collection('vegetables', '{}/vegetables.json'.format(root))
        purge_and_import_collection('people', '{}/people.json'.format(root))
        captured = capsys.readouterr()
        assert 'Success' in captured.out

        resp = client.get('/api/v1/people/123456789/favourite_food', headers={'Accept': 'application/json'})
        assert 404 == resp.status_code


def test_get_successful_data(client, app, capsys):
    with app.app_context():
        purge_and_import_collection('companies', '{}/companies.json'.format(root))
        purge_and_import_collection('fruits', '{}/fruits.json'.format(root))
        purge_and_import_collection('vegetables', '{}/vegetables.json'.format(root))
        purge_and_import_collection('people', '{}/people.json'.format(root))
        captured = capsys.readouterr()
        assert 'Success' in captured.out
        person = get_item_from_collection_by_field('people', 'index', 943)
        assert "orange" in person['fruits']
        assert "banana" in person['fruits']
        assert "beetroot" in person['vegetables']
        assert "celery" in person['vegetables']

        resp = client.get('/api/v1/people/943/liked_food', headers={'Accept': 'application/json'})
        assert 200 == resp.status_code
        resp_data = json.loads(resp.data.decode('utf-8'))
        assert {'age', 'fruits', 'username', 'vegetables', '_links'} == set(resp_data.keys())
        assert resp_data['age'] == 59
        assert set(resp_data['fruits']) == set(['orange', "banana"])
        assert resp_data['username'] == "Mullen Jennings"
        assert set(resp_data['vegetables']) == set(["beetroot", "celery"])


def test_get_common_special_friends(client, app, capsys):
    with app.app_context():
        purge_and_import_collection('companies', '{}/companies.json'.format(root))
        purge_and_import_collection('fruits', '{}/fruits.json'.format(root))
        purge_and_import_collection('vegetables', '{}/vegetables.json'.format(root))
        purge_and_import_collection('people', '{}/people.json'.format(root))
        captured = capsys.readouterr()
        assert 'Success' in captured.out
        resp = client.get('/api/v1/people/special_friends?person_1={}&person_2={}'.format(1, 2),
                          headers={'Accept': 'application/json'})
        assert 200 == resp.status_code
        resp_data = json.loads(resp.data.decode('utf-8'))
        assert {'common_brown_eyed_alive_friends', 'people'} == set(resp_data.keys())
        assert resp_data['people'][0]['address'] == '492 Stockton Street, Lawrence, Guam, 4854'
        assert resp_data['people'][0]['age'] == 60
        assert resp_data['people'][0]['name'] == "Decker Mckenzie"
        assert resp_data['people'][0]['index'] == 1
        assert resp_data['people'][1]['address'] == '455 Dictum Court, Nadine, Mississippi, 6499'
        assert resp_data['people'][1]['age'] == 54
        assert resp_data['people'][1]['name'] == "Bonnie Bass"
        assert resp_data['people'][1]['index'] == 2
        assert resp_data['common_brown_eyed_alive_friends'][0]['index'] == 1
