ENVIRONMENT ?= mgmt
SERVICE ?= read-only-viewer
BUILD_DIR := ../../build/services/${SERVICE}
ARTEFACT_BUCKET := ${REPO_NAME}-${ENVIRONMENT}-artefacts-bucket
TEMP_DIRECTORY ?= ./temp
DEPLOYMENT_BUCKET ?= ftrs-dos-${ENVIRONMENT}-${SERVICE}-${SERVICE}-bucket-${WORKSPACE}
READ_ONLY_VIEWER_DOMIAN_NAME = ${DEPLOYMENT_BUCKET}.s3.${AWS_REGION}.amazonaws.com
CLOUDFRONT_DISTRIBUTION_ID =

ensure-build-dir:
	mkdir -p $(BUILD_DIR)

clean:
	rm -rf .eslintcache .jest .tmp .coverage coverage.xml
	rm -rf $(BUILD_DIR)

install: install-dependencies

install-dependencies:
	asdf install
	npm install

format:
	npm run format -- --fix
	npm run lint -- --fix

lint:
	npm run check

unit-test:
	npm run test -- --passWithNoTests

build: ensure-build-dir
	npm run build -- --outDir $(BUILD_DIR) --emptyOutDir
	cd $(BUILD_DIR) && zip -r -q ../$(SERVICE)-$(APPLICATION_TAG).zip *
	rm -rf $(BUILD_DIR)/*
	mv $(BUILD_DIR)/../$(SERVICE)-$(APPLICATION_TAG).zip $(BUILD_DIR)/

publish:
	aws s3 cp $(BUILD_DIR)/$(SERVICE)-$(APPLICATION_TAG).zip s3://$(ARTEFACT_BUCKET)/$(WORKSPACE)/$(COMMIT_HASH)/$(SERVICE)-$(APPLICATION_TAG).zip --region $(AWS_REGION)

deploy:
	aws s3 cp s3://$(ARTEFACT_BUCKET)/$(WORKSPACE)/$(COMMIT_HASH)/$(SERVICE)-$(APPLICATION_TAG).zip .
	unzip $(SERVICE)-$(APPLICATION_TAG).zip -d ${TEMP_DIRECTORY}
	aws s3 cp $(TEMP_DIRECTORY)/  s3://$(DEPLOYMENT_BUCKET)/ --recursive

invlidate-cloudfront-cache:
	CLOUDFRONT_DISTRIBUTION_ID=$(aws cloudfront list-distributions --query "DistributionList.Items[?Origins.Items[0].DomainName=='$READ_ONLY_VIEWER_DOMIAN_NAME'].Id" --output text)
	aws cloudfront create-invalidation --distribution-id $(CLOUDFRONT_DISTRIBUTION_ID) --paths "/*"
