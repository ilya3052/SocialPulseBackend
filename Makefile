run:
	python sandbox/manage.py runserver
migrate:
	python sandbox/manage.py makemigrations
	python sandbox/manage.py migrate
