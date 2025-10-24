PROJECT_NAME := ftrs-dos
ENVIRONMENT ?= dev
SERVICE ?= is-performance
PYTHON_VERSION ?= 3.12
TEST_DIR := parameter_files
WORKSPACE_PARAMETER_FILES_BUCKET := ${PROJECT_NAME}-${ENVIRONMENT}-${SERVICE}-parameter-files-bucket-${WORKSPACE}
MAIN_PARAMETER_FILES_BUCKET := ${PROJECT_NAME}-${ENVIRONMENT}-${SERVICE}-parameter-files-bucket
JMETER_PLUGINS_MANAGER_VERSION := 1.11
CMDRUNNER_VERSION := 2.3
AWS_REGION ?= eu-west-2

install: config

config:
	make _install-dependencies
	make install-jmeter-plugins
	make install-jmeter-dependencies

install-jmeter-plugins: ## Installs jmeter plugin manager, tools and required plugins
	echo "Installing jmeter plugin manager"
	curl --output-dir  $$(asdf where jmeter)/lib/ext -O https://repo1.maven.org/maven2/kg/apc/jmeter-plugins-manager/${JMETER_PLUGINS_MANAGER_VERSION}/jmeter-plugins-manager-${JMETER_PLUGINS_MANAGER_VERSION}.jar

	echo "Installing jmeter command runner"
	curl --output-dir  $$(asdf where jmeter)/lib -O https://repo1.maven.org/maven2/kg/apc/cmdrunner/${CMDRUNNER_VERSION}/cmdrunner-${CMDRUNNER_VERSION}.jar

	echo "Setting up jmeter command runner"
	java -cp $$(asdf where jmeter)/lib/ext/jmeter-plugins-manager-${JMETER_PLUGINS_MANAGER_VERSION}.jar org.jmeterplugins.repository.PluginManagerCMDInstaller

	echo "Installing jmeter plugins"
	/bin/bash $$(asdf where jmeter)/bin/PluginsManagerCMD.sh install jpgc-graphs-basic,jpgc-graphs-additional

install-jmeter-dependencies: ## Installs jmeter dependencies
	echo "Installing jmeter dependencies"
	curl --output-dir  $$(asdf where jmeter)/lib -O https://repo1.maven.org/maven2/com/auth0/java-jwt/4.5.0/java-jwt-4.5.0.jar

performance-test-mtls: ##[PLAN_NAME=name of jmeter plan] [PFX_PATH=path to pfk file][PFX_PASSWORD=password for pfx file] [ENDPOINT=endpoint of APIs]
	echo "running performance tests against ${PLAN_NAME}..."
	jmeter -n -t ${PLAN_NAME}.jmx -J serviceendpoint=${ENDPOINT} -f -l result.jtl -e -o "report" -D javax.net.ssl.keyStore="${PFX_PATH}" -D javax.net.ssl.keyStorePassword="${PFX_PASSWORD}";

performance-test-jwt: ##[PLAN_NAME=name of jmeter plan] [APIM_ENV=environment for APIM proxy][APIKEY=API key for APIM proxy [KID=Name of key for JWT token]
	echo "running performance tests against ${PLAN_NAME}..."
	jmeter -n -t ${PLAN_NAME}.jmx -J apim_env=${APIM_ENV} -J apikey=${APIKEY} -J kid=${KID} -f -l result.jtl -e -o "report" ;

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

jmeter-ec2-id:
	@ID="$(JMETER_INSTANCE_ID)"; \
	if [ -z "$$ID" ]; then echo "JMETER_INSTANCE_ID is required"; exit 1; fi; \
	echo "JMeter EC2 instance id: $$ID"

jmeter-private-ip:
	@ID="$(JMETER_INSTANCE_ID)"; \
	if [ -z "$$ID" ]; then echo "JMETER_INSTANCE_ID is required"; exit 1; fi; \
	IP=$$(aws ec2 describe-instances --region $(AWS_REGION) --instance-ids "$$ID" \
		--query 'Reservations[0].Instances[0].PrivateIpAddress' --output text 2>/dev/null | tr -d '[:space:]'); \
	echo "JMeter EC2 private IP: $$IP"

jmeter-start-instance: ## [JMETER_INSTANCE_ID=i-xxxxxxxxxxxxxxxxx] Start the JMeter EC2 instance and wait until running
	@ID="$(JMETER_INSTANCE_ID)"; \
	if [ -z "$$ID" ]; then echo "JMETER_INSTANCE_ID is required"; exit 1; fi; \
	aws ec2 start-instances --region $(AWS_REGION) --instance-ids "$$ID" >/dev/null; \
	aws ec2 wait instance-running --region $(AWS_REGION) --instance-ids "$$ID"; \
	echo "JMeter instance started: $$ID"

jmeter-stop-instance: ## [JMETER_INSTANCE_ID=i-xxxxxxxxxxxxxxxxx] Stop the JMeter EC2 instance and wait until stopped
	@ID="$(JMETER_INSTANCE_ID)"; \
	if [ -z "$$ID" ]; then echo "JMETER_INSTANCE_ID is required"; exit 1; fi; \
	aws ec2 stop-instances --region $(AWS_REGION) --instance-ids "$$ID" >/dev/null; \
	aws ec2 wait instance-stopped --region $(AWS_REGION) --instance-ids "$$ID"; \
	echo "JMeter instance stopped: $$ID"

jmeter-version-remote: ## [JMETER_INSTANCE_ID=i-xxxxxxxxxxxxxxxxx] Print JMeter version on the EC2 using SSM
	@ID="$(JMETER_INSTANCE_ID)"; \
	if [ -z "$$ID" ]; then echo "JMETER_INSTANCE_ID is required"; exit 1; fi; \
	aws ssm start-session --region $(AWS_REGION) --target "$$ID" --document-name AWS-StartInteractiveCommand --parameters 'command=["jmeter -v"]'

jmeter-ssm-shell: ## [JMETER_INSTANCE_ID=i-xxxxxxxxxxxxxxxxx] Open an interactive SSM shell to the JMeter EC2 instance
	@ID="$(JMETER_INSTANCE_ID)"; \
	if [ -z "$$ID" ]; then echo "JMETER_INSTANCE_ID is required"; exit 1; fi; \
	aws ssm start-session --region $(AWS_REGION) --target "$$ID"

jmeter-copy-plan-ssm-inline: ## [JMETER_INSTANCE_ID=i-xxxxxxxxxxxxxxxxx] [PLAN=jmeter_test_plan.jmx] [DEST=jmeter_test_plan.jmx]
	@ID="$(JMETER_INSTANCE_ID)"; \
	if [ -z "$$ID" ]; then echo "JMETER_INSTANCE_ID is required"; exit 1; fi; \
	PLAN="${PLAN}"; if [ -z "$$PLAN" ]; then PLAN=jmeter_test_plan.jmx; fi; \
	DEST="${DEST}"; if [ -z "$$DEST" ]; then DEST=$$(basename "$$PLAN"); fi; \
	if [ ! -f "$$PLAN" ]; then ALT="tests/performance/$$(basename "$$PLAN")"; if [ -f "$$ALT" ]; then PLAN="$$ALT"; else echo "Plan file '$$PLAN' not found"; exit 1; fi; fi; \
	B64=$$(base64 < "$$PLAN" | tr -d '\n'); \
	echo "Uploading '$$PLAN' to EC2:/home/ssm-user/$$DEST via SSM inline"; \
	PARAMS_FILE=$$(mktemp); \
	printf '%s\n' '{' '  "commands": [' '    "bash -lc \"printf %s '\''__B64__'\'' | base64 -d > /home/ssm-user/__DEST__ && ls -l /home/ssm-user/__DEST__\""' '  ]' '}' > "$$PARAMS_FILE"; \
	B64_ESC=$$(printf '%s' "$$B64" | sed -e 's/[&|]/\\\&/g'); \
	DEST_ESC=$$(printf '%s' "$$DEST" | sed -e 's/[&|]/\\\&/g'); \
	sed -i.bak -e "s|__B64__|$$B64_ESC|g" -e "s|__DEST__|$$DEST_ESC|g" "$$PARAMS_FILE"; rm -f "$$PARAMS_FILE.bak"; \
	CMD_ID=$$(aws ssm send-command --region $(AWS_REGION) --instance-ids "$$ID" \
		--document-name AWS-RunShellScript \
		--parameters file://$$PARAMS_FILE \
		--query 'Command.CommandId' --output text); \
	rm -f "$$PARAMS_FILE"; \
	aws ssm wait command-executed --region $(AWS_REGION) --instance-id "$$ID" --command-id "$$CMD_ID"; \
	echo "Plan uploaded to /home/ssm-user/$${DEST}"

.PHONY: jmeter-start-instance jmeter-stop-instance jmeter-version-remote jmeter-ssm-shell jmeter-copy-plan-ssm-inline jmeter-ec2-id jmeter-private-ip
