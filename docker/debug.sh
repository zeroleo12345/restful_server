#!/usr/bin/env sh

export ENVIRONMENT=unittest; export DEBUG=1; ENTRYPOINT=sh docker-compose up -d api
