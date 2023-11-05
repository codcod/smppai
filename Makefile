.PHONY = venv fix test run

APP_DIR=smppai

export PYTHONPATH=.

venv:
	rm -rf ".venv"
	poetry install
	@printf "\nDone. You can now activate the virtual environment:"
	@printf "\n  source .venv/bin/activate\n  virtualenv --upgrade-embed-wheels\n"

fix:
	poetry run isort $(APP_DIR)
	poetry run black $(APP_DIR)
	poetry run flake8 $(APP_DIR)
	poetry run ruff $(APP_DIR)/**

test:
	poetry run pytest

run:
	poetry run python smppai/experiment/app1.py
