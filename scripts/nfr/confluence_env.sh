#!/usr/bin/env zsh
#
# Confluence/Jira environment (non-secrets)
#
# Usage:
#   source scripts/nfr/confluence_env.sh
#   # then also source secrets (see confluence_secrets.sh)
#   # finally run the publisher
#
# Notes:
# - Keep secrets in scripts/nfr/confluence_secrets.sh (user/token).
# - Prefer explicit category parent IDs. Alternatively, set TOP parent to derive.

# Localize shell options so sourcing doesn't affect your interactive shell
confluence_env__apply() {
    emulate -L zsh
    set -e
    set -u
    set -o pipefail

# --- Core Confluence config ---
# Confluence base URL, e.g. https://your-domain.atlassian.net/wiki
export CONFLUENCE_BASE_URL="https://nhsd-confluence.digital.nhs.uk/"

# Space key, e.g. FTRS
export CONFLUENCE_SPACE="FRS"

# Auth mode: basic (email+token) or bearer (PAT)
export CONFLUENCE_AUTH="bearer"

# --- Parent page targeting ---
# Preferred: explicit parents for the two categories
export CONFLUENCE_DOMAIN_PARENT_ID="1247790797"   # Parent of "NFRs by Domain"
export CONFLUENCE_SERVICE_PARENT_ID="1247790801"  # Parent of "NFRs by Service"

# Or derive both from a known top parent (optional)
# export CONFLUENCE_TOP_PARENT_ID=""

# Legacy: single parent for all (not recommended for service child pages)
# export CONFLUENCE_PARENT_ID=""

# --- Optional Jira enrichment (non-secret) ---
# Jira base URL (defaults to nhsd Jira if left blank here)
export JIRA_BASE_URL="https://nhsd-jira.digital.nhs.uk"

# Jira auth mode: basic or bearer (token provided in secrets script)
export JIRA_AUTH="bearer"

echo "[confluence_env] Loaded non-secret env vars. Remember to: source scripts/nfr/confluence_secrets.sh"
}

confluence_env__apply
unset -f confluence_env__apply
