#!/bin/bash
set -ex

python manage.py collectstatic --noinput
python manage.py migrate --noinput
exec gunicorn pycon.wsgi:application
