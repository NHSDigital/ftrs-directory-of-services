.PHONY: help install jwt-token

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

install:
	@pip install "PyJWT[crypto]" boto3 requests

jwt-token: ## Generate JWT token - usage: make jwt-token env=<local|dev|prod>
ifndef env
	$(error env parameter is required. Usage: make jwt-token env=local)
endif
	@python generate_jwt.py $(env)

.DEFAULT_GOAL := help
