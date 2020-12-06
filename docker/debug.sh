#!/usr/bin/env sh

export ENVIRONMENT=unittest; export DEBUG=True; ENTRYPOINT=sh docker-compose up -d api
