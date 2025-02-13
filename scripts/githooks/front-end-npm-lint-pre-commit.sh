#!/bin/bash
export FRONT_END_DIR="${FRONT_END_DIR:-"src/frontend"}"
# Navigate to the frontend directory if it exists
if [ -d "$FRONT_END_DIR" ]; then
  if git diff-index --quiet --cached HEAD "${FRONT_END_DIR}" ; then
    echo "No changes to code in ${FRONT_END_DIR}"
  else
    # Run the linter #
    npm run lint
  fi
else
  echo No code to lint
fi

