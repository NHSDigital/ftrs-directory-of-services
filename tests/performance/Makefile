PROJECT := ftrs-dos
ENVIRONMENT ?= dev
SERVICE ?= is-performance
PYTHON_VERSION ?= 3.12
TEST_DIR := parameter_files
WORKSPACE_PARAMETER_FILES_BUCKET := ${PROJECT}-${ENVIRONMENT}-${SERVICE}-parameter-files-bucket-${WORKSPACE}
MAIN_PARAMETER_FILES_BUCKET := ${PROJECT}-${ENVIRONMENT}-${SERVICE}-parameter-files-bucket

install: install-dependencies

install-dependencies:
	asdf install

performance-test: ##[PLAN_NAME=name of jmeter plan] [PFX_PATH=path to pfk file][PFX_PASSWORD=password for pfx file] [ENDPOINT=endpoint of APIs]
	echo "running performance tests against ${PLAN_NAME}..."
	export PLAN_NAME=${PLAN_NAME} ; \
	export ENDPOINT=${ENDPOINT} ; \
	export PFX_PATH=${PFX_PATH} ; \
	export PFX_PASSWORD=${PFX_PASSWORD} ; \
	jmeter -n -t ${PLAN_NAME}.jmx -J serviceendpoint=${ENDPOINT} -f -l result.csv -e -o "report" -D javax.net.ssl.keyStore="${PFX_PATH}" -D javax.net.ssl.keyStorePassword="${PFX_PASSWORD}";


performance-test-dashboard: ##[TEST_DATA=name of performance test data jtl file]
	echo "generating performance dashboard for ${TEST_DATA}..."
	export TEST_DATA=${TEST_DATA} ; \
	jmeter -g ${TEST_DATA}.jtl -f -e -o reports ;

download-workspace-performance-parameter-files: ##[AWS_REGION=aws region] [WORKSPACE=workspace name]
	echo "PROJECT: ${PROJECT}"
	echo "ENVIRONMENT: ${ENVIRONMENT}"
	echo "SERVICE: ${SERVICE}"
	echo "WORKSPACE_PARAMETER_FILES_BUCKET: ${WORKSPACE_PARAMETER_FILES_BUCKET}"
	aws s3 cp s3://${WORKSPACE_PARAMETER_FILES_BUCKET} --region $(AWS_REGION) ${TEST_DIR}/ --recursive

download-main-performance-parameter-files: ##[AWS_REGION=aws region]
	echo "PROJECT: ${PROJECT}"
	echo "ENVIRONMENT: ${ENVIRONMENT}"
	echo "SERVICE: ${SERVICE}"
	echo "MAIN_PARAMETER_FILES_BUCKET: ${MAIN_PARAMETER_FILES_BUCKET}"
	aws s3 cp s3://${MAIN_PARAMETER_FILES_BUCKET} --region $(AWS_REGION) ${TEST_DIR}/ --recursive

copy-performance-parameter-files: ##[AWS_REGION=aws region] [WORKSPACE=workspace name]
	echo "PROJECT: ${PROJECT}"
	echo "ENVIRONMENT: ${ENVIRONMENT}"
	echo "SERVICE: ${SERVICE}"
	echo "WORKSPACE_PARAMETER_FILES_BUCKET: ${WORKSPACE_PARAMETER_FILES_BUCKET}"
	echo "MAIN_PARAMETER_FILES_BUCKET: ${MAIN_PARAMETER_FILES_BUCKET}"
	aws s3 cp s3://${MAIN_PARAMETER_FILES_BUCKET} --region $(AWS_REGION) s3://${WORKSPACE_PARAMETER_FILES_BUCKET} --region $(AWS_REGION) --recursive
