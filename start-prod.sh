#!/bin/sh


  mkdir -p /var/run/django
  chown django:django /var/run/django
  chown django:django /home/django
  chown django:django /static_files

su django -c sh <<_
  PATH="/venv/bin/:$PATH"
yes | django-admin migrate --no-input || \
  (echo "waiting for postgres..."; sleep 10; yes | django-admin migrate --no-input)
django-admin collectstatic --no-input --clear
gunicorn --access-logfile - \
  --error-logfile - \
  --workers 2 \
  --max-requests 50 \
  --max-requests-jitter 5 \
  --bind unix:/var/run/django/dash.sock \
  config.wsgi:application
-
