# Fetch main branch from origin (remote repo).
git fetch origin main

# Compare the new branch to main and return a list of changed files
FILES="$(git diff --staged --name-only origin/main..HEAD)"

# check committed changes for updates to codeowner files
for FILE in ${FILES}; do
  echo "Processing file: ${FILE}"
  if [[ "${FILE}" == ".github/CODEOWNERS" ]]; then
    WARNINGS+="Governance|⚠️ Codeowners|Check carefully before approving!\n"
  fi
done

# Create a Markdown table for the Pull Request
if [[ -n ${WARNINGS} ]]; then
  IMPACTS="Scope|Type|Check / Approver(s)\n:-----|:---|:------\n${WARNINGS}"
fi

# randomize the Heredoc delimiter to reduce risk of an injection attack
# https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions#understanding-the-risk-of-script-injections
DELIM=$(echo ${RANDOM} | base64)

{
  echo "impacts<<${DELIM}"
  echo -e "${IMPACTS}"
  echo "${DELIM}"
} >> "$GITHUB_OUTPUT"
