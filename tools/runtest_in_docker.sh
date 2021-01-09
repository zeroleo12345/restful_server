#!/usr/bin/env sh
set -o verbose

docker-compose exec api ./.test/runtest

# docker-compose exec api pytest  trade/user/tests.py
# docker-compose exec api pytest  -k  test_payjs_post
