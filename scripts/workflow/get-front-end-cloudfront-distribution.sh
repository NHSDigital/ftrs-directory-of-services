#! /bin/bash

# This script gets the cloud front distribution id for the front end
#

if [ -z "$ENVIRONMENT" ]; then
  echo "Set the ENVIRONMENT environment variable" >&2
  exit 1;
fi

if [ -z "$WORKSPACE" ]; then
  echo "Set the WORKSPACE environment variable" >&2
  exit 1;
fi

if [ -z "$DOMAIN" ]; then
  echo "Set the DOMAIN environment variable" >&2
  exit 1;
fi

if [ -z "$AWS_REGION" ]; then
  echo "Set the AWS_REGION environment variable" >&2
  exit 1;
fi

if [ "$WORKSPACE" = "default" ]; then
  FRONT_END_DOMAIN="nhse-${DOMAIN}-${ENVIRONMENT}-front-end.s3.${AWS_REGION}.amazonaws.com"
else
  FRONT_END_DOMAIN="nhse-${DOMAIN}-${ENVIRONMENT}-front-end-${WORKSPACE}.s3.${AWS_REGION}.amazonaws.com"
fi

QUERY_COMMAND="DistributionList.Items[?Origins.Items[0].DomainName=='$FRONT_END_DOMAIN'].{Id: Id}[0].Id"

DISTRIBUTION_ID=$(aws cloudfront list-distributions --query "$QUERY_COMMAND")
echo $DISTRIBUTION_ID
