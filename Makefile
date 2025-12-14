.PHONY: run test

venv:
	python3 -m venv .venv

install:
	pip install -e .[dev]

run:
	python3 main.py

test:
	pytest

# run:
# make venv
# source .venv/bin/activate
# make install
# make run
