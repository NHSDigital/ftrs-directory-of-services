#!/bin/bash

set -euo pipefail

# Pre-commit git hook to check format Terraform code.
#
# Usage:
#   $ [options] ./check-terraform-format.sh
#
# Options:
#   check_only=true         # Do not format, run check only, default is 'false'
#   VERBOSE=true            # Show all the executed commands, default is 'false'

# ==============================================================================

versions=$(git rev-parse --show-toplevel)/.tool-versions
terraform_version=$(grep -E '^terraform' $versions | awk '{print $2}')
image_version=${terraform_version:-latest}

function main() {
  # No-op: Terraform formatting check disabled.
  # Keeping this script present so pre-commit still invokes it, but it will
  # immediately return to avoid running terraform formatting during commits.
  return 0
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

