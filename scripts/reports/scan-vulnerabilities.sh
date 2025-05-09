#!/bin/bash

# WARNING: Please, DO NOT edit this file! It is maintained in the Repository Template (https://github.com/nhs-england-tools/repository-template). Raise a PR instead.

set -euo pipefail

# Script to scan an SBOM file for CVEs (Common Vulnerabilities and Exposures).
# This is a grype command wrapper. It will run grype natively if it is
# installed, otherwise it will run it in a Docker container.
#
# Usage:
#   $ [options] ./scan-vulnerabilities.sh
#
# Options:
#   BUILD_DATETIME=%Y-%m-%dT%H:%M:%S%z  # Build datetime, default is `date -u +'%Y-%m-%dT%H:%M:%S%z'`
#   FORCE_USE_DOCKER=true               # If set to true the command is run in a Docker container, default is 'false'
#   VERBOSE=true                        # Show all the executed commands, default is `false`
#
# Depends on:
#   $ ./create-sbom-report.sh

# ==============================================================================

function main() {

  cd "$(git rev-parse --show-toplevel)"

  create-report
  enrich-report
}

function create-report() {

  if command -v grype > /dev/null 2>&1 && ! is-arg-true "${FORCE_USE_DOCKER:-false}"; then
    run-grype-natively
  else
    run-grype-in-docker
  fi
}

function run-grype-natively() {

  grype \
    sbom:"$PWD/sbom-repository-report.json" \
    --config "$PWD/scripts/config/grype.yaml" \
    --output json \
    --file "$PWD/vulnerabilities-repository-report.tmp.json"
}

function run-grype-in-docker() {

  # shellcheck disable=SC1091
  source ./scripts/docker/docker.lib.sh
  DOCKER_CMD=$(_set_docker_cmd)
  echo run in "$DOCKER_CMD"
  # shellcheck disable=SC2155
  local image=$(name=ghcr.io/anchore/grype docker-get-image-version-and-pull)
  $DOCKER_CMD run --rm --platform linux/amd64 \
    --volume "$PWD":/workdir \
    --volume /tmp/grype/db:/.cache/grype/db \
    "$image" \
      sbom:/workdir/sbom-repository-report.json \
      --config /workdir/scripts/config/grype.yaml \
      --output json \
      --file /workdir/vulnerabilities-repository-report.tmp.json
}

function enrich-report() {

  build_datetime=${BUILD_DATETIME:-$(date -u +'%Y-%m-%dT%H:%M:%S%z')}
  git_url=$(git config --get remote.origin.url)
  git_branch=$(git rev-parse --abbrev-ref HEAD)
  git_commit_hash=$(git rev-parse HEAD)
  git_tags=$(echo \""$(git tag | tr '\n' ',' | sed 's/,$//' | sed 's/,/","/g')"\" | sed 's/""//g')
  pipeline_run_id=${GITHUB_RUN_ID:-0}
  pipeline_run_number=${GITHUB_RUN_NUMBER:-0}
  pipeline_run_attempt=${GITHUB_RUN_ATTEMPT:-0}

  # shellcheck disable=SC2086
  jq \
    '.creationInfo |= . + {"created":"'${build_datetime}'","repository":{"url":"'${git_url}'","branch":"'${git_branch}'","tags":['${git_tags}'],"commitHash":"'${git_commit_hash}'"},"pipeline":{"id":'${pipeline_run_id}',"number":'${pipeline_run_number}',"attempt":'${pipeline_run_attempt}'}}' \
    vulnerabilities-repository-report.tmp.json \
      > vulnerabilities-repository-report.json
  rm -f vulnerabilities-repository-report.tmp.json
}

# ==============================================================================

function is-arg-true() {

  if [[ "$1" =~ ^(true|yes|y|on|1|TRUE|YES|Y|ON)$ ]]; then
    return 0
  else
    return 1
  fi
}

# ==============================================================================

is-arg-true "${VERBOSE:-false}" && set -x

main "$@"

exit 0
