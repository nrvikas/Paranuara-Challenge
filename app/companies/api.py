from flask import jsonify
from app.db_layer.operations import get_item_from_collection_by_field
from app.companies import companies_bp
from app.decorator import int_index
from app.settings import URL_PREFIX
from app.people.api import get_employees_of_company
from app.utils import get_error, get_server_error


@companies_bp.route('{}/companies/<id>'.format(URL_PREFIX), methods=['GET'])
@int_index
def get_company_employees(id):
    """
    This endpoint gets a company by index
    """

    try:
        company = get_item_from_collection_by_field('companies', 'index', id, enhance_hateoas)
        if not company:
            return jsonify(get_company_not_found_error(id)), 404

        return jsonify(company), 200
    except Exception:
        return jsonify(get_server_error()), 404


@companies_bp.route('{}/companies/<id>/employees'.format(URL_PREFIX), methods=['GET'])
@int_index
def get_company(id):
    """
    This methods gets all the employees of a company
    """
    try:
        company = get_item_from_collection_by_field('companies', 'index', id)
        if not company:
            return jsonify(get_company_not_found_error(id)), 404

        employees = get_employees_of_company(company['index'])
        if not employees:
            return jsonify(get_error('No employees found', 'Not Found', 404, 'No employees found',
                                     'Company {} has no employees'.format(id))), 404

        return jsonify(employees), 200
    except Exception as e:
        return jsonify(get_server_error()), 404


def get_company_not_found_error(id):
    return get_error("Company {} not found".format(id), "Not found", 404, "Not Found",
                     "There was no company with that index {}".format(id))


def enhance_hateoas(items, index=''):
    if not items:
        return

    docs = [items] if not isinstance(items, list) else items
    for doc in docs:
        doc_id = str(doc.get('index', index))
        doc.setdefault('_links', {})
        doc['_links']['self'] = {
            'href': '{}/companies/{}'.format(URL_PREFIX, doc_id)
        }
        doc['_links']['employees'] = {
            'href': '{}/companies/{}/employees'.format(URL_PREFIX, doc_id)
        }
