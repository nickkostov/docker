.PHONY: builder-install

builder-install:
	python3 -m venv .venv
	.venv/bin/python -m pip install --editable .
