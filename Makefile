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

throttle-two-users: # Run two concurrent users with throttle test; params: url=..., rate1=..., rate2=..., duration=..., theory_rate=..., theory_burst=..., warmup=..., api_key1=..., api_key2=..., cert1=..., key1=..., cert2=..., key2=..., headers='K: V'..., headers2='K: V'..., params='k=v'..., params2='k=v'..., out_prefix=PATH, json=1, verbose=1 @Tests
	@if [ -z "$(url)" ]; then echo "Error: url= is required" >&2; exit 2; fi
	@echo "Launching two users in parallel against $(url)"
	@echo "User1: rate=$(or $(rate1),$(rate),1) rps, duration=$(or $(duration),30)s"
	@echo "User2: rate=$(or $(rate2),$(rate),1) rps, duration=$(or $(duration),30)s"
	@out1=$(or $(out_prefix),.)/raw-results.user1.log; \
	out2=$(or $(out_prefix),.)/raw-results.user2.log; \
	tee1=$(or $(out_prefix),.)/results.user1.log; \
	tee2=$(or $(out_prefix),.)/results.user2.log; \
	cmd1="bash scripts/tests/throttle_test.sh -u '$(url)' -X '$(or $(method),GET)' -r '$(or $(rate1),$(rate),1)' -d '$(or $(duration),30)' --theory-rate '$(or $(theory_rate),3)' --theory-burst '$(or $(theory_burst),9)' $$( [ -n '$(api_key1)' ] && printf -- "-a '%s' " '$(api_key1)') $$( [ -n '$(cert1)' ] && [ -n '$(key1)' ] && printf -- "-c '%s' -k '%s' " '$(cert1)' '$(key1)') $$( [ -n '$(ca_bundle)' ] && printf -- "-C '%s' " '$(ca_bundle)') $$( [ -n '$(max_time)' ] && printf -- "--max-time '%s' " '$(max_time)') $$( [ -n '$(connect_timeout)' ] && printf -- "--connect-timeout '%s' " '$(connect_timeout)') $$( [ -n '$(user_agent)' ] && printf -- "--user-agent '%s' " '$(user_agent)') $$( [ -n '$(warmup)' ] && printf -- "--warmup '%s' " '$(warmup)') --out-log "$$out1" --tee "$$tee1" $$( [ "$(json)" = "1" -o "$(json)" = "true" ] && printf -- "--json ") $$( [ "$(dry_run)" = "1" -o "$(dry_run)" = "true" ] && printf -- "--dry-run ") $$( [ "$(insecure)" = "1" -o "$(insecure)" = "true" ] && printf -- "-I ") $$( [ "$(verbose)" = "1" -o "$(verbose)" = "true" ] && printf -- "-v ")"; \
	for h in $(headers); do cmd1="$$cmd1 -H '$$h'"; done; \
	for p in $(params); do cmd1="$$cmd1 -p '$$p'"; done; \
	cmd2="bash scripts/tests/throttle_test.sh -u '$(url)' -X '$(or $(method),GET)' -r '$(or $(rate2),$(rate),1)' -d '$(or $(duration),30)' --theory-rate '$(or $(theory_rate),3)' --theory-burst '$(or $(theory_burst),9)' $$( [ -n '$(api_key2)' ] && printf -- "-a '%s' " '$(api_key2)') $$( [ -n '$(cert2)' ] && [ -n '$(key2)' ] && printf -- "-c '%s' -k '%s' " '$(cert2)' '$(key2)') $$( [ -n '$(ca_bundle)' ] && printf -- "-C '%s' " '$(ca_bundle)') $$( [ -n '$(max_time)' ] && printf -- "--max-time '%s' " '$(max_time)') $$( [ -n '$(connect_timeout)' ] && printf -- "--connect-timeout '%s' " '$(connect_timeout)') $$( [ -n '$(user_agent)' ] && printf -- "--user-agent '%s' " '$(user_agent)') $$( [ -n '$(warmup)' ] && printf -- "--warmup '%s' " '$(warmup)') --out-log "$$out2" --tee "$$tee2" $$( [ "$(json)" = "1" -o "$(json)" = "true" ] && printf -- "--json ") $$( [ "$(dry_run)" = "1" -o "$(dry_run)" = "true" ] && printf -- "--dry-run ") $$( [ "$(insecure)" = "1" -o "$(insecure)" = "true" ] && printf -- "-I ") $$( [ "$(verbose)" = "1" -o "$(verbose)" = "true" ] && printf -- "-v ")"; \
	for h in $(headers2); do cmd2="$$cmd2 -H '$$h'"; done; \
	for p in $(params2); do cmd2="$$cmd2 -p '$$p'"; done; \
	echo "USER1> $$cmd1"; \
	echo "USER2> $$cmd2"; \
	( eval $$cmd1 ) & \
	( eval $$cmd2 ) & \
	wait; \
	echo "Done. Logs: $$tee1, $$tee2; Raw: $$out1, $$out2"

${VERBOSE}.SILENT: \
	build \
	clean \
	config \
	dependencies \
	deploy \
	throttle-test \
	throttle-two-users \
