#!/usr/bin/env sh

echo "app lable, 可选值: trade all"
app_lable=$1
if [[ "$#" != "1" ]]; then
   exit
fi
if [[ "$app_lable" == "all" ]]; then
    docker-compose exec api  python src/manage.py makemigrations trade
else
    docker-compose exec api  python src/manage.py makemigrations $1
fi
