#!/bin/bash

# fail on first error
set -e

export WORKSPACE="${WORKSPACE:-""}"
export OPEN_SEARCH_DOMAIN="${OPEN_SEARCH_DOMAIN:-""}"
export INDEX="${INDEX:-""}"

echo "Building Open Search Index: ${INDEX} on Open Search Domain: ${OPEN_SEARCH_DOMAIN} in Workspace: ${WORKSPACE}"

curl -X PUT "https://${OPEN_SEARCH_DOMAIN}/_index/${INDEX}${WORKSPACE}" \
  -H "Content-Type: application/json" \
  -d '{
    "mappings": {
        "properties": {
            "primary_key": {"type": "keyword"},
            "sgsd": {
                "type": "nested",
                "properties": {
                    "sg": {"type": "integer"},
                    "sd": {"type": "integer"}
                }
            }
        }
    }
}'

echo "Index ${INDEX}${WORKSPACE} created successfully."
