web: python manage.py migrate && python manage.py collectstatic --noinput && gunicorn mensa_member_connect_backend.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120
