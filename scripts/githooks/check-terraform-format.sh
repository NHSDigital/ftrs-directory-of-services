#!/bin/bash

# WARNING: Please DO NOT edit this file! It is maintained in the Repository Template (https://github.com/nhs-england-tools/repository-template). Raise a PR instead.

set -euo pipefail

# Pre-commit git hook to check format Terraform code.
#
# Usage:
#   $ [options] ./check-terraform-format.sh
#
# Options:
#   check_only=true         # Do not format, run check only, default is 'false'
#   FORCE_USE_DOCKER=true   # If set to true the command is run in a Docker container, default is 'false'
#   VERBOSE=true            # Show all the executed commands, default is 'false'

# ==============================================================================

function main() {

  cd "$(git rev-parse --show-toplevel)"

  local check_only=${check_only:-false}
  check_only=$check_only terraform-fmt
}

# Format Terraform files.
# Arguments (provided as environment variables):
#   check_only=[do not format, run check only]
function terraform-fmt() {

  local opts=
  if is-arg-true "$check_only"; then
    opts="-check"
  fi
  opts=$opts dir=infrastructure make terraform-fmt
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
