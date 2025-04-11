#!/bin/bash
pip install -r requirements.txt
mkdir -p /app/staticfiles
python manage.py collectstatic --noinput
python manage.py migrate 