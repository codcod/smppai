.PHONY = venv lint test run

export PYTHONPATH=src/.

venv:
	rm -rf ".venv"
	rye sync
	@printf "\nDone. You can now activate the virtual environment:"
	@printf "\n  source .venv/bin/activate\n  virtualenv --upgrade-embed-wheels\n"

lint:
	rye run lint

test:
	rye run pytest

run:
	rye run demo1 --count 100
