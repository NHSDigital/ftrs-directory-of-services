module.exports = async ({ needs, github, context }) => {

  const plan_max_length = 30000
  const lb = '\n\n';
  var output = '';


  function dedent(str) {
    // Trims leading whitespace from multiline raw strings so they can be indented, to keep the code readable
    const lines = str.split('\n');
    let minIndent = Infinity;
    // Determine the lowest common indent, excluding the first line
    lines.slice(1).forEach(line => {
      const indent = line.match(/^(\s+)\S+/);
      if (indent) {
        minIndent = Math.min(minIndent, indent[1].length);
      }
    });
    // Apply dedenting starting from the second line
    return [lines[0]].concat(lines.slice(1).map(line => line.startsWith(' ') ? line.slice(minIndent) : line)).join('\n');
  }

  function indent(str, indent) {
    // Adds leading whitespace to a multiline string to match code indent (except first line)
    var indentSpaces = ' '.repeat(indent);
    var lines = str.split('\n');
    return [lines[0]].concat(lines.slice(1).map(line => indentSpaces + line)).join('\n');
  }

  function unescape(str) {
    // Remove the escapes inserted by bash
    str = str.replace(/\\\$/g, '$');
    return str.replace(/\\\`/g, '`');
  }

  function tfreport(plan_scope, plan_outcome, plan_output, plan_summary) {
    output += `#### ${plan_scope} Terraform Plan 📖\`${plan_outcome}\`` + lb;
    if (plan_output) {
      let plan = unescape(String.raw`${plan_output}`);
      let truncated_message = ''
      if (plan.length == plan_max_length) {
        truncated_message = "Output is too long and was trimmed. You can read full Plan in " + run_link + lb;
        plan = '...' + plan;
      }
      output += dedent(`> ${plan_summary}

      <details><summary>Show Plan</summary>

      \`\`\`
      ${indent(plan, 6)}
      \`\`\`

      </details>
      ${indent(truncated_message, 6)}

      `);
    }
  }


  // 1. Retrieve existing bot comments for the PR
  const { data: comments } = await github.rest.issues.listComments({
    owner: context.repo.owner,
    repo: context.repo.repo,
    issue_number: context.issue.number,
  })
  const botComment = comments.find(comment => {
    return comment.user.type === 'Bot' && comment.body.includes('Programmes Setup Terraform Plan')
  })


  // 2. Prepare body of the comment
  const run_link = `<a href="${context.serverUrl}/${context.repo.owner}/${context.repo.repo}/actions/runs/${context.runId}">Actions</a>.`;


  // 2a. Impacts
  // The information is presented slightly differently if there are warnings
  // The markdown table will be expanded by default to draw attention to it
  if (needs.impacts.outputs.warnings) {
    output += dedent(`#### Change Governance 👮

    Impacts:

    ${indent(needs.impacts.outputs.impacts, 4)}

    `);
  }
  // needs.impacts.outputs.approvers will be null if there are warnings
  if (needs.impacts.outputs.approvers) {
    output += dedent(`#### Change Approvers 👮

    \`${needs.impacts.outputs.approvers}\`

    <details><summary>Show Impacts</summary>

    ${indent(needs.impacts.outputs.impacts, 4)}

    </details>

    `);
  }


  // 2b. Terraform for programmes setup
  tfreport(
    "Programmes Setup",
    needs.terraform.outputs.tfprogs_plan_outcome,
    needs.terraform.outputs.tfprogs_plan_output,
    needs.terraform.outputs.tfprogs_plan_summary
  )


  // 2c. Terraform for Permission Set config
  tfreport(
    "Permission Sets",
    needs.terraform.outputs.tfpermsets_plan_outcome,
    needs.terraform.outputs.tfpermsets_plan_output,
    needs.terraform.outputs.tfpermsets_plan_summary
  )

  tfreport(
    "TEAM Config",
    needs.terraform.outputs.tfteam_plan_outcome,
    needs.terraform.outputs.tfteam_plan_output,
    needs.terraform.outputs.tfteam_plan_summary
  )


  // 2d. Git-Secrets
  // interpret git-secrets output as a template literal (raw string)
  var gitsecrets = unescape(String.raw`${needs.gitsecrets.outputs.response}`);
  output += `#### Git-secrets Scanning 🔑\`${needs.gitsecrets.outputs.outcome}\`` + lb;

  if (needs.gitsecrets.outputs.outcome === "failure") {
    // git-secrets only produces output when checks fail
    output += dedent(`<details><summary>Show Errors</summary>

    \`\`\`
    ${indent(gitsecrets, 4)}
    \`\`\`

    </details>

    `);
  }


  // 2e. Footer
  output += dedent(`---
  *Triggered by: @${context.actor}, Action: \`${context.eventName}\`, Workflow: \`${context.workflow}\`*`);
  // The github-script 'context' object properties roughly correlate with the 'github' context in GitHub Actions
  // https://github.com/actions/toolkit/blob/main/packages/github/src/context.ts
  // https://docs.github.com/en/actions/learn-github-actions/contexts#github-context



  // 3. If there is an existing bot comment, update it, otherwise create a new one
  if (botComment) {
    github.rest.issues.updateComment({
      owner: context.repo.owner,
      repo: context.repo.repo,
      comment_id: botComment.id,
      body: output
    })
  } else {
    github.rest.issues.createComment({
      issue_number: context.issue.number,
      owner: context.repo.owner,
      repo: context.repo.repo,
      body: output
    })
  }

}
