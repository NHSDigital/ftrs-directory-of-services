#! /bin/bash

# fail on first error
set -e
# This script pushes a tag to the repository or moves an existing tag.

# TAG_TO_PUSH The name of the tag to push to the repository
# TAG_OVERWRITE Option as to whether we are allowed to move the tag if it exists in the repository already

EXPORTS_SET=0

if [ -z "$TAG_TO_PUSH" ] ; then
    echo TAG_TO_PUSH not set
    EXPORTS_SET=1
fi

if [ -z "$TAG_OVERWRITE" ] ; then
    echo TAG_OVERWRITE not set
    EXPORTS_SET=1
fi

if [ $EXPORTS_SET = 1 ] ; then
  echo One or more parameters not set
  exit 1
fi

echo "Push Tag Script invoked with the following parameters: "
echo "TAG_TO_PUSH: $TAG_TO_PUSH"
echo "TAG_OVERWRITE: $TAG_OVERWRITE"

echo "Checking to see if tag already exists: $TAG_TO_PUSH"
git fetch --tags
if [ -z "$(git tag -l "$TAG_TO_PUSH")" ]; then
  echo "Tag does not exist"
else
  echo "Tag exists"
  if [ "$TAG_OVERWRITE" == "yes" ]; then
    git push --delete origin "$TAG_TO_PUSH"
    git tag -d "$TAG_TO_PUSH"
  else
    echo "Exiting with error as we cannot overwrite an existing tag"
    exit 1
  fi
fi

echo "About to push tag: $TAG_TO_PUSH"

git tag "$TAG_TO_PUSH"
git push origin "$TAG_TO_PUSH"
