#!/bin/bash
set -o errexit
set -o pipefail
set -o nounset

python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py collectstatic --noinput

case "$MODE" in
"TEST")
    echo "TEST"
    ;;
"PROD")
    gunicorn core.asgi:application --worker-class uvicorn.workers.UvicornWorker --workers 5 --bind 0.0.0.0:8000 --timeout 200
    ;;
"DEV")
    uvicorn core.asgi:application --host 0.0.0.0 --port 8000 --reload
    ;;
*)
    echo "NO MODE SPECIFIED!"
    exit 1
    ;;
esac
