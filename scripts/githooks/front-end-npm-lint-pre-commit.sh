#!/bin/bash

export FRONT_END_DIR="${FRONT_END_DIR:-"src/frontend"}"
# Navigate to the frontend directory if it exists
if [ -d "$FRONT_END_DIR" ]; then
  cd "$FRONT_END_DIR"  || exit
  # Run the linter #
  npm run lint
else
  echo No code to lint
fi

