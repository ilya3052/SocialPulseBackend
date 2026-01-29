run:
	python sandbox/manage.py runserver 127.0.0.1:8000
migrate:
	python sandbox/manage.py makemigrations
	python sandbox/manage.py migrate
