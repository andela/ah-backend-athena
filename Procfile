release: ./manage.py makemigrations&&./manage.py migrate --noinput
web: gunicorn authors.wsgi --log-file -