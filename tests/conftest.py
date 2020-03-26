import os
import sys
from pathlib import Path
from pytest import fixture
from flask import Config

root = (Path(__file__).parent / '..').resolve()
sys.path.insert(0, str(root))

from app import create_app


def update_config(conf):
    conf['DB_NAME'] = 'paranuara_test'
    conf['MONGO_URI'] = os.environ.get('MONGO_URI', 'mongodb://localhost/{}'.format(conf['DB_NAME']))
    return conf


def clean_databases(app):
    app.extensions['data'].cx.drop_database(app.config['DB_NAME'])


@fixture
def app():
    cfg = Config(root)
    cfg.from_object('app.settings')
    update_config(cfg)
    app = create_app(config=cfg)
    return app


@fixture
def client(app):
    return app.test_client()


@fixture(autouse=True)
def setup(app):
    with app.app_context():
        clean_databases(app)
        yield
