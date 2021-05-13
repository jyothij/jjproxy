.PHONY: run build clean lint help

.DEFAULT_GOAL := help

help:
	@echo "----------MyProxy Python App HELP------------"
	@echo "To build dependencies type make build"
	@echo "To run app type make run HTTP_PORT=<port>"
	@echo "---------------------------------------------"

lint:
	@flake8 .

clean:
	@find . -type f -name '*.pyc' -delete

build:
	@pip install -r requirements.txt

run:
	export HTTP_PORT=$(HTTP_PORT)
	@python app.py 