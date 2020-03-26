#!/bin/bash -e

# Script file to start mongoDB services on Travis for CI/CD

sudo sed -i 's\enabled: true\enabled: false\' /etc/mongod.conf
sudo service mongod restart

pip install -r requirements.txt
