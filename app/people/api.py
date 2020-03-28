from app.decorator import int_index
from flask import jsonify, request
from app.db_layer.operations import get_items_from_collection_by_aggregation, get_item_from_collection_by_field, \
    get_items_from_collection_by_query
from app.settings import URL_PREFIX
from app.people import people_bp
from app.utils import get_error, get_server_error, get_index_value_error


def get_person_not_found_error(id):
    return get_error("Person {} not found".format(id), "Not found", 404, "Not Found",
                     "There was no person with that index {}".format(id))


@people_bp.route('{}/people/<id>'.format(URL_PREFIX), methods=['GET'])
@int_index
def get_person(id):
    """
    This endpoint returns the entire people collection
    """
    try:
        person = get_item_from_collection_by_field('people', 'index', id, enhance_hateoas)
        if not person:
            return jsonify(get_person_not_found_error(id)), 404

        return jsonify(person), 200
    except Exception:
        return jsonify(get_server_error()), 500


@people_bp.route('{}/people/<id>/liked_food'.format(URL_PREFIX), methods=['GET'])
@int_index
def get_person_fav_food(id):
    """
    This endpoint returns the favorite fruits and vegetables of a person
    """
    try:
        pipeline = [{"$match": {"index": id}},
                    {"$project": {
                        "_id": 0,
                        "age": 1,
                        "username": "$name",
                        "fruits": 1,
                        "vegetables": 1
                    }}]
        people = list(get_items_from_collection_by_aggregation('people', pipeline))

        if not people:
            return jsonify(get_person_not_found_error(id)), 404

        person = people[0]
        enhance_hateoas(person, id)
        return jsonify(person), 200
    except Exception as e:
        return jsonify(get_server_error()), 500


@people_bp.route('{}/people/special_friends'.format(URL_PREFIX), methods=['GET'])
def get_special_friends():
    """
    Given 2 people, this method provides their information (Name, Age, Address, phone)
    and the list of their friends in common which have brown eyes and are still alive.
    """
    if not request.args.get('person_1') or not request.args.get('person_2'):
        return jsonify(get_error("Request params missing", "Bad Request", 400, "Missing parameters",
                                 "Values for person_1 and person_2 are missing in request params")), 400

    try:
        person_one_index = int(request.args.get('person_1'))
        person_two_index = int(request.args.get('person_2'))
    except ValueError:
        return jsonify(get_index_value_error()), 400

    try:
        results = list(get_items_from_collection_by_aggregation('people',
                                                                get_aggregation_pipeline_query_special_friends(
                                                                    person_one_index, person_two_index)))

        # Frame response and send - separate function
        response = frame_response_special_friends_search(results)
        return jsonify(response), 200
    except Exception as e:
        return jsonify(get_server_error()), 500


def get_employees_of_company(company_index):
    query = {'company_id': int(company_index)}
    employees = list(get_items_from_collection_by_query('people', query))
    enhance_hateoas(employees)
    return employees


def enhance_hateoas(items, index=''):
    if not items:
        return

    docs = [items] if not isinstance(items, list) else items
    for doc in docs:
        doc_id = str(doc.get('index', index))
        doc.setdefault('_links', {})
        doc['_links']['self'] = {
            'href': '{}/people/{}'.format(URL_PREFIX, doc_id)
        }
        doc['_links']['liked_food'] = {
            'href': '{}/people/{}/liked_food'.format(URL_PREFIX, doc_id)
        }


def frame_response_special_friends_search(results):
    response = {}
    if results:
        response['people'] = results[0]['people'][0]["people"]
        response["common_brown_eyed_alive_friends"] = results[0]["special_friends"]
        enhance_hateoas(response['people'])
        enhance_hateoas(response["common_brown_eyed_alive_friends"])
    return response


def get_aggregation_pipeline_query_special_friends(person_1, person_2):
    pipeline = [
        {"$match": {"index": {"$in": [person_1, person_2]}}},
        {"$project": {"_id": 0, "age": 1, "name": 1, "address": 1, "phone": 1, "friends": 1, "index": 1}},
        {"$group": {
            "people": {"$push": "$$ROOT"}, "_id": 0,
            "friends1": {"$first": "$friends.index"}, "friends2": {"$last": "$friends.index"}
        }},
        {"$project": {"commonFriends": {"$setIntersection": ["$friends1", "$friends2"]}, "_id": 0, "people": 1}},
        {"$lookup": {
            "from": "people",
            "localField": "commonFriends",
            "foreignField": "index",
            "as": "commonFriendsObjects"
        }},
        {"$unwind": {"path": "$commonFriendsObjects", "preserveNullAndEmptyArrays": True}},
        {"$match": {"commonFriendsObjects.eyeColor": "brown", "commonFriendsObjects.has_died": False}},
        {"$project": {"commonFriendsObjects._id": 0}},
        {"$group": {
            "_id": "$_id",
            "people": {"$push": "$$ROOT"},
            "special_friends": {"$push": "$commonFriendsObjects"}
        }},
        {"$project": {
            "people.people": 1,
            "special_friends": 1
        }}
    ]

    return pipeline
