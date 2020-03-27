# paranuara-challenge
[![Build Status](https://travis-ci.com/nrvikas/Paranuara-Challenge.svg?branch=master)](https://travis-ci.com/nrvikas/Paranuara-Challenge.svg?branch=master)

## Overview
This is a Flask based **HATEOAS driven RESTful** **API** to get and search data related to company and employees according to  Paranuara Challenge -   build a REST API to provide the desired information about people living in the Paranuara planet.
Simply use a API tool like Postman.
It uses MongoDB for data storage.  `pytest` framework is used to write test cases to enhance data import and  API behavior and stability.
Travis CI is used to facilitate CI/CD for the ongoing development of the API.


## Table of contents
* [API](#api)
* [Installation](#installation)
* [Config](#config)
    * [System Config](#system-config)
    * [Tests Config](#test-config)
* [Data Import](#data-import)
* [Schema](#schema)
* [Database](#database)
* [Code base](#code-base)
* [CI-CD and Testing](#ci-cd-and-testing)

## API

  The API supports **HATEOAS**
  The endpoints currently supported are:

| Endpoint | Description    |
|--|--|
|/api/v1/companies/{index}  | API to return a company with requested index  |
| /api/v1/companies/{index}/employees| API to return all the employees of a company |
|/api/v1/people/{index}  | API to return the person with the requested index |
|/api/v1/people/{index}/liked_food  | API to return the favourite fruit and vegetable of a person |
|/api/v1/people/special_friends?person_1={index_1}&person_2={index_2|Given 2 people, the API provides their information (Name, Age, Address, phone) and the list of their friends in common which have brown eyes and are still alive.|
|  |  |


## Installation
Given an environment with Python and MongoDB (>= 3.6) installed, setting this application up is very easy and straight forward.

In the folder of the project:
```
pip install -r requirements.txt
```

## Config
Below sections include the config options that can be defined in settings.py.

### System Config
* DB_NAME
    * Database name for the API. Defaults to `paranuara`

### Test Config
* DB_NAME
    * Test Database name for the API. Defaults to `paranuara_test`

## Data Import

Data Import is supported my ```manage``` commands.
We have 4 collections in this API instance.

- companies
- people
- fruits
- vegetables

In order to have this application evolve, ```fruits``` and ```vegetables``` were made collections and not just in-memory lists or data files. This way, just like ```people``` and ```companies``` even ```fruits``` and `vegetables`` can be added to the system by data imports and minimal or no code changes.

The data imports of ```people```  collections automatically creates ```['fruits']``` and ```['vegetables']``` lists in the ```people``` document deriving it from ```favouriteFood```. This way we don't need to do DB look-ups while fetching data for API responses.
Because of this, the order of importing data is important. ```fruits``` and ```vegetables``` must be imported before we import ```people```

Following validations are covered during data import and there are test cases to verify these:

 - Valid and allowed collection name only
 - File extension to be only .json
 - Must be a valid file path
 - Various schema validations (mentioned in *schema* section below
 - Collection dependency validation -to ensure ```fruits```, ```vegetables``` and ```companies``` are imported before importing ```people```

Format of the command to import data is 'collection_name' followed by 'absolute_file_path'

-	Import ```fruits``` and ```vegetables```
		-	```python manage.py fruits <absolute_path_to_the_folder>/fruits.json```
		-	```python manage.py vegetables <absolute_path_to_the_folder>/vegetables.json```
-	Import ```people```
		-	```python manage.py people <absolute_path_to_the_folder>/people.json```
-	Import ```companies```
		-	```python manage.py companies <absolute_path_to_the_folder>/companies.json```

**Bulk import of data at once to all collections are also supported. Simple place all your .json files in one location and use the following command:**
```python manage.py initialze_data_from_directory <abolute_directory_path_to_all_four_json>```

## Schema
  As there is an ```index``` field in the given JSON files, we are using that as the ID of the documents exposed to public. The ```_id``` field created by MongoDB is not projected outside.
  During the data import, schema validations that take place are:
  - Checking for 'type' validation to make sure number, boolean and list fields are as as per schema specification
  - ```index``` field is a required field
  - ```index``` field is verified for uniqueness during validation
  - Fields that are not a part of the resource schema are discarded.
  - During the import of 'people' resource, ```favouriteFood``` is split into ```fruits``` and ```vegetables```array in the ```people``` document.

## Database
To enable efficient access of the ```people``` and ```companies``` documents, following MongoDB indexes are created.
```people``` collection:
  - ```index```
  - ```company_id```
   - ```eyeColor```
   - ```has_died```

```companies``` collection:
  - ```index``` field

## Code Base
The architecture of the code base enables the API to evolve.
Modular approach taken enables us to develop other fully operational API endpoints for other collections with minimal effort.   Simply create a Flask *blueprint* for the next API you want to develop and implement the specific API business logic.   For this reason, there has been a specific effort to abstract Database operations into a `db_layer` module so the API business logic can be agnostic about the inner DB implementations.
* `app` : ```___init``` initializes the Flask App, initializes DB, registers blueprints,   add config variables and initializes core app modules
* `db_layer`: contains interfaces exposed for other Blueprints and future APIs to use to carry out any database operations.
* `static`: Static Image files/assets used in HTML templates. Ex. Main page of the API
* `templates`: HTML templates used by the application
* `tests`: ```pytest``` test cases for validation of data import, schema and API behavior.

To ensure proper standards and best practices for coding the API, we use `flake8` as the styling guide.

## CI-CD and Testing

Travis CI is integrated with this repository to run `pytest` test cases and uses `flake8` to ensure proper code style and standards across Python files being pushed into the repository.
Tests written cover:
 * Data import validation.
 * Schema and data dependency Validation
 * API verification of all endpoints

