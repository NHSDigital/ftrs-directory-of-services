SERVICE ?= slack-notification
BUILD_DIR := ../../../build/lambda/${SERVICE}
S3_BUCKET := ${REPO_NAME}-$(ENVIRONMENT)-artefacts-bucket
LAMBDA_NAME := ftrs-dos-${SERVICE}-lambda
RELEASE_BUILD ?= false
RELEASE_DIR ?= releases

# ==============================================================================

clean:
	rm -rf $(BUILD_DIR)

build: clean
	mkdir -p $(BUILD_DIR)
	cp index.py requirements.txt $(BUILD_DIR)/
	cd $(BUILD_DIR) && pip install -r requirements.txt -t . --quiet
	cd $(BUILD_DIR) && zip -r -q ../$(LAMBDA_NAME)-$(APPLICATION_TAG).zip .

publish:
	if [ "$(RELEASE_BUILD)" = "false" ] ; then \
		aws s3 cp $(BUILD_DIR)/../$(LAMBDA_NAME)-$(APPLICATION_TAG).zip s3://$(S3_BUCKET)/$(WORKSPACE)/$(COMMIT_HASH)/$(LAMBDA_NAME)-$(APPLICATION_TAG).zip --region $(AWS_REGION);\
	else \
		aws s3 cp $(BUILD_DIR)/../$(LAMBDA_NAME)-$(APPLICATION_TAG).zip s3://$(S3_BUCKET)/$(RELEASE_DIR)/$(APPLICATION_TAG)/$(LAMBDA_NAME)-$(APPLICATION_TAG).zip --region $(AWS_REGION);\
	fi

# ==============================================================================

${VERBOSE}.SILENT: \
	build \
	clean \
