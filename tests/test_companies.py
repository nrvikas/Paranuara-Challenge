from pathlib import Path
from bson import ObjectId
from manage import purge_and_import_collection, valid_collections
from app.db_layer.operations import get_item_from_collection_by_field
import json

root = (Path(__file__).parent / 'test_files').resolve()


def test_get_wrong_company_index(client, app, capsys):
    with app.app_context():
        purge_and_import_collection('companies', '{}/companies.json'.format(root))
        captured = capsys.readouterr()
        assert 'Success' in captured.out
        company = get_item_from_collection_by_field('companies', 'index', 92)
        assert company['index'] == 92
        assert company['company'] == "SUNCLIPSE"

        resp = client.get('/api/v1/companies/1', headers={'Accept': 'application/json'})
        assert 404 == resp.status_code


def test_get_company_employees(client, app, capsys):
    with app.app_context():
        purge_and_import_collection('companies', '{}/companies.json'.format(root))
        captured = capsys.readouterr()
        assert 'Success' in captured.out
        company = get_item_from_collection_by_field('companies', 'index', 92)
        assert company['index'] == 92
        assert company['company'] == "SUNCLIPSE"

        purge_and_import_collection('fruits', '{}/fruits.json'.format(root))
        purge_and_import_collection('vegetables', '{}/vegetables.json'.format(root))
        purge_and_import_collection('people', '{}/people.json'.format(root))
        captured = capsys.readouterr()
        assert 'Success' in captured.out
        person = get_item_from_collection_by_field('people', 'index', 943)

        resp = client.get('/api/v1/companies/92/employees', headers={'Accept': 'application/json'})
        assert 200 == resp.status_code
        employee = json.loads(resp.data.decode('utf-8'))
        assert employee[0].get('index') == 943


def test_get_company_no_employees(client, app, capsys):
    with app.app_context():
        purge_and_import_collection('companies', '{}/companies.json'.format(root))
        captured = capsys.readouterr()
        assert 'Success' in captured.out
        company = get_item_from_collection_by_field('companies', 'index', 92)
        assert company['index'] == 92
        assert company['company'] == "SUNCLIPSE"

        resp = client.get('/api/v1/companies/92/employees', headers={'Accept': 'application/json'})
        assert 404 == resp.status_code
        resp_data = json.loads(resp.data.decode('utf-8'))
        assert resp_data['error']['error_msg'] == 'Company 92 has no employees'
