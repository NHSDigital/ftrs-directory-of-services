PROJECT_NAME := ftrs-dos
ENVIRONMENT ?= dev
SERVICE ?= is-performance
PYTHON_VERSION ?= 3.12
TEST_DIR := parameter_files
WORKSPACE_PARAMETER_FILES_BUCKET := ${PROJECT_NAME}-${ENVIRONMENT}-${SERVICE}-parameter-files-bucket-${WORKSPACE}
MAIN_PARAMETER_FILES_BUCKET := ${PROJECT_NAME}-${ENVIRONMENT}-${SERVICE}-parameter-files-bucket
JMETER_PLUGINS_MANAGER_VERSION := 1.11
CMDRUNNER_VERSION := 2.3

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
		$(MAKE) _install-dependency name="$${plugin}"; \
	done

# Discover JMeter EC2 instance by a configurable filter (first match in account/environment)
ifeq ($(origin JMETER_INSTANCE_ID), undefined)
JMETER_INSTANCE_ID := $(shell aws ec2 describe-instances --region $(AWS_REGION) \
	--filters $(foreach f,$(JMETER_FILTERS),'$(f)') 'Name=instance-state-name,Values=pending,running,stopping,stopped' \
	--query 'Reservations[].Instances[0].InstanceId' --output text 2>/dev/null)
endif
JMETER_PRIVATE_IP := $(shell aws ec2 describe-instances --region $(AWS_REGION) \
	--instance-ids $(JMETER_INSTANCE_ID) \
	--query 'Reservations[].Instances[0].PrivateIpAddress' --output text 2>/dev/null)

jmeter-ec2-id:
	@echo "JMeter EC2 instance id: $(JMETER_INSTANCE_ID)"

jmeter-private-ip:
	@echo "JMeter EC2 private IP: $(JMETER_PRIVATE_IP)"

jmeter-start-instance: ## Start the JMeter EC2 instance and wait until running
	@ID="$(JMETER_INSTANCE_ID)"; \
	if [ -z "$$ID" ] || [ "$$ID" = "None" ]; then \
		ID=$$(aws ec2 describe-instances --region $(AWS_REGION) \
		--filters $(JMETER_FILTERS) 'Name=instance-state-name,Values=pending,running,stopping,stopped' \
		--query 'Reservations[].Instances[0].InstanceId' --output text 2>/dev/null); \
	fi; \
	if [ -z "$$ID" ] || [ "$$ID" = "None" ]; then \
		echo "Could not find a JMeter instance. Check JMETER_FILTERS or pass JMETER_INSTANCE_ID explicitly"; exit 1; \
	fi; \
	aws ec2 start-instances --region $(AWS_REGION) --instance-ids "$$ID" >/dev/null; \
	aws ec2 wait instance-running --region $(AWS_REGION) --instance-ids "$$ID"; \
	echo "JMeter instance started: $$ID"

jmeter-stop-instance: ## Stop the JMeter EC2 instance and wait until stopped
	@ID="$(JMETER_INSTANCE_ID)"; \
	if [ -z "$$ID" ] || [ "$$ID" = "None" ]; then \
		ID=$$(aws ec2 describe-instances --region $(AWS_REGION) \
		--filters $(JMETER_FILTERS) 'Name=instance-state-name,Values=pending,running,stopping,stopped' \
		--query 'Reservations[].Instances[0].InstanceId' --output text 2>/dev/null); \
	fi; \
	if [ -z "$$ID" ] || [ "$$ID" = "None" ]; then echo "Instance not found"; exit 1; fi; \
	aws ec2 stop-instances --region $(AWS_REGION) --instance-ids "$$ID" >/dev/null; \
	aws ec2 wait instance-stopped --region $(AWS_REGION) --instance-ids "$$ID"; \
	echo "JMeter instance stopped: $$ID"

jmeter-version-remote: ## Print JMeter version on the EC2 using SSM
	@ID="$(JMETER_INSTANCE_ID)"; \
	if [ -z "$$ID" ] || [ "$$ID" = "None" ]; then \
		ID=$$(aws ec2 describe-instances --region $(AWS_REGION) \
		--filters $(JMETER_FILTERS) 'Name=instance-state-name,Values=pending,running,stopping,stopped' \
		--query 'Reservations[].Instances[0].InstanceId' --output text 2>/dev/null); \
	fi; \
	if [ -z "$$ID" ] || [ "$$ID" = "None" ]; then echo "Instance not found"; exit 1; fi; \
	aws ssm start-session --region $(AWS_REGION) --target "$$ID" --document-name AWS-StartInteractiveCommand --parameters 'command=["jmeter -v"]'

jmeter-run-remote: ## Run a JMeter plan on the EC2 using SSM (PLAN=<file in home dir>, ARGS="-n -l out.jtl ...")
	@ID="$(JMETER_INSTANCE_ID)"; \
	if [ -z "$$ID" ] || [ "$$ID" = "None" ]; then \
		ID=$$(aws ec2 describe-instances --region $(AWS_REGION) \
		--filters $(JMETER_FILTERS) 'Name=instance-state-name,Values=pending,running,stopping,stopped' \
		--query 'Reservations[].Instances[0].InstanceId' --output text 2>/dev/null); \
	fi; \
	if [ -z "$$ID" ] || [ "$$ID" = "None" ]; then echo "Instance not found"; exit 1; fi; \
	if [ -z "$(PLAN)" ]; then echo "PLAN is required, e.g., PLAN=jmeter_test_plan.jmx"; exit 1; fi; \
	aws ssm start-session --region $(AWS_REGION) --target "$$ID" --document-name AWS-StartInteractiveCommand --parameters 'command=["bash -lc \"set -o pipefail; cd /home/ssm-user; if command -v sudo >/dev/null 2>&1; then sudo install -d -m 775 -o ssm-user -g ssm-user report; sudo install -d -m 755 -o ssm-user -g ssm-user parameter_files; sudo install -m 664 -o ssm-user -g ssm-user /dev/null jmeter.log; sudo install -m 664 -o ssm-user -g ssm-user /dev/null jmeter.out; if [ -e $(PLAN) ]; then sudo chown ssm-user:ssm-user $(PLAN); sudo chmod 644 $(PLAN); fi; if [ -e odscodes.csv ]; then sudo chown ssm-user:ssm-user odscodes.csv; sudo chmod 644 odscodes.csv; fi; else mkdir -p report parameter_files; chmod 775 report; chmod 755 parameter_files; : > jmeter.log; : > jmeter.out; chmod 664 jmeter.log jmeter.out; if [ -e $(PLAN) ]; then chmod 644 $(PLAN); fi; if [ -e odscodes.csv ]; then chmod 644 odscodes.csv; fi; fi; if command -v stdbuf >/dev/null 2>&1; then stdbuf -oL -eL jmeter $(ARGS) -t \\\"$(PLAN)\\\" -j jmeter.log | tee -a jmeter.out; else jmeter $(ARGS) -t \\\"$(PLAN)\\\" -j jmeter.log | tee -a jmeter.out; fi\""]'

jmeter-ssm-shell: ## Open an interactive SSM shell to the JMeter EC2 instance
	@ID="$(JMETER_INSTANCE_ID)"; \
	if [ -z "$$ID" ] || [ "$$ID" = "None" ]; then \
		ID=$$(aws ec2 describe-instances --region $(AWS_REGION) \
		--filters $(JMETER_FILTERS) 'Name=instance-state-name,Values=pending,running,stopping,stopped' \
		--query 'Reservations[].Instances[0].InstanceId' --output text 2>/dev/null); \
	fi; \
	if [ -z "$$ID" ] || [ "$$ID" = "None" ]; then echo "Instance not found"; exit 1; fi; \
	aws ssm start-session --region $(AWS_REGION) --target "$$ID"

jmeter-copy-plan-ssm-inline: ## [PLAN=jmeter_test_plan.jmx] [DEST=jmeter_test_plan.jmx]
	@ID="$(JMETER_INSTANCE_ID)"; \
	if [ -z "$$ID" ] || [ "$$ID" = "None" ]; then \
		ID=$$(aws ec2 describe-instances --region $(AWS_REGION) \
		--filters $(JMETER_FILTERS) 'Name=instance-state-name,Values=pending,running,stopping,stopped' \
		--query 'Reservations[].Instances[0].InstanceId' --output text 2>/dev/null); \
	fi; \
	if [ -z "$$ID" ] || [ "$$ID" = "None" ]; then echo "Instance not found"; exit 1; fi; \
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

# New: copy ODS codes CSV inline via SSM
jmeter-copy-odscodes-ssm-inline: ## Copy tests/performance/parameter_files/odscodes.csv to EC2:/home/ssm-user/parameter_files/odscodes.csv
	@ID="$(JMETER_INSTANCE_ID)"; \
	if [ -z "$$ID" ] || [ "$$ID" = "None" ]; then \
		ID=$$(aws ec2 describe-instances --region $(AWS_REGION) \
		--filters $(JMETER_FILTERS) 'Name=instance-state-name,Values=pending,running,stopping,stopped' \
		--query 'Reservations[].Instances[0].InstanceId' --output text 2>/dev/null); \
	fi; \
	if [ -z "$$ID" ] || [ "$$ID" = "None" ]; then echo "Instance not found"; exit 1; fi; \
	SRC="tests/performance/parameter_files/odscodes.csv"; DEST="/home/ssm-user/parameter_files/odscodes.csv"; \
	if [ ! -f "$$SRC" ]; then echo "Missing $$SRC"; exit 1; fi; \
	B64=$$(base64 < "$$SRC" | tr -d '\n'); \
	PARAMS_FILE=$$(mktemp); \
	printf '%s\n' '{' '  "commands": [' '    "bash -lc \"mkdir -p /home/ssm-user/parameter_files && printf %s '\''__B64__'\'' | base64 -d > __DEST__ && ls -l __DEST__\""' '  ]' '}' > "$$PARAMS_FILE"; \
	B64_ESC=$$(printf '%s' "$$B64" | sed -e 's/[&|]/\\\&/g'); \
	DEST_ESC=$$(printf '%s' "$$DEST" | sed -e 's/[&|]/\\\&/g'); \
	sed -i.bak -e "s|__B64__|$$B64_ESC|g" -e "s|__DEST__|$$DEST_ESC|g" "$$PARAMS_FILE"; rm -f "$$PARAMS_FILE.bak"; \
	CMD_ID=$$(aws ssm send-command --region $(AWS_REGION) --instance-ids "$$ID" \
		--document-name AWS-RunShellScript \
		--parameters file://$$PARAMS_FILE \
		--query 'Command.CommandId' --output text); \
	rm -f "$$PARAMS_FILE"; \
	aws ssm wait command-executed --region $(AWS_REGION) --instance-id "$$ID" --command-id "$$CMD_ID"; \
	echo "odscodes.csv uploaded to $$DEST"

# Build and print the SSM parameters JSON for the copy step (no AWS call)
jmeter-copy-plan-params-dry-run: ## [PLAN=<local file>] [DEST=<remote name>] Build and print the SSM parameters JSON used for upload (no execution)
	@PLAN="${PLAN}"; if [ -z "$$PLAN" ]; then PLAN=jmeter_test_plan.jmx; fi; \
	DEST="${DEST}"; if [ -z "$$DEST" ]; then DEST=$$(basename "$$PLAN"); fi; \
	if [ ! -f "$$PLAN" ]; then ALT="tests/performance/$$(basename "$$PLAN")"; if [ -f "$$ALT" ]; then PLAN="$$ALT"; else echo "Plan file '$$PLAN' not found"; exit 1; fi; fi; \
	B64=$$(base64 < "$$PLAN" | tr -d '\n'); \
	PARAMS_FILE=$$(mktemp); \
	printf '%s\n' '{' '  "commands": [' '    "bash -lc \"printf %s '\''__B64__'\'' | base64 -d > /home/ssm-user/__DEST__ && ls -l /home/ssm-user/__DEST__\""' '  ]' '}' > "$$PARAMS_FILE"; \
	B64_ESC=$$(printf '%s' "$$B64" | sed -e 's/[&|]/\\\&/g'); \
	DEST_ESC=$$(printf '%s' "$$DEST" | sed -e 's/[&|]/\\\&/g'); \
	sed -i.bak -e "s|__B64__|$$B64_ESC|g" -e "s|__DEST__|$$DEST_ESC|g" "$$PARAMS_FILE"; rm -f "$$PARAMS_FILE.bak"; \
	echo "--- BEGIN SSM parameters JSON ---"; \
	cat "$$PARAMS_FILE"; \
	echo "--- END SSM parameters JSON ---"; \
	rm -f "$$PARAMS_FILE"

# One-shot: copy the plan onto EC2 via SSM inline, then run it via SSM
jmeter-copy-and-run: ## [PLAN=jmeter_test_plan.jmx] [DEST=jmeter_test_plan.jmx] [ARGS='-n -l result.jtl ...'] Copy plan to EC2 and run it (no SSH, no S3)
	@P="${PLAN}"; if [ -z "$$P" ]; then P=jmeter_test_plan.jmx; fi; \
	D="${DEST}"; if [ -z "$$D" ]; then D=$$(basename "$$P"); fi; \
	echo "Ensuring odscodes.csv is present on EC2"; \
	$(MAKE) -f $(lastword $(MAKEFILE_LIST)) jmeter-copy-odscodes-ssm-inline; \
	echo "Copying '$$P' to EC2 as '$$D' and running with ARGS: $(ARGS)"; \
	$(MAKE) -f $(lastword $(MAKEFILE_LIST)) jmeter-copy-plan-ssm-inline PLAN="$$P" DEST="$$D" && \
	$(MAKE) -f $(lastword $(MAKEFILE_LIST)) jmeter-run-remote PLAN="$$D" ARGS="$(ARGS)"

# Inline fetch: stream artifacts over SSM session (no S3). Defaults to result.jtl only.
jmeter-fetch-artifacts-inline: ## [REMOTE_OUT_JTL=result.jtl] [INCLUDE_REPORT=false] [REMOTE_REPORT_DIR=report] [LOCAL_ARTIFACTS_DIR=tests/performance/artifacts]
	@ID="$(JMETER_INSTANCE_ID)"; \
	if [ -z "$$ID" ] || [ "$$ID" = "None" ]; then \
		ID=$$(aws ec2 describe-instances --region $(AWS_REGION) \
		--filters $(JMETER_FILTERS) 'Name=instance-state-name,Values=pending,running,stopping,stopped' \
		--query 'Reservations[].Instances[0].InstanceId' --output text 2>/dev/null); \
	fi; \
	if [ -z "$$ID" ] || [ "$$ID" = "None" ]; then echo "Instance not found"; exit 1; fi; \
	OUT="${REMOTE_OUT_JTL}"; if [ -z "$$OUT" ]; then OUT=result.jtl; fi; \
	REP="${REMOTE_REPORT_DIR}"; if [ -z "$$REP" ]; then REP=report; fi; \
	INC="${INCLUDE_REPORT}"; if [ -z "$$INC" ]; then INC=false; fi; \
	LDIR="${LOCAL_ARTIFACTS_DIR}"; if [ -z "$$LDIR" ]; then LDIR=tests/performance/artifacts; fi; \
	mkdir -p "$$LDIR"; \
	TMPDIR=$$(mktemp -d); B64FILE="$$TMPDIR/artifacts.inline.b64"; TARFILE="$$TMPDIR/artifacts.inline.tar.gz"; \
	echo "Fetching '$$OUT'"; if [ "$$INC" = "true" ]; then echo " and '$$REP'"; fi; \
	RCMD="set -o pipefail; cd /home/ssm-user; echo __B64_START__; LIST=; if [ -f \"$$OUT\" ]; then LIST=\"$$LIST $$OUT\"; fi; if [ \"$$INC\" = \"true\" ] && [ -d \"$$REP\" ]; then LIST=\"$$LIST $$REP\"; fi; if [ -z \"$$LIST\" ]; then echo __NO_FILES__; else tar czf - $$LIST 2>/dev/null | base64; fi; echo __B64_END__"; \
	PARAMS_FILE="$$TMPDIR/params.json"; \
	ESC_RCMD=$$(printf '%s' "$$RCMD" | sed -e 's/\\/\\\\/g' -e 's/\"/\\\"/g'); \
	printf '%s' '{"command":["bash -lc \"'"$$ESC_RCMD"'\""]}' > "$$PARAMS_FILE"; \
	aws ssm start-session --region $(AWS_REGION) --target "$$ID" \
		--document-name AWS-StartInteractiveCommand \
		--parameters file://"$$PARAMS_FILE" \
		| awk '/__B64_START__/{flag=1;next}/__B64_END__/{flag=0}flag' > "$$B64FILE"; \
	if grep -q "__NO_FILES__" "$$B64FILE"; then echo "No artifacts present on EC2 (no $$OUT nor $$REP)"; rm -rf "$$TMPDIR"; exit 1; fi; \
	# Attempt to decode tar; if empty, fallback to fetching only result.jtl directly \
	( base64 --decode < "$$B64FILE" > "$$TARFILE" 2>/dev/null || base64 -D < "$$B64FILE" > "$$TARFILE" ); \
	if [ ! -s "$$TARFILE" ]; then \
		echo "No artifacts received (empty tar). If report is large, consider narrowing contents)"; \
		echo "Falling back to single-file fetch of '$$OUT'"; \
		OUTFILE="$$LDIR/$$(basename "$$OUT")"; \
		B64FILE2="$$TMPDIR/single.inline.b64"; \
		RCMD2="set -o pipefail; cd /home/ssm-user; echo __B64_START__; if [ -f \"$$OUT\" ]; then base64 \"$$OUT\"; else echo __NO_RESULT__; fi; echo __B64_END__"; \
		PARAMS_FILE2="$$TMPDIR/params2.json"; \
		ESC_RCMD2=$$(printf '%s' "$$RCMD2" | sed -e 's/\\/\\\\/g' -e 's/\"/\\\"/g'); \
		printf '%s' '{"command":["bash -lc \"'"$$ESC_RCMD2"'\""]}' > "$$PARAMS_FILE2"; \
		aws ssm start-session --region $(AWS_REGION) --target "$$ID" \
		--document-name AWS-StartInteractiveCommand \
		--parameters file://"$$PARAMS_FILE2" \
		| awk '/__B64_START__/{flag=1;next}/__B64_END__/{flag=0}flag' > "$$B64FILE2"; \
		if grep -q "__NO_RESULT__" "$$B64FILE2"; then echo "Remote file '$$OUT' not found"; rm -rf "$$TMPDIR"; exit 1; fi; \
		( base64 --decode < "$$B64FILE2" > "$$OUTFILE" 2>/dev/null || base64 -D < "$$B64FILE2" > "$$OUTFILE" ); \
		if [ ! -s "$$OUTFILE" ]; then echo "Failed to fetch '$$OUT'"; rm -rf "$$TMPDIR"; exit 1; fi; \
		ls -lh "$$OUTFILE"; \
		rm -rf "$$TMPDIR"; \
		exit 0; \
	fi; \
	tar -xzf "$$TARFILE" -C "$$LDIR"; \
	echo "Artifacts extracted to $$LDIR"; \
	rm -rf "$$TMPDIR"

# Convenience: run a plan already on EC2 with required properties
jmeter-run-remote-with-properties: ## PLAN=<file on EC2> SERVICEENDPOINT=<host> BEARER_TOKEN=<jwt> [OUT_JTL=result.jtl] [REPORT_DIR=report] [EXTRA_ARGS='...']
	@if [ -z "$(PLAN)" ]; then echo "PLAN is required (file must exist on EC2)"; exit 1; fi; \
	if [ -z "$(SERVICEENDPOINT)" ]; then echo "SERVICEENDPOINT is required"; exit 1; fi; \
	if [ -z "$(BEARER_TOKEN)" ]; then echo "BEARER_TOKEN is required"; exit 1; fi; \
	ARGS_BUILT="-n -l $(OUT_JTL) -J serviceendpoint=$(SERVICEENDPOINT) -J bearer_token=$(BEARER_TOKEN) -f -e -o $(REPORT_DIR) $(EXTRA_ARGS)"; \
	$(MAKE) -f $(lastword $(MAKEFILE_LIST)) jmeter-run-remote PLAN="$(PLAN)" ARGS="$$ARGS_BUILT"

# Convenience: copy plan to EC2 then run with required properties
jmeter-copy-and-run-with-properties: ## PLAN=<local .jmx> [DEST=<remote name>] SERVICEENDPOINT=<host> BEARER_TOKEN=<jwt> [OUT_JTL=result.jtl] [REPORT_DIR=report] [EXTRA_ARGS='...']
	@if [ -z "$(PLAN)" ]; then echo "PLAN is required (local .jmx path)"; exit 1; fi; \
	if [ -z "$(SERVICEENDPOINT)" ]; then echo "SERVICEENDPOINT is required"; exit 1; fi; \
	if [ -z "$(BEARER_TOKEN)" ]; then echo "BEARER_TOKEN is required"; exit 1; fi; \
	ARGS_BUILT="-n -l $(OUT_JTL) -J serviceendpoint=$(SERVICEENDPOINT) -J bearer_token=$(BEARER_TOKEN) -f -e -o $(REPORT_DIR) $(EXTRA_ARGS)"; \
	$(MAKE) -f $(lastword $(MAKEFILE_LIST)) jmeter-copy-and-run PLAN="$(PLAN)" DEST="$(DEST)" ARGS="$$ARGS_BUILT"

# Convenience: start instance, copy plan, run it, optionally stop
jmeter-prep-copy-and-run: ## [PLAN=jmeter_test_plan.jmx] [DEST=jmeter_test_plan.jmx] [ARGS='-n -l result.jtl ...'] [STOP_AFTER=true] Start instance, copy plan via SSM, run it; optionally stop instance
	@echo "Starting EC2 instance (if not already running)"
	$(MAKE) -f $(lastword $(MAKEFILE_LIST)) jmeter-start-instance
	@echo "Copying plan and running JMeter on EC2"
	$(MAKE) -f $(lastword $(MAKEFILE_LIST)) jmeter-copy-and-run PLAN="${PLAN}" DEST="${DEST}" ARGS="$(ARGS)"
	@if [ "${STOP_AFTER}" = "true" ]; then \
		echo "Stopping EC2 instance"; \
		$(MAKE) -f $(lastword $(MAKEFILE_LIST)) jmeter-stop-instance; \
	else \
		echo "Leaving EC2 instance running (STOP_AFTER!=true)"; \
	fi

# Convenience: start, copy, run with properties, optionally stop
jmeter-prep-copy-and-run-with-properties: ## PLAN=<local .jmx> [DEST=<remote name>] SERVICEENDPOINT=<host> BEARER_TOKEN=<jwt> [OUT_JTL=result.jtl] [REPORT_DIR=report] [EXTRA_ARGS='...'] [STOP_AFTER=true]
	@if [ -z "$(PLAN)" ]; then echo "PLAN is required (local .jmx path)"; exit 1; fi; \
	if [ -z "$(SERVICEENDPOINT)" ]; then echo "SERVICEENDPOINT is required"; exit 1; fi; \
	if [ -z "$(BEARER_TOKEN)" ]; then echo "BEARER_TOKEN is required"; exit 1; fi; \
	ARGS_BUILT="-n -l $(OUT_JTL) -J serviceendpoint=$(SERVICEENDPOINT) -J bearer_token=$(BEARER_TOKEN) -f -e -o $(REPORT_DIR) $(EXTRA_ARGS)"; \
	$(MAKE) -f $(lastword $(MAKEFILE_LIST)) jmeter-prep-copy-and-run PLAN="$(PLAN)" DEST="$(DEST)" ARGS="$$ARGS_BUILT" STOP_AFTER="$(STOP_AFTER)"

# Convenience: start, copy, run with properties, fetch artifacts, optionally stop (no S3)
jmeter-prep-copy-run-and-fetch-with-properties: ## PLAN=<local .jmx> [DEST=<remote name>] SERVICEENDPOINT=<host> BEARER_TOKEN=<jwt> [OUT_JTL=result.jtl] [REPORT_DIR=report] [EXTRA_ARGS='...'] [LOCAL_ARTIFACTS_DIR=tests/performance/artifacts] [INCLUDE_REPORT=false] [BUILD_LOCAL_REPORT=true] [STOP_AFTER=true]
	@if [ -z "$(PLAN)" ]; then echo "PLAN is required (local .jmx path)"; exit 1; fi; \
	if [ -z "$(SERVICEENDPOINT)" ]; then echo "SERVICEENDPOINT is required"; exit 1; fi; \
	if [ -z "$(BEARER_TOKEN)" ]; then echo "BEARER_TOKEN is required"; exit 1; fi; \
	O="${OUT_JTL}"; if [ -z "$$O" ]; then O=result.jtl; fi; \
	R="${REPORT_DIR}"; if [ -z "$$R" ]; then R=report; fi; \
	LDIR="${LOCAL_ARTIFACTS_DIR}"; if [ -z "$$LDIR" ]; then LDIR=tests/performance/artifacts; fi; \
	INC="${INCLUDE_REPORT}"; if [ -z "$$INC" ]; then INC=false; fi; \
	BLR="${BUILD_LOCAL_REPORT}"; if [ -z "$$BLR" ]; then BLR=true; fi; \
	STATUS=0; \
	$(MAKE) -f $(lastword $(MAKEFILE_LIST)) jmeter-prep-copy-and-run-with-properties PLAN="$(PLAN)" DEST="$(DEST)" SERVICEENDPOINT="$(SERVICEENDPOINT)" BEARER_TOKEN="$(BEARER_TOKEN)" OUT_JTL="$$O" REPORT_DIR="$$R" EXTRA_ARGS="$(EXTRA_ARGS)" STOP_AFTER="false" || STATUS=$$?; \
	if [ $$STATUS -eq 0 ]; then \
		if [ "$$INC" = "true" ]; then \
		echo "Fetching JTL and report via SSM (may be large)"; \
		$(MAKE) -f $(lastword $(MAKEFILE_LIST)) jmeter-fetch-artifacts-inline REMOTE_OUT_JTL="$$O" REMOTE_REPORT_DIR="$$R" LOCAL_ARTIFACTS_DIR="$$LDIR" INCLUDE_REPORT="true" || STATUS=$$?; \
		else \
		echo "Fetching only JTL via SSM"; \
		$(MAKE) -f $(lastword $(MAKEFILE_LIST)) jmeter-fetch-jtl-inline REMOTE_OUT_JTL="$$O" LOCAL_ARTIFACTS_DIR="$$LDIR" || STATUS=$$?; \
		OUTPATH="$$LDIR/$$(basename "$$O")"; \
		if [ $$STATUS -eq 0 ] && [ -f "$$OUTPATH" ] && [ -s "$$OUTPATH" ] && [ "$$BLR" = "true" ]; then \
		echo "Building local HTML report from fetched JTL"; \
		$(MAKE) -f $(lastword $(MAKEFILE_LIST)) jmeter-build-report-local LOCAL_JTL="$$OUTPATH" LOCAL_REPORT_DIR="$$LDIR/report_local" || STATUS=$$?; \
		fi; \
		fi; \
	fi; \
	if [ "$(STOP_AFTER)" = "true" ]; then $(MAKE) -f $(lastword $(MAKEFILE_LIST)) jmeter-stop-instance; else echo "Leaving EC2 instance running (STOP_AFTER!=true)"; fi; \
	exit $$STATUS

# Helper: verify a file exists on EC2 under /home/ssm-user
jmeter-verify-plan-remote: ## DEST=<remote filename> Verify the uploaded plan exists and show its details on EC2
	@ID="$(JMETER_INSTANCE_ID)"; \
	if [ -z "$$ID" ] || [ "$$ID" = "None" ]; then \
		ID=$$(aws ec2 describe-instances --region $(AWS_REGION) \
		--filters $(JMETER_FILTERS) 'Name=instance-state-name,Values=pending,running,stopping,stopped' \
		--query 'Reservations[].Instances[0].InstanceId' --output text 2>/dev/null); \
	fi; \
	if [ -z "$$ID" ] || [ "$$ID" = "None" ]; then echo "Instance not found"; exit 1; fi; \
	D="${DEST}"; if [ -z "$$D" ]; then D=jmeter_test_plan.jmx; fi; \
	aws ssm start-session --region $(AWS_REGION) --target "$$ID" --document-name AWS-StartInteractiveCommand --parameters 'command=["bash -lc \"set -o pipefail; ls -l /home/ssm-user/\\\"'"'"'$$D'"'"'\\\"; file /home/ssm-user/\\\"'"'"'$$D'"'"'\\\" || true\""]'

# Fetch only the JTL via SSM (safer for large reports)
jmeter-fetch-jtl-inline: ## [REMOTE_OUT_JTL=result.jtl] [LOCAL_ARTIFACTS_DIR=tests/performance/artifacts] Fetch only the JTL file via SSM
	@ID="$(JMETER_INSTANCE_ID)"; \
	if [ -z "$$ID" ] || [ "$$ID" = "None" ]; then \
		ID=$$(aws ec2 describe-instances --region $(AWS_REGION) \
		--filters $(JMETER_FILTERS) 'Name=instance-state-name,Values=pending,running,stopping,stopped' \
		--query 'Reservations[].Instances[0].InstanceId' --output text 2>/dev/null); \
	fi; \
	if [ -z "$$ID" ] || [ "$$ID" = "None" ]; then echo "Instance not found"; exit 1; fi; \
	OUT="${REMOTE_OUT_JTL}"; if [ -z "$$OUT" ]; then OUT=result.jtl; fi; \
	LDIR="${LOCAL_ARTIFACTS_DIR}"; if [ -z "$$LDIR" ]; then LDIR=tests/performance/artifacts; fi; \
	mkdir -p "$$LDIR"; \
	TMPDIR=$$(mktemp -d); B64FILE="$$TMPDIR/jtl.inline.b64"; \
	echo "Fetching '$$OUT' via SSM"; \
	RCMD="set -o pipefail; cd /home/ssm-user; echo __B64_START__; if [ -f \"$$OUT\" ]; then base64 \"$$OUT\"; else echo __NO_RESULT__; fi; echo __B64_END__"; \
	PARAMS_FILE="$$TMPDIR/params.json"; \
	ESC_RCMD=$$(printf '%s' "$$RCMD" | sed -e 's/\\/\\\\/g' -e 's/\"/\\\"/g'); \
	printf '%s' '{"command":["bash -lc \"'"$$ESC_RCMD"'\""]}' > "$$PARAMS_FILE"; \
	aws ssm start-session --region $(AWS_REGION) --target "$$ID" \
		--document-name AWS-StartInteractiveCommand \
		--parameters file://"$$PARAMS_FILE" \
		| awk '/__B64_START__/{flag=1;next}/__B64_END__/{flag=0}flag' > "$$B64FILE"; \
	if grep -q "__NO_RESULT__" "$$B64FILE"; then echo "Remote file '$$OUT' not found"; rm -rf "$$TMPDIR"; exit 1; fi; \
	OUTFILE="$$LDIR/$$(basename "$$OUT")"; \
	( base64 --decode < "$$B64FILE" > "$$OUTFILE" 2>/dev/null || base64 -D < "$$B64FILE" > "$$OUTFILE" ); \
	if [ ! -s "$$OUTFILE" ]; then echo "Failed to fetch '$$OUT'"; rm -rf "$$TMPDIR"; exit 1; fi; \
	ls -lh "$$OUTFILE"; \
	rm -rf "$$TMPDIR"

# Build JMeter HTML report locally from a JTL
jmeter-build-report-local: ## [LOCAL_JTL=tests/performance/artifacts/result.jtl] [LOCAL_REPORT_DIR=tests/performance/artifacts/report_local] Build local HTML report from a JTL
	@JTL="${LOCAL_JTL}"; if [ -z "$$JTL" ]; then JTL=tests/performance/artifacts/result.jtl; fi; \
	RDIR="${LOCAL_REPORT_DIR}"; if [ -z "$$RDIR" ]; then RDIR=tests/performance/artifacts/report_local; fi; \
	if [ ! -f "$$JTL" ]; then echo "Local JTL not found at '$$JTL'"; exit 1; fi; \
	rm -rf "$$RDIR" && mkdir -p "$$RDIR"; \
	echo "Generating local report at '$$RDIR' from '$$JTL'"; \
	jmeter -g "$$JTL" -f -e -o "$$RDIR"; \
	ls -l "$$RDIR" | head -n 20

.PHONY: jmeter-start-instance jmeter-stop-instance jmeter-version-remote jmeter-run-remote jmeter-ssm-shell jmeter-copy-plan-ssm-inline jmeter-copy-odscodes-ssm-inline jmeter-copy-and-run jmeter-run-remote-with-properties jmeter-copy-and-run-with-properties jmeter-prep-copy-and-run jmeter-prep-copy-and-run-with-properties jmeter-fetch-artifacts-inline jmeter-verify-plan-remote jmeter-fetch-jtl-inline jmeter-build-report-local
