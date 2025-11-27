release: python manage.py migrate && python manage.py migrate eventos 0004 --fake
web: gunicorn config.wsgi --log-file -
