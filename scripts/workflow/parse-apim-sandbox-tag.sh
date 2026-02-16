#!/usr/bin/env bash

set -euo pipefail

TAG="${GITHUB_REF_NAME:-}"
WORKSPACE_ROOT="${GITHUB_WORKSPACE:-}" || true

ALLOWED_ENVS=(sandbox internal-dev-sandbox)
ALLOWED_SERVICES=(dos-search)

sandbox_environment="sandbox"
service="dos-search"
version=""
should_deploy="false"

join_with_pipe() {
  local IFS='|'
  printf '%s' "$*"
  return 0
}

info() {
  printf '[parse-apim-sandbox-tag] %s\n' "$*"
  return 0
}

write_step_summary() {
  if [[ -n "${GITHUB_STEP_SUMMARY:-}" ]]; then
    printf '%s' "$1" >> "$GITHUB_STEP_SUMMARY"
  fi
  return 0
}

write_outputs() {
  printf 'sandbox_environment=%s\nservice=%s\nversion=%s\nshould_deploy=%s\n' "$1" "$2" "$3" "$4" > "$GITHUB_OUTPUT"
  return 0
}

fetch_remote_heads() {
  git fetch --no-tags origin "+refs/heads/*:refs/remotes/origin/*" --quiet || true
  return 0
}

resolve_main_ref() {
  git rev-parse --verify origin/main 2>/dev/null || return 1
}

resolve_tag_commit() {
  if git rev-parse --verify "refs/tags/${TAG}^{commit}" >/dev/null 2>&1; then
    git rev-parse --verify "refs/tags/${TAG}^{commit}"
  elif [[ -n "${GITHUB_SHA:-}" ]]; then
    printf '%s' "${GITHUB_SHA}"
  else
    return 1
  fi
}

ensure_tag_on_main() {
  local tag_commit="$1"
  local main_ref="$2"
  if git merge-base --is-ancestor "${tag_commit}" "${main_ref}" >/dev/null 2>&1; then
    return 0
  fi
  return 1
}

is_allowed() {
  local needle="$1"; shift
  for candidate in "$@"; do
    [[ "$needle" == "$candidate" ]] && return 0
  done
  return 1
}

fail_and_exit() {
  local reason="$1"
  info "$reason"
  echo "Parse result: sandbox_environment=${sandbox_environment} service=${service} version=${version} should_deploy=${should_deploy}"
  write_step_summary "## Parse result\n\n- Reason: ${reason}\n- Deployment: Skipped\n\n"
  echo "### Deployment decision: Skipping deploy"
  sandbox_environment=""
  service=""
  version=""
  should_deploy="false"
  write_outputs "" "" "" "false"
  exit 0
}

print_and_write_success() {
  echo "Parse result: sandbox_environment=${sandbox_environment} service=${service} version=${version} should_deploy=${should_deploy}"
  write_step_summary "## Parse result\n\n- sandbox_environment: ${sandbox_environment}\n- service: ${service}\n- version: ${version}\n- should_deploy: ${should_deploy}\n\n### Deployment decision: Proceeding with deploy\n"
  echo "### Deployment decision: Proceeding with deploy"
  write_outputs "${sandbox_environment}" "${service}" "${version}" "${should_deploy}"
  return 0
}

parse_tag_format() {
  local tag="$1"
  local env_regex
  local service_regex
  env_regex="$(join_with_pipe "${ALLOWED_ENVS[@]}")"
  service_regex="$(join_with_pipe "${ALLOWED_SERVICES[@]}")"
  if [[ "$tag" =~ ^(${env_regex})-(${service_regex})-([0-9]+\.[0-9]+\.[0-9]+)$ ]]; then
    env_prefix="${BASH_REMATCH[1]}"
    service="${BASH_REMATCH[2]}"
    version="${BASH_REMATCH[3]}"
    if ! is_allowed "${env_prefix}" "${ALLOWED_ENVS[@]}"; then
      fail_and_exit "Invalid environment prefix '${env_prefix}'"
    fi
    if ! is_allowed "${service}" "${ALLOWED_SERVICES[@]}"; then
      fail_and_exit "Invalid service '${service}'"
    fi
    sandbox_environment="${env_prefix}"
    should_deploy="true"
    info "Parsed env=${sandbox_environment}, service=${service}, version=${version}"
    return 0
  fi
  return 1
}

main() {
  info "Evaluating tag '${TAG}'"
  if [[ -z "${TAG}" ]]; then
    fail_and_exit "No tag ref detected; skipping sandbox deploy"
  fi
  fetch_remote_heads
  main_ref=$(resolve_main_ref) || fail_and_exit "origin/main not found after fetch; skipping"
  TAG_COMMIT=$(resolve_tag_commit) || fail_and_exit "Could not resolve tag commit for '${TAG}'"
  if ! ensure_tag_on_main "${TAG_COMMIT}" "${main_ref}"; then
    fail_and_exit "Tag commit not on main; skipping"
  fi
  if ! parse_tag_format "${TAG}"; then
    fail_and_exit "Tag '${TAG}' does not match <environment>-<service>-<version>"
  fi
  print_and_write_success
}

main
