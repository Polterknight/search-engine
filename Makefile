.PHONY: install test run clean

install:
	pip install -r requirements.txt

test:
	python -m pytest tests/ -v --cov=src

test-performance:
	python -m pytest tests/test_performance.py -v

run-index:
	python src/cli.py index --dir ./data/sample_docs

run-search:
	python src/cli.py search "пример запроса"

clean:
	rm -rf __pycache__
	rm -rf src/__pycache__
	rm -rf tests/__pycache__
	rm -f *.json

format:
	black src/ tests/

lint:
	flake8 src/ tests/

type-check:
	mypy src/

check-all: lint type-check test

benchmark:
	python benchmarks/performance_test.py

docs:
	pdoc --html src --output-dir docs/api

.PHONY: format lint type-check check-all benchmark docs