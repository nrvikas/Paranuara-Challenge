#!/bin/bash -e

# Script file to run flake8(style check) and behave tests on Travis for CI/CD
flake8
pytest
