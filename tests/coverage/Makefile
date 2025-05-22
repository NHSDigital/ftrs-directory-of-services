install: install-dependencies

install-dependencies:
	asdf install
	poetry install --no-interaction

combine-coverage:
	poetry run coverage combine .*-coverage
