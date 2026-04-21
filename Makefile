run:
	python src/manage.py runserver 127.0.0.1:8000
migrate:
	python src/manage.py makemigrations
	python src/manage.py migrate
