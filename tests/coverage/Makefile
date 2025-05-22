install: install-dependencies


install-dependencies:
	asdf install
	poetry install --no-interaction

combine-coverage:
	cd ../
	pwd
	ls -lat
	poetry run coverage combine .*-coverage
