#!/usr/bin/env sh
set -o verbose

# pip install flake8

# flake8 src/ --show-source --exclude=migrations,manage.py --max-line-length=120
flake8 src --config=src/tox.ini
