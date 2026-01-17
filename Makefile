.PHONY: install test lint format clean

install:
	pip install -e .
	pip install -e .[dev]

test:
	pytest tests/

lint:
	ruff check .
	black --check .
	mypy src/

format:
	black .
	ruff check --fix .

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	find . -name '__pycache__' -exec rm -rf {} +
	find . -name '*.pyc' -exec rm -rf {} +
	find . -name '*.pyo' -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
