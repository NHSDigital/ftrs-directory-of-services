#!/bin/bash

# WARNING: Please DO NOT edit this file! It is maintained in the Repository Template (https://github.com/nhs-england-tools/repository-template). Raise a PR instead.

set -euo pipefail

# Terraform command wrapper. It will run the command natively if Terraform is
# installed, otherwise it will run it in a Docker container.
#
# Usage:
#   $ [options] ./terraform.sh
#
# Options:
#   cmd=command             # Terraform command to execute
#   FORCE_USE_DOCKER=true   # If set to true the command is run in a Docker container, default is 'false'
#   VERBOSE=true            # Show all the executed commands, default is 'false'

# ==============================================================================

function main() {

  cd "$(git rev-parse --show-toplevel)"

  if command -v terraform > /dev/null 2>&1 && ! is-arg-true "${FORCE_USE_DOCKER:-false}"; then
    # shellcheck disable=SC2154
    cmd=$cmd run-terraform-natively
  else
    cmd=$cmd run-terraform-in-docker
  fi
}

# Run Terraform natively.
# Arguments (provided as environment variables):
#   cmd=[Terraform command to execute]
function run-terraform-natively() {

  # shellcheck disable=SC2086
  terraform $cmd
}

# Run Terraform in a Docker container.
# Arguments (provided as environment variables):
#   cmd=[Terraform command to execute]
function run-terraform-in-docker() {

  # shellcheck disable=SC1091
  source ./scripts/docker/docker.lib.sh
  DOCKER_CMD=$(_set_docker_cmd)
  echo run in "$DOCKER_CMD"
  # shellcheck disable=SC2155
  local image=$(name=hashicorp/terraform docker-get-image-version-and-pull)
  # shellcheck disable=SC2086
  $DOCKER_CMD run --rm --platform linux/amd64 \
    --volume "$PWD":/workdir \
    --workdir /workdir \
    "$image" \
      $cmd
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
