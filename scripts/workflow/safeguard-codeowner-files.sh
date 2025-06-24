# Fetch main branch from origin (remote repo).
git fetch origin main

# Compare the new branch to main and return a list of changed files
FILES="$(git diff --name-only origin/main..HEAD)"

# check committed changes for updates to codeowner files
for FILE in ${FILES}; do
  if [[ "${FILE}" == ".github/CODEOWNERS" ]]; then
    echo "Processing file: ${FILE}"
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
echo "${WARNINGS}"
echo "${IMPACTS}"
{
  echo "warnings<<${DELIM}"
  echo -e "${WARNINGS}"
  echo "${DELIM}"
} >> "$GITHUB_OUTPUT"

{
  echo "impacts<<${DELIM}"
  echo -e "${IMPACTS}"
  echo "${DELIM}"
} >> "$GITHUB_OUTPUT"
