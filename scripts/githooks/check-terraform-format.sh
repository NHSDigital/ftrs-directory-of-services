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

  # Run Terraform fmt in a Docker container
  docker run --rm --platform linux/amd64 \
    --volume=$PWD:/workdir \
    hashicorp/terraform:$image_version \
    fmt -recursive $opts
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
