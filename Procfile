release: python manage.py migrate && python manage.py poblar_db
web: gunicorn config.wsgi --log-file -
