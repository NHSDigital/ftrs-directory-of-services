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
branch_glob="${SANDBOX_BRANCH_GLOB:-task/*}"

join_with_pipe() {
  local IFS='|'
  printf '%s' "$*"
}

info() {
  printf '[parse-apim-sandbox-tag] %s\n' "$*"
}

fail_and_exit() {
  info "$1"
  echo "Parse result: sandbox_environment= service= version= should_deploy=false"

  if [[ -n "${GITHUB_STEP_SUMMARY:-}" ]]; then
    {
      echo "## Parse result"
      echo ""
      echo "- Reason: $1"
      echo "- Deployment: Skipped"
      echo ""
    } >> "$GITHUB_STEP_SUMMARY"
  fi

  {
    echo "sandbox_environment="
    echo "service="
    echo "version="
    echo "should_deploy=false"
  } >> "$GITHUB_OUTPUT"

  exit 0
}

ensure_commit_on_branch() {
  local glob="$1"
  git fetch origin --depth=1 --quiet || true

  local candidates=()
  while IFS= read -r ref_name; do
    candidates+=("$ref_name")
  done < <(git for-each-ref --format='%(refname:short)' "refs/remotes/origin/${glob}")

  if (( ${#candidates[@]} == 0 )); then
    fail_and_exit "No origin branches match '${glob}'; skipping"
  fi

  for remote_ref in "${candidates[@]}"; do
    # Correct check: is the tag commit an ancestor of the remote branch tip?
    if git merge-base --is-ancestor "${GITHUB_SHA}" "${remote_ref}" >/dev/null 2>&1; then
      info "Tag commit verified on branch '${remote_ref}'"
      return 0
    fi
  done

  fail_and_exit "Tag commit not on any branch matching '${glob}'; skipping"
}

info "Evaluating tag '${TAG}'"

if [[ -z "${TAG}" ]]; then
  fail_and_exit "No tag ref detected; skipping sandbox deploy"
fi

if [[ "${GITHUB_REF_TYPE:-}" != "tag" ]]; then
  fail_and_exit "Ref type '${GITHUB_REF_TYPE:-}' is not tag; skipping"
fi

ensure_commit_on_branch "${branch_glob}"

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

echo "Parse result: sandbox_environment=${sandbox_environment} service=${service} version=${version} should_deploy=${should_deploy}"

if [[ -n "${GITHUB_STEP_SUMMARY:-}" ]]; then
  {
    echo "## Parse result"
    echo ""
    echo "- sandbox_environment: ${sandbox_environment}"
    echo "- service: ${service}"
    echo "- version: ${version}"
    echo "- should_deploy: ${should_deploy}"
    if [[ "${should_deploy}" == "true" ]]; then
      echo ""
      echo "### Deployment decision: Proceeding with deploy"
    else
      echo ""
      echo "### Deployment decision: Skipping deploy"
    fi
  } >> "$GITHUB_STEP_SUMMARY"
fi

echo "sandbox_environment=${sandbox_environment}" >> "$GITHUB_OUTPUT"
echo "service=${service}" >> "$GITHUB_OUTPUT"
echo "version=${version}" >> "$GITHUB_OUTPUT"
echo "should_deploy=${should_deploy}" >> "$GITHUB_OUTPUT"
