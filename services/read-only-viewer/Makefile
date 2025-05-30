ENVIRONMENT ?= mgmt
SERVICE ?= read-only-viewer
BUILD_DIR := ../../build/services/${SERVICE}
ARTEFACT_BUCKET := ${REPO_NAME}-mgmt-artefacts-bucket
TEMP_DIRECTORY ?= ./temp
DEPLOYMENT_WORKSPACE := $(if $(WORKSPACE),$(if $(filter default,$(WORKSPACE)),,-$(WORKSPACE)),)
DEPLOYMENT_BUCKET ?= ftrs-dos-${ENVIRONMENT}-${SERVICE}-frontend-bucket${DEPLOYMENT_WORKSPACE}
READ_ONLY_VIEWER_DOMAIN_NAME = ${DEPLOYMENT_BUCKET}.s3.${AWS_REGION}.amazonaws.com
CLOUDFRONT_DISTRIBUTION_ID := $(shell aws cloudfront list-distributions --query "DistributionList.Items[?contains(Origins.Items[*].DomainName, '$(READ_ONLY_VIEWER_DOMAIN_NAME)')].Id" --output text)

ensure-build-dir:
	mkdir -p $(BUILD_DIR)

clean:
	rm -rf .eslintcache .jest .tmp .coverage coverage.xml .vinxi .output
	rm -rf $(BUILD_DIR)

install: install-dependencies

install-dependencies:
	asdf install
	npm install

pre-commit: format lint

format:
	npm run format -- --fix
	npm run lint -- --fix

lint:
	npm run check

unit-test:
	npm run test -- --passWithNoTests

build: clean ensure-build-dir
	npm run build
	cd .output/public && zip -r -q ../../$(BUILD_DIR)/$(SERVICE)-assets-$(APPLICATION_TAG).zip *
	cd .output/server && zip -r -q ../../$(BUILD_DIR)/$(SERVICE)-server-$(APPLICATION_TAG).zip *

publish:
	aws s3 sync $(BUILD_DIR)/ s3://$(ARTEFACT_BUCKET)/$(WORKSPACE)/$(COMMIT_HASH)/ --region $(AWS_REGION)

deploy:
	aws s3 cp s3://$(ARTEFACT_BUCKET)/$(WORKSPACE)/$(COMMIT_HASH)/$(SERVICE)-assets-$(APPLICATION_TAG).zip .
	unzip $(SERVICE)-assets-$(APPLICATION_TAG).zip -d ${TEMP_DIRECTORY}
	aws s3 sync --delete $(TEMP_DIRECTORY)/  s3://$(DEPLOYMENT_BUCKET)/

invalidate-cloudfront-cache:
	@echo "CLOUDFRONT_DISTRIBUTION_ID: $(CLOUDFRONT_DISTRIBUTION_ID)"
	aws cloudfront create-invalidation --distribution-id $(shell aws cloudfront list-distributions --query "DistributionList.Items[?contains(Origins.Items[*].DomainName, '$(READ_ONLY_VIEWER_DOMAIN_NAME)')].Id" --output text) --paths "/*"
