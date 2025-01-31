# Workflow scripts

The scripts in this directory are checked out as part of the checkout-repository action
(see .github/actions/checkout-repository/action.yaml)

Which version of those scripts is checked out is determined by the management-tag input parameter
That parameter will be set by default to the latest stable release

If you are changing any of the scripts in this directory or below you are advised to pass your task branch as a parameter
