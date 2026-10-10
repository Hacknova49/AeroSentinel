.PHONY: install install-ml test lint demo api
install:
	pip install -e packages/schemas -e "python[dev]"
install-ml:
	pip install -e "python[ml,dev]"
test:
	python -m pytest packages/schemas/tests python/tests integration/tests -q
lint:
	ruff check packages python integration scripts
demo:
	python scripts/run_demo.py
api:
	uvicorn aerosentinel.api.app:app --reload --port 8000
