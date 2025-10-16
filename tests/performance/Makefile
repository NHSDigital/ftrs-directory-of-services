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
JENKINS ?= false
SSH_USERNAME ?= ec2-user
SSH_KEY_PATH ?=

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

# Discover JMeter EC2 instance by tag Role=jmeter (first match in account/environment)
JMETER_INSTANCE_ID := $(shell aws ec2 describe-instances --region $(AWS_REGION) \
	--filters 'Name=tag:Role,Values=jmeter' 'Name=instance-state-name,Values=pending,running,stopping,stopped' \
	--query 'Reservations[].Instances[0].InstanceId' --output text 2>/dev/null)
JMETER_PRIVATE_IP := $(shell aws ec2 describe-instances --region $(AWS_REGION) \
	--instance-ids $(JMETER_INSTANCE_ID) \
	--query 'Reservations[].Instances[0].PrivateIpAddress' --output text 2>/dev/null)

jmeter-ec2-id:
	@echo "JMeter EC2 instance id: $(JMETER_INSTANCE_ID)"

jmeter-private-ip:
	@echo "JMeter EC2 private IP: $(JMETER_PRIVATE_IP)"

jmeter-start: ## Start the JMeter EC2 instance and wait until running
	@if [ "$(JMETER_INSTANCE_ID)" = "None" ] || [ -z "$(JMETER_INSTANCE_ID)" ]; then \
		echo "Could not find a JMeter instance (Role=jmeter). Ensure Terraform applied"; exit 1; \
	fi
	aws ec2 start-instances --region $(AWS_REGION) --instance-ids $(JMETER_INSTANCE_ID) >/dev/null
	aws ec2 wait instance-running --region $(AWS_REGION) --instance-ids $(JMETER_INSTANCE_ID)
	@echo "JMeter instance started: $(JMETER_INSTANCE_ID)"

jmeter-stop: ## Stop the JMeter EC2 instance and wait until stopped
	@if [ "$(JMETER_INSTANCE_ID)" = "None" ] || [ -z "$(JMETER_INSTANCE_ID)" ]; then \
		echo "Could not find a JMeter instance (Role=jmeter). Ensure Terraform applied"; exit 1; \
	fi
	aws ec2 stop-instances --region $(AWS_REGION) --instance-ids $(JMETER_INSTANCE_ID) >/dev/null
	aws ec2 wait instance-stopped --region $(AWS_REGION) --instance-ids $(JMETER_INSTANCE_ID)
	@echo "JMeter instance stopped: $(JMETER_INSTANCE_ID)"

jmeter-ssh: ## SSH into the JMeter EC2 (requires VPN and SSH key); set SSH_KEY_PATH=~/.ssh/key.pem if needed
	@if [ -z "$(SSH_KEY_PATH)" ]; then echo "SSH_KEY_PATH is required (path to your .pem)"; exit 1; fi
	@if [ -z "$(JMETER_PRIVATE_IP)" ] || [ "$(JMETER_PRIVATE_IP)" = "None" ]; then echo "Private IP not found; ensure instance is running"; exit 1; fi
	ssh -o StrictHostKeyChecking=no -i $(SSH_KEY_PATH) $(SSH_USERNAME)@$(JMETER_PRIVATE_IP)

jmeter-copy-plan: ## Copy a JMeter plan to the EC2 via scp (PLAN=IS_Test_Plan.jmx)
	@if [ -z "$(SSH_KEY_PATH)" ]; then echo "SSH_KEY_PATH is required (path to your .pem)"; exit 1; fi
	@if [ -z "$(PLAN)" ]; then echo "PLAN is required, e.g., PLAN=IS_Test_Plan.jmx"; exit 1; fi
	@if [ -z "$(JMETER_PRIVATE_IP)" ] || [ "$(JMETER_PRIVATE_IP)" = "None" ]; then echo "Private IP not found; ensure instance is running"; exit 1; fi
	scp -o StrictHostKeyChecking=no -i $(SSH_KEY_PATH) $(PLAN) $(SSH_USERNAME)@$(JMETER_PRIVATE_IP):/home/$(SSH_USERNAME)/$(PLAN)

jmeter-version-remote: ## Print JMeter version on the EC2 using SSM
	@if [ -z "$(JMETER_INSTANCE_ID)" ] || [ "$(JMETER_INSTANCE_ID)" = "None" ]; then echo "Instance not found"; exit 1; fi
	aws ssm start-session --region $(AWS_REGION) --target $(JMETER_INSTANCE_ID) --document-name AWS-StartInteractiveCommand --parameters 'command=["jmeter -v"]'

jmeter-run-remote: ## Run a JMeter plan on the EC2 using SSM (PLAN=<file in home dir>, ARGS="-n -l out.jtl ...")
	@if [ -z "$(JMETER_INSTANCE_ID)" ] || [ "$(JMETER_INSTANCE_ID)" = "None" ]; then echo "Instance not found"; exit 1; fi
	@if [ -z "$(PLAN)" ]; then echo "PLAN is required, e.g., PLAN=IS_Test_Plan.jmx"; exit 1; fi
	aws ssm start-session --region $(AWS_REGION) --target $(JMETER_INSTANCE_ID) --document-name AWS-StartInteractiveCommand --parameters 'command=["jmeter $(ARGS) -t $(PLAN)"]'
