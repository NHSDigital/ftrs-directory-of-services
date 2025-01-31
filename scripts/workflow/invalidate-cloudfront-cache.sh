#! /bin/bash

# This script invalidates the CloudFront cache
export FRONT_END_DIR="${FRONT_END_DIR:-"src/frontend"}"
# Check frontend directory  exists
if [ -d "$FRONT_END_DIR" ]; then
  if [ -z "$DISTRIBUTION_ID" ]; then
    echo "DISTRIBUTION_ID is not set."
    echo "CloudFront cache will not be invalidated"
  else
    echo "Invalidating CloudFront cache"
    DISTRIBUTION_ID=$(echo "$DISTRIBUTION_ID" | sed 's/"//g')
    aws cloudfront create-invalidation --distribution-id $DISTRIBUTION_ID --paths "/*"
  fi
else
  echo No frontend source code
fi


