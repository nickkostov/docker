.PHONY: validate discover inspectur-install inspectur builder-install

discover:
	@scripts/discover-images.sh

validate:
	@scripts/validate-metadata.sh
	@scripts/validate-dockerfiles.sh
	@echo "Repository validation passed."

inspectur-install:
	python3 -m venv .venv
	.venv/bin/python -m pip install --editable .

builder-install:
	python3 -m venv .venv
	.venv/bin/python -m pip install --editable .

inspectur:
	@.venv/bin/inspectur
