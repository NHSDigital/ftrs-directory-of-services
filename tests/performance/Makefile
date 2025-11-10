PROJECT_NAME := ftrs-dos
ENVIRONMENT ?= dev
SERVICE ?= is-performance
PYTHON_VERSION ?= 3.12
LOCAL_DIR := parameter_files
WORKSPACE_FILES_BUCKET := ${PROJECT_NAME}-${ENVIRONMENT}-${SERVICE}-parameter-files-bucket-${WORKSPACE}
MAIN_FILES_BUCKET := ${PROJECT_NAME}-${ENVIRONMENT}-${SERVICE}-parameter-files-bucket
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

download-performance-files: ##[AWS_REGION=aws region] [MAIN_FILES_BUCKET=main bucket for performance files]  [LOCAL_DIR=local folder]
	echo "downloading performance test files from  ${MAIN_FILES_BUCKET}"
	aws s3 cp s3://${MAIN_FILES_BUCKET} --region $(AWS_REGION) ${LOCAL_DIR}/ --recursive

upload-performance-file: ##[AWS_REGION=aws region] [WORKSPACE=workspace name +/] [MAIN_FILES_BUCKET=main bucket for performance files]
## [FILE=file] [FILE_PATH=./local/path/to/file/]
	echo "Uploading performance test file ${FILE_PATH}${FILE} to s3://${MAIN_FILES_BUCKET}/${WORKSPACE}"
	aws s3 cp --region $(AWS_REGION) ${FILE_PATH}${FILE} s3://${MAIN_FILES_BUCKET}/${WORKSPACE}${FILE}

upload-performance-folder: ##[AWS_REGION=aws region] [WORKSPACE=workspace name] [MAIN_FILES_BUCKET=main bucket for performance files] [LOCAL_DIR=local folder]
	echo "Uploading performance test files from ${LOCAL_DIR} to s3://${MAIN_FILES_BUCKET}/${WORKSPACE}"
	aws s3 cp --region $(AWS_REGION) ${LOCAL_DIR} s3://${MAIN_FILES_BUCKET}/${WORKSPACE}${LOCAL_DIR} --recursive

# Get a secret value from Secrets Manager
secrets-get: ## [SECRET_ID=arn or name] [OUT=name of file to store secret]
	aws secretsmanager get-secret-value --region  $(AWS_REGION) --secret-id $(SECRET_ID) --query 'SecretString' --output text > $(OUT)


_install-dependency: # Install asdf dependency - mandatory: name=[listed in the '.tool-versions' file]; optional: version=[if not listed]
	echo ${name}
	asdf plugin add ${name} ||:
	asdf plugin update ${name} ||:
	asdf install ${name} $(or ${version},)

_install-dependencies: # Install all the dependencies listed in .tool-versions
	for plugin in $$(grep ^[a-z] .tool-versions | sed 's/[[:space:]].*//'); do \
		make _install-dependency name="$${plugin}"; \
	done


# ---------------------------------------------------------------------------------------------------------------------------------------------------
# EC2 Make Targets
# ---------------------------------------------------------------------------------------------------------------------------------------------------

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

jmeter-version-remote: ## [JMETER_INSTANCE_ID=i-xxxxxxxxxxxxxxxxx] Print JMeter version number from /home/ssm-user on the EC2 using SSM
	@ID="$(JMETER_INSTANCE_ID)"; \
	if [ -z "$$ID" ]; then echo "JMETER_INSTANCE_ID is required"; exit 1; fi; \
	aws ssm start-session --region $(AWS_REGION) --target "$$ID" --document-name AWS-StartInteractiveCommand --parameters 'command=["bash -lc \"cd /home/ssm-user && echo && echo '\''jmeter\\ version'\'' &&  echo '\''--------------'\'' && jmeter -v 2>&1 | grep -Eo '\''[0-9]+(\\.[0-9]+)+'\'' | tail -n1\""]'

jmeter-ssm-shell: ## [JMETER_INSTANCE_ID=i-xxxxxxxxxxxxxxxxx] Open an interactive SSM shell to the JMeter EC2 instance
	@ID="$(JMETER_INSTANCE_ID)"; \
	if [ -z "$$ID" ]; then echo "JMETER_INSTANCE_ID is required"; exit 1; fi; \
	aws ssm start-session --region $(AWS_REGION) --target "$$ID"

jmeter-copy-ssm-inline: ## [JMETER_INSTANCE_ID=i-xxxxxxxxxxxxxxxxx] [FILE=jmeter_test_plan.jmx] [DEST=jmeter_test_plan.jmx]
	@ID="$(JMETER_INSTANCE_ID)"; \
	if [ -z "$$ID" ]; then echo "JMETER_INSTANCE_ID is required"; exit 1; fi; \
	FILE="${FILE}"; if [ -z "$$FILE" ]; then FILE=jmeter_test_plan.jmx; fi; \
	DEST="${DEST}"; if [ -z "$$DEST" ]; then DEST=$$(basename "$$FILE"); fi; \
	if [ ! -f "$$FILE" ]; then ALT="tests/performance/$$(basename "$$FILE")"; if [ -f "$$ALT" ]; then FILE="$$ALT"; else echo "File '$$FILE' not found"; exit 1; fi; fi; \
	B64=$$(base64 < "$$FILE" | tr -d '\n'); \
	echo "Uploading '$$FILE' to EC2:/home/ssm-user/$$DEST via SSM inline"; \
	PARAMS_FILE=$$(mktemp); \
	printf '%s\n' '{' '  "commands": [' '    "bash -lc \"printf %s '\''__B64__'\'' | base64 -d > /home/ssm-user/__DEST__ && chown ssm-user:ssm-user /home/ssm-user/__DEST__ && ls -l /home/ssm-user/__DEST__\""' '  ]' '}' > "$$PARAMS_FILE"; \
	B64_ESC=$$(printf '%s' "$$B64" | sed -e 's/[&|]/\\\&/g'); \
	DEST_ESC=$$(printf '%s' "$$DEST" | sed -e 's/[&|]/\\\&/g'); \
	sed -i.bak -e "s|__B64__|$$B64_ESC|g" -e "s|__DEST__|$$DEST_ESC|g" "$$PARAMS_FILE"; rm -f "$$PARAMS_FILE.bak"; \
	CMD_ID=$$(aws ssm send-command --region $(AWS_REGION) --instance-ids "$$ID" \
		--document-name AWS-RunShellScript \
		--parameters file://$$PARAMS_FILE \
		--query 'Command.CommandId' --output text); \
	rm -f "$$PARAMS_FILE"; \
	if [ -z "$$CMD_ID" ] || [ "$$CMD_ID" = "None" ]; then echo "SSM send-command failed"; exit 1; fi; \
	if ! aws ssm wait command-executed --region $(AWS_REGION) --instance-id "$$ID" --command-id "$$CMD_ID"; then \
		echo "SSM command execution failed; fetching invocation logs..."; \
		aws ssm get-command-invocation --region $(AWS_REGION) --command-id "$$CMD_ID" --instance-id "$$ID" --output text \
			--query '[Status,StandardOutputContent,StandardErrorContent]' || true; \
		exit 1; \
	fi; \
	echo "File uploaded to /home/ssm-user/$${DEST}"

jmeter-copy-dir-ssm-inline: ## [JMETER_INSTANCE_ID=i-xxxxxxxxxxxxxxxxx] [DIR=parameter_files] [DEST_DIR=] Copy all regular files in DIR to EC2 under /home/ssm-user[/DEST_DIR] using the same inline logic as jmeter-copy-ssm-inline
	@ID="$(JMETER_INSTANCE_ID)"; \
	if [ -z "$$ID" ]; then echo "JMETER_INSTANCE_ID is required"; exit 1; fi; \
	DIR="${DIR}"; if [ -z "$$DIR" ]; then DIR=parameter_files; fi; \
	DIR=$${DIR%/}; \
	if [ ! -d "$$DIR" ]; then ALT="tests/performance/$$(basename "$$DIR")"; if [ -d "$$ALT" ]; then DIR="$$ALT"; else echo "Directory '$$DIR' not found"; exit 1; fi; fi; \
	DEST_DIR="${DEST_DIR}"; \
	for FILE in "$$DIR"/*; do \
		[ -e "$$FILE" ] || continue; \
		if [ ! -f "$$FILE" ]; then continue; fi; \
		DEST=$$(basename "$$FILE"); \
		if [ -n "$$DEST_DIR" ] && [ "$$DEST_DIR" != "." ]; then DEST_PATH="/home/ssm-user/$${DEST_DIR}/$${DEST}"; else DEST_PATH="/home/ssm-user/$${DEST}"; fi; \
		B64=$$(base64 < "$$FILE" | tr -d '\n'); \
		echo "Uploading '$$FILE' to EC2:$$DEST_PATH via SSM inline"; \
		PARAMS_FILE=$$(mktemp); \
		printf '%s\n' '{' '  "commands": [' \
			"    \"bash -lc \\\"set -euo pipefail; DEST_DIR=__DEST_DIR__; DEST_PATH=__DEST_PATH__; if [ -n \\\"$$DEST_DIR\\\" ] && [ \\\"$$DEST_DIR\\\" != \\\".\\\" ]; then install -d -m 0755 -o ssm-user -g ssm-user /home/ssm-user/\\\"$$DEST_DIR\\\"; fi; printf %s __B64__ | base64 -d > \\\"$$DEST_PATH\\\" && chown ssm-user:ssm-user \\\"$$DEST_PATH\\\"; ls -l \\\"$$DEST_PATH\\\"\\\"\"" \
			'  ]' '}' > "$$PARAMS_FILE"; \
		B64_ESC=$$(printf '%s' "$$B64" | sed -e 's/[&|]/\\\&/g'); \
		DEST_DIR_ESC=$$(printf '%s' "$$DEST_DIR" | sed -e 's/[&|]/\\\&/g'); \
		DEST_PATH_ESC=$$(printf '%s' "$$DEST_PATH" | sed -e 's/[&|]/\\\&/g'); \
		sed -i.bak \
			-e "s|__B64__|$$B64_ESC|g" \
			-e "s|__DEST_DIR__|$$DEST_DIR_ESC|g" \
			-e "s|__DEST_PATH__|$$DEST_PATH_ESC|g" \
			"$$PARAMS_FILE"; rm -f "$$PARAMS_FILE.bak"; \
		CMD_ID=$$(aws ssm send-command --region $(AWS_REGION) --instance-ids "$$ID" \
			--document-name AWS-RunShellScript \
			--parameters file://$$PARAMS_FILE \
			--query 'Command.CommandId' --output text); \
		rm -f "$$PARAMS_FILE"; \
		if [ -z "$$CMD_ID" ] || [ "$$CMD_ID" = "None" ]; then echo "SSM send-command failed"; exit 1; fi; \
		if ! aws ssm wait command-executed --region $(AWS_REGION) --instance-id "$$ID" --command-id "$$CMD_ID"; then \
			echo "SSM command execution failed; fetching invocation logs..."; \
			aws ssm get-command-invocation --region $(AWS_REGION) --command-id "$$CMD_ID" --instance-id "$$ID" --output text \
				--query '[Status,StandardOutputContent,StandardErrorContent]' || true; \
			exit 1; \
		fi; \
		echo "Uploaded $$DEST_PATH"; \
	done

# Fetch any single file via SSM
jmeter-fetch-file-inline: ## [REMOTE_FILE=result.jtl] [LOCAL_DIR=tests/performance/artifacts] [LOCAL_FILE=<optional>] Fetch any single file via SSM into LOCAL_DIR or to LOCAL_FILE
	@set -euo pipefail; \
	ID="$(JMETER_INSTANCE_ID)"; \
	if [ -z "$$ID" ]; then echo "JMETER_INSTANCE_ID is required"; exit 1; fi; \
	REM="${REMOTE_FILE}"; if [ -z "$$REM" ]; then REM=result.jtl; fi; \
	case "$$REM" in /*) RPATH="$$REM" ;; *) RPATH="/home/ssm-user/$$REM" ;; esac; \
	LFILE="${LOCAL_FILE}"; \
	if [ -n "$$LFILE" ]; then OUTFILE="$$LFILE"; mkdir -p "$$(dirname "$$OUTFILE")"; else \
		ROOT_DIR=$$(git rev-parse --show-toplevel 2>/dev/null || pwd); \
		LDIR="${LOCAL_DIR}"; if [ -z "$$LDIR" ]; then LDIR="$$ROOT_DIR/tests/performance/artifacts"; fi; mkdir -p "$$LDIR"; OUTFILE="$$LDIR/$$(basename "$$RPATH")"; \
	fi; \
	TMPDIR=$$(mktemp -d); B64FILE="$$TMPDIR/file.inline.b64"; \
	echo "Fetching '$$RPATH' via SSM"; \
	RCMD="set -o pipefail; echo __B64_START__; if [ -f \"$$RPATH\" ]; then base64 \"$$RPATH\"; else echo __NO_RESULT__; fi; echo __B64_END__"; \
	PARAMS_FILE="$$TMPDIR/params.json"; \
	ESC_RCMD=$$(printf '%s' "$$RCMD" | sed -e 's/\\/\\\\/g' -e 's/\"/\\\"/g'); \
	printf '%s' '{"command":["bash -lc \"'"$$ESC_RCMD"'\""]}' > "$$PARAMS_FILE"; \
	aws ssm start-session --region $(AWS_REGION) --target "$$ID" \
		--document-name AWS-StartInteractiveCommand \
		--parameters file://"$$PARAMS_FILE" \
		| awk '/__B64_START__/{flag=1;next}/__B64_END__/{flag=0}flag' > "$$B64FILE"; \
	if grep -q "__NO_RESULT__" "$$B64FILE"; then echo "Remote file not found: $$RPATH"; rm -rf "$$TMPDIR"; exit 1; fi; \
	if base64 --decode < "$$B64FILE" > "$$OUTFILE" 2>/dev/null; then :; \
	elif base64 -d < "$$B64FILE" > "$$OUTFILE" 2>/dev/null; then :; \
	elif base64 -D < "$$B64FILE" > "$$OUTFILE" 2>/dev/null; then :; \
	else echo "Failed to decode base64 for '$$RPATH'"; rm -rf "$$TMPDIR"; exit 1; fi; \
	ls -lh "$$OUTFILE" || ls -l "$$OUTFILE"; \
	rm -rf "$$TMPDIR"; \
	echo "Downloaded '$$RPATH' to '$$OUTFILE'"

jmeter-fetch-dir-inline: ## [REMOTE_DIR=artifacts] [LOCAL_DIR=tests/performance/artifacts] Fetch all regular files from REMOTE_DIR into LOCAL_DIR using SSM (indexed loop)
	@set -euo pipefail; \
	ID="$(JMETER_INSTANCE_ID)"; \
	if [ -z "$$ID" ]; then echo "JMETER_INSTANCE_ID is required"; exit 1; fi; \
	REMOTE_DIR="${REMOTE_DIR}"; if [ -z "$$REMOTE_DIR" ]; then REMOTE_DIR=artifacts; fi; \
	case "$$REMOTE_DIR" in /*) RDIR="$$REMOTE_DIR" ;; *) RDIR="/home/ssm-user/$$REMOTE_DIR" ;; esac; \
	LDIR="${LOCAL_DIR}"; if [ -z "$$LDIR" ]; then ROOT_DIR=$$(git rev-parse --show-toplevel 2>/dev/null || pwd); LDIR="$$ROOT_DIR/tests/performance/artifacts"; fi; mkdir -p "$$LDIR"; \
	WORKDIR=$$(mktemp -d); [ -n "$$WORKDIR" ] || { echo "mktemp failed"; exit 1; }; \
	PARAMS="$$WORKDIR/params.list.json"; OUT="$$WORKDIR/files.list"; B64TMP="$$WORKDIR/file.b64"; \
	echo "Listing files in remote directory: $$RDIR"; \
	LIST_CMD=$$(printf '%s' "if [ -d \"$$RDIR\" ]; then find \"$$RDIR\" -maxdepth 1 -type f -printf '%f\\n' | sort; else echo __NO_DIR__; fi"); \
	ESC_LIST_CMD=$$(printf '%s' "$$LIST_CMD" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g'); \
	printf '%s' '{"commands":["bash -lc \"'"$$ESC_LIST_CMD"'\""]}' > "$$PARAMS"; \
	CMD_ID=$$(aws ssm send-command --region $(AWS_REGION) --instance-ids "$$ID" --document-name AWS-RunShellScript --parameters file://"$$PARAMS" --query 'Command.CommandId' --output text); \
	rm -f "$$PARAMS"; \
	if [ -z "$$CMD_ID" ] || [ "$$CMD_ID" = "None" ]; then echo "SSM send-command failed for listing"; rm -rf "$$WORKDIR"; exit 1; fi; \
	aws ssm wait command-executed --region $(AWS_REGION) --instance-id "$$ID" --command-id "$$CMD_ID"; \
	aws ssm get-command-invocation --region $(AWS_REGION) --instance-id "$$ID" --command-id "$$CMD_ID" --query 'StandardOutputContent' --output text > "$$OUT" || true; \
	if grep -q "__NO_DIR__" "$$OUT" 2>/dev/null; then echo "No remote directory: $$RDIR"; rm -rf "$$WORKDIR"; exit 0; fi; \
	if [ ! -s "$$OUT" ]; then echo "No files found in remote directory: $$RDIR"; rm -rf "$$WORKDIR"; exit 0; fi; \
	CLEAN="$$WORKDIR/files.clean"; \
	tr -d '\r' < "$$OUT" \
		| awk '{gsub(/^[[:space:]]+|[[:space:]]+$$/, ""); if ($$0 ~ /[[:graph:]]/) print $$0}' > "$$CLEAN"; \
	COUNT=$$(wc -l < "$$CLEAN" | tr -d '[:space:]'); \
	echo "Total files: $$COUNT"; \
	FETCHED=0; i=1; \
	while [ "$$i" -le "$$COUNT" ]; do \
		F=$$(sed -n "$${i}p" "$$CLEAN" | tr -d '\r\n'); \
		if [ -z "$$F" ]; then i=$$((i+1)); continue; fi; \
		RPATH="$$RDIR/$$F"; OUTFILE="$$LDIR/$$F"; TMPP=$$(mktemp); [ -n "$$TMPP" ] || { echo "mktemp failed for file $$F"; rm -rf "$$WORKDIR"; exit 1; }; \
		echo "[$$i/$$COUNT] Fetching: $$RPATH -> $$OUTFILE"; \
		FETCH_CMD=$$(printf '%s' "if [ -f \"$$RPATH\" ]; then base64 \"$$RPATH\"; else echo __NO_RESULT__; fi"); \
		ESC_FETCH_CMD=$$(printf '%s' "$$FETCH_CMD" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g'); \
		printf '%s' '{"commands":["bash -lc \"'"$$ESC_FETCH_CMD"'\""]}' > "$$TMPP"; \
		CMD_ID=$$(aws ssm send-command --region $(AWS_REGION) --instance-ids "$$ID" --document-name AWS-RunShellScript --parameters file://"$$TMPP" --query 'Command.CommandId' --output text); \
		rm -f "$$TMPP"; \
		if [ -z "$$CMD_ID" ] || [ "$$CMD_ID" = "None" ]; then echo "SSM send-command failed for $$RPATH"; rm -rf "$$WORKDIR"; exit 1; fi; \
		aws ssm wait command-executed --region $(AWS_REGION) --instance-id "$$ID" --command-id "$$CMD_ID"; \
		aws ssm get-command-invocation --region $(AWS_REGION) --instance-id "$$ID" --command-id "$$CMD_ID" --query 'StandardOutputContent' --output text > "$$B64TMP" || true; \
		if grep -q "__NO_RESULT__" "$$B64TMP"; then echo "Remote file not found: $$RPATH"; rm -rf "$$WORKDIR"; exit 1; fi; \
		if base64 --decode < "$$B64TMP" > "$$OUTFILE" 2>/dev/null; then :; \
		elif base64 -d < "$$B64TMP" > "$$OUTFILE" 2>/dev/null; then :; \
		elif base64 -D < "$$B64TMP" > "$$OUTFILE" 2>/dev/null; then :; \
		else echo "Failed to decode base64 for '$$RPATH'"; rm -rf "$$WORKDIR"; exit 1; fi; \
		ls -lh "$$OUTFILE" || ls -l "$$OUTFILE"; \
		FETCHED=$$((FETCHED+1)); \
		i=$$((i+1)); \
	done; \
	rm -rf "$$WORKDIR"; \
	echo "Downloaded $$FETCHED files from '$$RDIR' to '$$LDIR' (listed $$COUNT)"

.PHONY: s3-upload-file s3-upload-folder s3-download-file s3-download-folder secrets-get secrets-get-value
