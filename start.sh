docker compose up --build -d
docker compose exec backend sh -c "python manage.py migrate"
docker compose exec backend sh -c "python manage.py createsuperuser"
docker compose exec backend sh -c "python manage.py collectstatic"
docker compose exec backend sh -c "cp -r /app/collected_static/* /backend_static/static/"
