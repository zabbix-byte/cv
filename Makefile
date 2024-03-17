.PHONY: app-start \
app-start-debug

app-start:
	@echo "starting app..."
	python /code/manage.py runserver 0.0.0.0:4000 --insecure;

app-start-debug:
	@echo "starting app in debug mode..."
	python -m debugpy --wait-for-client --listen 0.0.0.0:4949 /code/manage.py runserver 0.0.0.0:80 --insecure;