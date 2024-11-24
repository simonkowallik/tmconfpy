.PHONY: clean clean-test clean-pyc clean-build docs help

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . \( -path ./env -o -path ./venv -o -path ./.env -o -path ./.venv \) -prune -o -name '*.egg-info' -exec rm -fr {} +
	find . \( -path ./env -o -path ./venv -o -path ./.env -o -path ./.venv \) -prune -o -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -f .coverage
	rm -f coverage.xml
	rm -f coverage.lcov
	rm -fr htmlcov/
	rm -fr .pytest_cache
	rm -fr .ruff_cache
	find . -name '.mypy_cache' -exec rm -fr {} +

code-format:
	ruff check --select I --fix --exclude .venv
	ruff format --exclude .venv

test:
	pytest --cov=tmconfpy tests/
	coverage html
	coverage lcov
	coverage xml
	coverage report -m

tests: test

ansible:
	cp -f tmconfpy/parser.py ansible_collections/simonkowallik/tmconfpy/plugins/module_utils/parser.py
	cp -f LICENSE ansible_collections/simonkowallik/tmconfpy/LICENSE
	mkdir -p ./build
	ansible-galaxy collection build ansible_collections/simonkowallik/tmconfpy --output-path build/
	echo 'ansible-galaxy collection publish build/simonkowallik-tmconfpy-*.tar.gz --api-key $ANSIBLE_GALAXY_API_KEY'

container:
	docker build -t tmconfpy .

publish-test-pypi: dist
#	poetry config repositories.test-pypi https://test.pypi.org/legacy/
#	poetry config pypi-token.test-pypi $(TOKEN)
	poetry publish -r test-pypi

publish-pypi: dist
#	poetry config repositories.pypi https://test.pypi.org/legacy/
#	poetry config pypi-token.pypi $(TOKEN)
	poetry publish -r pypi

dist: clean ## builds source and wheel package
	poetry build
	ls -l dist
	tar tzf dist/*.tar.gz