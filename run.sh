#!/bin/bash

set -ex

while ! pg_isready --host postgres --dbname "${POSTGRES_DB}"
do
    sleep 1
done

cd src

python3 ./manage.py check --deploy --fail-level ERROR
python3 ./manage.py makemigrations --check
python3 ./manage.py migrate

exec uwsgi \
    --module=myproject.wsgi:application \
    --http :8000 \
    --processes=2 \
    --uid=1000 --gid=1000
