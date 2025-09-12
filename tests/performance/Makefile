PROJECT_NAME := ftrs-dos
ENVIRONMENT ?= dev
SERVICE ?= is-performance
PYTHON_VERSION ?= 3.12
TEST_DIR := parameter_files
WORKSPACE_PARAMETER_FILES_BUCKET := ${PROJECT_NAME}-${ENVIRONMENT}-${SERVICE}-parameter-files-bucket-${WORKSPACE}
MAIN_PARAMETER_FILES_BUCKET := ${PROJECT_NAME}-${ENVIRONMENT}-${SERVICE}-parameter-files-bucket

install: config
	make install-jmeter-plugins

config:
	make _install-dependencies

install-jmeter-plugins: ## Installs jmeter plugin manager, tools and required plugins
	echo "Installing jmeter plugin manager"
	curl --output-dir  ~/.asdf/installs/jmeter/5.6.3/lib/ext -O https://repo1.maven.org/maven2/kg/apc/jmeter-plugins-manager/1.11/jmeter-plugins-manager-1.11.jar

	echo "Installing jmeter command runner"
	curl --output-dir  ~/.asdf/installs/jmeter/5.6.3/lib -O https://repo1.maven.org/maven2/kg/apc/cmdrunner/2.0/cmdrunner-2.0.jar

	echo "Installing jmeter plugin installer"
	-java -cp lib/ext/jmeter-plugins-manager-1.11.jar org.jmeterplugins.repository.PluginManagerCMDInstaller

	echo "Installing jmeter plugins"
	/bin/bash ~/.asdf/installs/jmeter/5.6.3/bin/PluginsManagerCMD.sh install jpgc-graphs-basic,jpgc-graphs-additional


performance-test: ##[PLAN_NAME=name of jmeter plan] [PFX_PATH=path to pfk file][PFX_PASSWORD=password for pfx file] [ENDPOINT=endpoint of APIs] [TEST_DATA=name of performance test data jtl file]
	echo "running performance tests against ${PLAN_NAME}..."
	jmeter -n -t ${PLAN_NAME}.jmx -J serviceendpoint=${ENDPOINT} -f -l ${TEST_DATA}.jtl -e -o "report" -D javax.net.ssl.keyStore="${PFX_PATH}" -D javax.net.ssl.keyStorePassword="${PFX_PASSWORD}"

performance-test-dashboard: ##[TEST_DATA=name of performance test data jtl file]
	echo "generating performance dashboard for ${TEST_DATA}..."
	jmeter -g ${TEST_DATA}.jtl -f -e -o reports

download-workspace-performance-parameter-files: ##[AWS_REGION=aws region] [WORKSPACE=workspace name]
	echo "PROJECT_NAME: ${PROJECT_NAME}"
	echo "ENVIRONMENT: ${ENVIRONMENT}"
	echo "SERVICE: ${SERVICE}"
	echo "WORKSPACE_PARAMETER_FILES_BUCKET: ${WORKSPACE_PARAMETER_FILES_BUCKET}"
	aws s3 cp s3://${WORKSPACE_PARAMETER_FILES_BUCKET} --region $(AWS_REGION) ${TEST_DIR}/ --recursive

download-main-performance-parameter-files: ##[AWS_REGION=aws region]
	echo "PROJECT_NAME: ${PROJECT_NAME}"
	echo "ENVIRONMENT: ${ENVIRONMENT}"
	echo "SERVICE: ${SERVICE}"
	echo "MAIN_PARAMETER_FILES_BUCKET: ${MAIN_PARAMETER_FILES_BUCKET}"
	aws s3 cp s3://${MAIN_PARAMETER_FILES_BUCKET} --region $(AWS_REGION) ${TEST_DIR}/ --recursive

copy-performance-parameter-files: ##[AWS_REGION=aws region] [WORKSPACE=workspace name]
	echo "PROJECT_NAME: ${PROJECT_NAME}"
	echo "ENVIRONMENT: ${ENVIRONMENT}"
	echo "SERVICE: ${SERVICE}"
	echo "WORKSPACE_PARAMETER_FILES_BUCKET: ${WORKSPACE_PARAMETER_FILES_BUCKET}"
	echo "MAIN_PARAMETER_FILES_BUCKET: ${MAIN_PARAMETER_FILES_BUCKET}"
	aws s3 cp s3://${MAIN_PARAMETER_FILES_BUCKET} --region $(AWS_REGION) s3://${WORKSPACE_PARAMETER_FILES_BUCKET} --region $(AWS_REGION) --recursive

_install-dependency: # Install asdf dependency - mandatory: name=[listed in the '.tool-versions' file]; optional: version=[if not listed]
	echo ${name}
	asdf plugin add ${name} ||:
	asdf plugin update ${name} ||:
	asdf install ${name} $(or ${version},)

_install-dependencies: # Install all the dependencies listed in .tool-versions
	for plugin in $$(grep ^[a-z] .tool-versions | sed 's/[[:space:]].*//'); do \
		make _install-dependency name="$${plugin}"; \
	done
