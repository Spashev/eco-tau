#!/bin/bash
set -o errexit
set -o pipefail
set -o nounset

python3 manage.py makemigrations
python3 manage.py migrate

python3 manage.py collectstatic --noinput

uvicorn core.asgi:application --host 0.0.0.0 --port 8000

