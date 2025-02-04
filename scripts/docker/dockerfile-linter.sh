#!/bin/bash

# WARNING: Please DO NOT edit this file! It is maintained in the Repository Template (https://github.com/nhs-england-tools/repository-template). Raise a PR instead.

set -euo pipefail

# Hadolint command wrapper. It will run hadolint natively if it is installed,
# otherwise it will run it in a Docker container.
#
# Usage:
#   $ [options] ./dockerfile-linter.sh
#
# Arguments (provided as environment variables):
#   file=Dockerfile         # Path to the Dockerfile to lint, relative to the project's top-level directory, default is './Dockerfile.effective'
#   FORCE_USE_DOCKER=true   # If set to true the command is run in a Docker container, default is 'false'
#   VERBOSE=true            # Show all the executed commands, default is 'false'

# ==============================================================================

function main() {

  cd "$(git rev-parse --show-toplevel)"

  local file=${file:-./Dockerfile.effective}
  if command -v hadolint > /dev/null 2>&1 && ! is-arg-true "${FORCE_USE_DOCKER:-false}"; then
    file="$file" run-hadolint-natively
  else
    file="$file" run-hadolint-in-docker
  fi
}

# Run hadolint natively.
# Arguments (provided as environment variables):
#   file=[path to the Dockerfile to lint, relative to the project's top-level directory]
function run-hadolint-natively() {

  # shellcheck disable=SC2001
  hadolint "$(echo "$file" | sed "s#$PWD#.#")"
}

# Run hadolint in a Docker container.
# Arguments (provided as environment variables):
#   file=[path to the Dockerfile to lint, relative to the project's top-level directory]
function run-hadolint-in-docker() {

  # shellcheck disable=SC1091
  source ./scripts/docker/docker.lib.sh
  DOCKER_CMD=$(_set_docker_cmd)
  echo run in "$DOCKER_CMD"
  # shellcheck disable=SC2155
  local image=$(name=hadolint/hadolint docker-get-image-version-and-pull)
  # shellcheck disable=SC2001
  $DOCKER_CMD run --rm --platform linux/amd64 \
    --volume "$PWD:/workdir" \
    --workdir /workdir \
    "$image" \
      hadolint \
        --config /workdir/scripts/config/hadolint.yaml \
        "/workdir/$(echo "$file" | sed "s#$PWD#.#")"
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
