from pathlib import Path
from manage import purge_and_import_collection, initialze_data_from_directory
from app.db_layer.operations import get_item_from_collection_by_field

root = (Path(__file__).parent / 'test_files').resolve()


def test_collection_name(client, app, capsys):
    with app.app_context():
        purge_and_import_collection('wrong_collection', '/some_path')
        collections = '\'companies\', \'people\', \'fruits\', \'vegetables\''
        expected = 'ERROR: Invalid collection name. Should be one of the following: [{}]'.format(collections)
        captured = capsys.readouterr()
        assert expected in captured.out


def test_file_extension(client, app, capsys):
    with app.app_context():
        purge_and_import_collection('companies', __file__)
        expected = 'Only \'.json\' files are accepted.'
        captured = capsys.readouterr()
        assert expected in captured.out


def test_file_path_exists(client, app, capsys):
    with app.app_context():
        purge_and_import_collection('companies', '/something.json')
        expected = 'File /something.json does not exist.'
        captured = capsys.readouterr()
        assert expected in captured.out


def test_companies_schema_error_validation(client, app, capsys):
    with app.app_context():
        purge_and_import_collection('companies', '{}/wrong_companies_1.json'.format(root))
        captured = capsys.readouterr()
        assert ' Unknown Index: index field not present in the JSON description' in captured.out
        assert '" \'hello string\': \'index\' value not a number"' in captured.out
        assert ' 2: company field not present in the JSON description' in captured.out


def test_companies_data_sanitization(client, app, capsys):
    with app.app_context():
        purge_and_import_collection('companies', '{}/extra_fields_wrong_companies_2.json'.format(root))
        captured = capsys.readouterr()
        assert 'Success' in captured.out
        company = get_item_from_collection_by_field('companies', 'index', 1)
        assert 'extra_field' not in company


def test_companies_successful_data_import(client, app, capsys):
    with app.app_context():
        purge_and_import_collection('companies', '{}/companies.json'.format(root))
        captured = capsys.readouterr()
        assert 'Success' in captured.out
        company = get_item_from_collection_by_field('companies', 'index', 92)
        assert company['index'] == 92
        assert company['company'] == "SUNCLIPSE"


def test_people_schema_error_validation(client, app, capsys):
    with app.app_context():
        purge_and_import_collection('companies', '{}/companies.json'.format(root))
        purge_and_import_collection('fruits', '{}/fruits.json'.format(root))
        purge_and_import_collection('vegetables', '{}/vegetables.json'.format(root))
        purge_and_import_collection('people', '{}/wrong_people_1.json'.format(root))
        captured = capsys.readouterr()
        assert ' Unknown Index: index field not present in the JSON description' in captured.out
        assert ' \'1\': \'has_died\' value not a boolean value"' in captured.out
        assert ' \'2\': \'tags\' value not a list' in captured.out
        assert ' \'3\': \'age\' value not a number' in captured.out


def test_people_removes_extra_fields(client, app, capsys):
    with app.app_context():
        purge_and_import_collection('companies', '{}/companies.json'.format(root))
        purge_and_import_collection('fruits', '{}/fruits.json'.format(root))
        purge_and_import_collection('vegetables', '{}/vegetables.json'.format(root))
        purge_and_import_collection('people', '{}/extra_fields_wrong_people_2.json'.format(root))
        captured = capsys.readouterr()
        assert 'Success' in captured.out
        person = get_item_from_collection_by_field('people', 'index', 0)
        assert "extra_field" not in person


def test_people_populates_fruits_vegetables(client, app, capsys):
    with app.app_context():
        purge_and_import_collection('companies', '{}/companies.json'.format(root))
        purge_and_import_collection('fruits', '{}/fruits.json'.format(root))
        captured = capsys.readouterr()
        assert 'Success' in captured.out
        purge_and_import_collection('vegetables', '{}/vegetables.json'.format(root))
        captured = capsys.readouterr()
        assert 'Success' in captured.out
        purge_and_import_collection('people', '{}/people.json'.format(root))
        captured = capsys.readouterr()
        assert 'Success' in captured.out
        person = get_item_from_collection_by_field('people', 'index', 943)
        assert "orange" in person['fruits']
        assert "banana" in person['fruits']
        assert "beetroot" in person['vegetables']
        assert "celery" in person['vegetables']


def test_people_import_dependency_collection_validation(client, app, capsys):
    with app.app_context():
        purge_and_import_collection('people', '{}/people.json'.format(root))
        captured = capsys.readouterr()
        assert 'Dependency collection \'fruits\' empty' in captured.out
        assert 'Dependency collection \'vegetables\' empty' in captured.out
        assert 'Dependency collection \'companies\' empty' in captured.out


def test_people_import_company_dependency_validation(client, app, capsys):
    with app.app_context():
        purge_and_import_collection('companies', '{}/missing_company_dependency.json'.format(root))
        purge_and_import_collection('fruits', '{}/fruits.json'.format(root))
        purge_and_import_collection('vegetables', '{}/vegetables.json'.format(root))
        purge_and_import_collection('people', '{}/people.json'.format(root))
        captured = capsys.readouterr()
        assert 'ERROR: Referenced companies with these indexes are missing: [92]' in captured.out


def test_initialze_data_from_directory_will_load_all_data(client, app, capsys):
    with app.app_context():
        initialze_data_from_directory(str(root))
        captured = capsys.readouterr()
        assert 'Success' in captured.out
        assert 'Success' in captured.out
        assert 'Success' in captured.out
        assert 'Success' in captured.out


def test_initialze_data_from_directory_will_fail_if_files_missing(client, app, capsys):
    with app.app_context():
        initialze_data_from_directory(str(Path(__file__).parent))
        captured = capsys.readouterr()
        assert 'ERROR: fruits.json file missing' in captured.out
        assert 'ERROR: vegetables.json file missing' in captured.out
        assert 'ERROR: companies.json file missing' in captured.out
        assert 'ERROR: people.json file missing' in captured.out
