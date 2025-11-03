# This file is for you! Edit it to implement your own hooks (make targets) into
# the project as automated steps to be executed on locally and in the CD pipeline.

include scripts/init.mk
DOCKER_CMD:=$(shell type -p docker >/dev/null 2>&1 && echo docker || echo podman)
# ==============================================================================

# Example CI/CD targets are: dependencies, build, publish, deploy, clean, etc.

dependencies: # Install dependencies needed to build and test the project @Pipeline
	# TODO: Implement installation of your project dependencies

build: # Build the project artefact @Pipeline
	# TODO: Implement the artefact build step

publish: # Publish the project artefact @Pipeline
	# TODO: Implement the artefact publishing step

deploy: # Deploy the project artefact to the target environment @Pipeline
	# TODO: Implement the artefact deployment step

clean:: # Clean-up project resources (main) @Operations
	# TODO: Implement project resources clean-up step

config:: # Configure development environment (main) @Configuration
	# TODO: Use only 'make' targets that are specific to this project, e.g. you may not need to install Node.js
	make _install-dependencies

# ==============================================================================

deps :=

throttle-test: # Run throttling test with curl (HTTP/2 + mTLS) - mandatory: url=[endpoint]; optional: api_key=..., cert=..., key=..., ca_bundle=..., insecure=true|false, headers='Key1: Val1' 'Key2: Val2', params='_revinclude=Endpoint:organization' 'identifier=odsOrganisationCode|H82028', rate=4, duration=30, theory_rate=3, theory_burst=9, method=GET, warmup=0, json=true|false, out_log=PATH, tee=PATH, user_agent=UA, dry_run=true|false, verbose=true|false, max_time=10, connect_timeout=3 @Tests
	@if [ -z "$(url)" ]; then echo "Error: url= is required" >&2; exit 2; fi
	@echo bash scripts/tests/throttle_test.sh \
		-u "$(url)" \
		-X "$(or $(method),GET)" \
		-r "$(or $(rate),4)" \
		-d "$(or $(duration),30)" \
		--theory-rate "$(or $(theory_rate),3)" \
		--theory-burst "$(or $(theory_burst),9)" \
		$(if $(api_key),-a "$(api_key)") \
		$(if $(and $(cert),$(key)),-c "$(cert)" -k "$(key)") \
		$(if $(ca_bundle),-C "$(ca_bundle)") \
		$(if $(max_time),--max-time "$(max_time)") \
		$(if $(connect_timeout),--connect-timeout "$(connect_timeout)") \
		$(if $(user_agent),--user-agent "$(user_agent)") \
		$(if $(warmup),--warmup "$(warmup)") \
		$(if $(out_log),--out-log "$(out_log)") \
		$(if $(tee),--tee "$(tee)") \
		$(if $(filter true 1,$(json)),--json) \
		$(if $(filter true 1,$(dry_run)),--dry-run) \
		$(if $(filter true 1,$(insecure)),-I) \
		$(if $(filter true 1,$(verbose)),-v) \
		$(foreach h,$(headers),-H "$(h)") \
		$(foreach p,$(params),-p "$(p)")
	@bash scripts/tests/throttle_test.sh \
		-u "$(url)" \
		-X "$(or $(method),GET)" \
		-r "$(or $(rate),4)" \
		-d "$(or $(duration),30)" \
		--theory-rate "$(or $(theory_rate),3)" \
		--theory-burst "$(or $(theory_burst),9)" \
		$(if $(api_key),-a "$(api_key)") \
		$(if $(and $(cert),$(key)),-c "$(cert)" -k "$(key)") \
		$(if $(ca_bundle),-C "$(ca_bundle)") \
		$(if $(max_time),--max-time "$(max_time)") \
		$(if $(connect_timeout),--connect-timeout "$(connect_timeout)") \
		$(if $(user_agent),--user-agent "$(user_agent)") \
		$(if $(warmup),--warmup "$(warmup)") \
		$(if $(out_log),--out-log "$(out_log)") \
		$(if $(tee),--tee "$(tee)") \
		$(if $(filter true 1,$(json)),--json) \
		$(if $(filter true 1,$(dry_run)),--dry-run) \
		$(if $(filter true 1,$(insecure)),-I) \
		$(if $(filter true 1,$(verbose)),-v) \
		$(foreach h,$(headers),-H "$(h)") \
		$(foreach p,$(params),-p "$(p)")

${VERBOSE}.SILENT: \
	build \
	clean \
	config \
	dependencies \
	deploy \
	throttle-test \
