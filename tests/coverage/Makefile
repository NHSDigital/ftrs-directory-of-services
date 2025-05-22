install: install-dependencies


install-dependencies:
	asdf install
	poetry install --no-interaction

combine-coverage:
	ls -lat
	poetry run coverage combine .*-coverage
