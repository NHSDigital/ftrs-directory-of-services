SERVICE ?= gp-search
PYTHON_VERSION ?= 3.12
BUILD_DIR := ../../build/services/${SERVICE}
LOCAL_DIR := ../../services/${SERVICE}
FUNC_DIR := functions/$(FUNCTION_NAME)
S3_BUCKET := ${REPO_NAME}-$(ENVIRONMENT)-artefacts-bucket
LAMBDA_NAME := ftrs-dos-${SERVICE}-lambda
FUNCTION_NAME := gp_search_function.py

# ==============================================================================

ensure-build-dir:
	mkdir -p $(BUILD_DIR)

dependencies: # Install dependencies needed to build and test the project @Pipeline
	# TODO: Implement installation of your project dependencies

build: ensure-build-dir
	echo "$(COMMIT_HASH)" > $(BUILD_DIR)/metadata.txt
	cp $(LOCAL_DIR)/$(FUNC_DIR) $(BUILD_DIR)/
	cd $(BUILD_DIR) && zip -r -q $(LAMBDA_NAME)-$(APPLICATION_TAG).zip $(FUNCTION_NAME)

publish: # Publish the project artefact @Pipeline
	aws s3 cp $(BUILD_DIR)/$(LAMBDA_NAME)-$(APPLICATION_TAG).zip s3://$(S3_BUCKET)/$(WORKSPACE)/$(COMMIT_HASH)/$(LAMBDA_NAME)-$(APPLICATION_TAG).zip --region $(AWS_REGION)

deploy: # Deploy the project artefact to the target environment @Pipeline
	# TODO: Implement the artefact deployment step

clean:: # Clean-up project resources (main) @Operations
	# TODO: Implement project resources clean-up step

config:: # Configure development environment (main) @Configuration
	# TODO: Use only 'make' targets that are specific to this project, e.g. you may not need to install Node.js
	make _install-dependencies

# ==============================================================================

${VERBOSE}.SILENT: \
	build \
	clean \
	config \
	dependencies \
	deploy \
