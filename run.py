"""App runner

This script takes a Flask app runs it on the host and port as provided by the setting of this application
"""
from app import create_app
from app.settings import HOST_ADDRESS, PORT

if __name__ == '__main__':
    app = create_app()
    app.run(host=HOST_ADDRESS, port=PORT)
