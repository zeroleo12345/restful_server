#!/usr/bin/env sh
set -o verbose

docker-compose exec web ../runtox

# docker-compose exec web pytest trade/user/tests.py -k  test_user

