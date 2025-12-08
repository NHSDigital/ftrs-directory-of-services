#!/usr/bin/env bash

set -euo pipefail

TAG="${GITHUB_REF_NAME:-}"
WORKSPACE_ROOT="${GITHUB_WORKSPACE:-}" || true

ALLOWED_ENVS=(sandbox internal-sandbox)
ALLOWED_SERVICES=(dos-search)

sandbox_environment="sandbox"
service="dos-search"
version=""
should_deploy="false"

join_with_pipe() {
  local IFS='|'
  printf '%s' "$*"
}

info() {
  printf '[parse-apim-sandbox-tag] %s\n' "$*"
}

fail_and_exit() {
  info "$1"
  echo "sandbox_environment=${sandbox_environment}" >> "$GITHUB_OUTPUT"
  echo "service=${service}" >> "$GITHUB_OUTPUT"
  echo "version=${version}" >> "$GITHUB_OUTPUT"
  echo "should_deploy=false" >> "$GITHUB_OUTPUT"
  exit 0
}

info "Evaluating tag '${TAG}'"

if [[ -z "${TAG}" ]]; then
  fail_and_exit "No tag ref detected; skipping sandbox deploy"
fi

if ! git fetch --prune --no-tags origin main >/dev/null 2>&1; then
  fail_and_exit "Unable to fetch origin/main; skipping"
fi

main_ref=$(git rev-parse --verify origin/main 2>/dev/null) || fail_and_exit "origin/main not found after fetch; skipping"

if ! git merge-base --is-ancestor "$main_ref" "${GITHUB_SHA}"; then
  fail_and_exit "Tag commit not on main; skipping"
fi

is_allowed() {
  local needle="$1"; shift
  for candidate in "$@"; do
    [[ "$needle" == "$candidate" ]] && return 0
  done
  return 1
}

env_regex="$(join_with_pipe "${ALLOWED_ENVS[@]}")"
service_regex="$(join_with_pipe "${ALLOWED_SERVICES[@]}")"

if [[ "${TAG}" =~ ^(${env_regex})-(${service_regex})-([0-9]+\.[0-9]+\.[0-9]+)$ ]]; then
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
else
  fail_and_exit "Tag '${TAG}' does not match <environment>-<service>-<version>"
fi

echo "sandbox_environment=${sandbox_environment}" >> "$GITHUB_OUTPUT"
echo "service=${service}" >> "$GITHUB_OUTPUT"
echo "version=${version}" >> "$GITHUB_OUTPUT"
echo "should_deploy=${should_deploy}" >> "$GITHUB_OUTPUT"
