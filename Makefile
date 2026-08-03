.PHONY: validate discover

discover:
	@scripts/discover-images.sh

validate:
	@scripts/validate-metadata.sh
	@scripts/validate-dockerfiles.sh
	@echo "Repository validation passed."
