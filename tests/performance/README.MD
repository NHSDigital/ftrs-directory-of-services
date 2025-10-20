# Performance Test Framework

## Overview

This is an Performance Framework using JMeter to load test services within FtRS

## Project Structure

```
├── performance/
    ├── service
        ├── tests
        │   ├── parameter_files
        ├── test_plan.jmx
        ├── README.MD
```

## Prerequisites and Configuration

See those in the main README.MD


### Install jmeter (local developer machine)

```shell
cd tests/performance
make install
```

## Test Configuration

### GUI setup
To be able to run a test plan from the GUI you will need to create a csv file called plan_params.csv that contains 4 data items. These 4 items are required to be able to run any of the test plans
```
internal R53 endpoint address, APIM Env address , APIM API Key, kid name

example:
test.dev.domain.uk,int.api.service.nhs.uk,tr24234yyr2342,mykid
```

### Test setup

The files required to populate the test parameters will need to be copied down from the appropriate S3 bucket via the command, either from Main or the workspaced bucket
```
make download-workspace-performance-parameter-files

OR

make download-performance-parameter-files
```
Generate a pfx file by converting the crt and pem files.
You will be prompted to set a password for this file

```
openssl pkcs12 -export -in <cert name>>.crt -inkey <key name>>.pem -out <pfx name>.pfx

```

###
To load the GUI
```
jmeter
```

## Running the test plan
Example parameter values:
PLAN_NAME = IS_Proxy_Test_Plan or IS_Test_Plan
SERVICEENDPOINT = test.dev.ftrs.cloud.nhs.uk
APIM_ENV = internal-dev
APIKEY = tr24234yyr2342
KID = my-kid

Store the pem file that corresponds to the APIKEY and KID in /parameter_files

### From command line and sending a mtls pfx file

```
jmeter -n -t IS_Test_Plan.jmx -f -l result.jtl -e -o "report"  -J serviceendpoint=<endpoint> -D javax.net.ssl.keyStore="<full paths to pfx file>" -D javax.net.ssl.keyStorePassword='<password for pfx file>'
```

### From command line and sending a request with a JWT token

The *Generate JWT Token - JSR223 PreProcessor* generates a JWT token based on the provided KID and API Key.
This is then passed to *Get Bearer Token* request a bearer token to be sent in the request header


```
jmeter -n -t IS_Proxy_Test_Plan.jmx -f -l result.jtl -e -o "report" -J apim_env=<apim_env>  -J apikey=<apikey> -J kid=<kid>
```

To generate a dashboard report in the folder reports based on the result.jtl file generated when the test plan ran
```
jmeter -g result.jtl -f -e -o reports
```

## Running JMeter on EC2 (recommended for performance tests)

The infrastructure provisions an EC2 instance (private subnet) with JMeter pre-installed. Access is via the VPN. Default state is Stopped; start it when needed and stop it when done.

Requirements:
- Connected to the environment VPN
- AWS CLI authenticated and set to the correct account/region (default eu-west-2)
- Alternatively, you can use AWS Systems Manager Session Manager (no SSH key required)

Helper commands (run from tests/performance):

Start/Stop the EC2 instance
```shell
make jmeter-start-instance AWS_REGION=eu-west-2
make jmeter-stop-instance AWS_REGION=eu-west-2
```

Check instance details
```shell
make jmeter-ec2-id AWS_REGION=eu-west-2
make jmeter-private-ip AWS_REGION=eu-west-2
```

Verify JMeter version on EC2 via SSM
```shell
make jmeter-version-remote AWS_REGION=eu-west-2
```

Open an SSM session
```shell
# Open an interactive Session Manager shell to the instance
make jmeter-ssm-shell AWS_REGION=eu-west-2
```

Run a plan via SSM (interactive, streams output)
```shell
# The plan file must exist in the EC2 user's home directory
# Output is streamed live and also saved to jmeter.out; JMeter writes jmeter.log in the same directory
make jmeter-run-remote AWS_REGION=eu-west-2 PLAN=jmeter_test_plan.jmx \
  ARGS='-n -l result.jtl -J serviceendpoint=internal-dev.api.service.nhs.uk -J bearer_token=<token> -f -e -o report'
```

### Copy the plan to EC2 without SSH (SSM inline)
Use the SSM inline base64 method to place the plan on the instance without SSH or S3.

```shell
# Copies local jmeter_test_plan.jmx to the EC2 instance home directory
make jmeter-copy-plan-ssm-inline AWS_REGION=eu-west-2 PLAN=jmeter_test_plan.jmx DEST=jmeter_test_plan.jmx
```

Notes:
- This uses AWS Systems Manager to send the plan content inline (base64) and reconstruct it on the instance
- Suitable for small/medium files; very large JMX plans may exceed SSM command size limits. If that happens, consider a temporary HTTPS download approach (e.g., presigned URL) or splitting the plan

Notes:
- You don't need to "start JMeter" as a service; JMeter runs when invoked and exits when done. The start/stop commands above control the EC2 instance
- The instance installs JMeter, plugin manager and common plugins on first boot and then powers off. This ensures the default state is Stopped.
- You can also copy parameter files into the instance user home directory before running tests (e.g., by SSM commands or your preferred method).


## jmeter_test_plan.jmx (user-supplied bearer token)

This plan calls the FHIR Organization search with:
- Authorization: Bearer <user-supplied token>
- Query params: _revinclude=Endpoint:organization and identifier=odsOrganisationCode|<ODS from CSV>
- Host is parameterized via -J serviceendpoint or the first column in parameter_files/plan_params.csv

Inputs:
- parameter_files/odscodes.csv with header `ods_code`
- A Bearer token supplied either as a JMeter property (-J bearer_token=...) or via env var BEARER_TOKEN

Run example (recommended):

```shell
jmeter -n -t jmeter_test_plan.jmx \
  -J serviceendpoint=internal-dev.api.service.nhs.uk \
  -J bearer_token="<paste-your-token>" \
  -f -l result.jtl -e -o report
```

Tip: In an interactive shell, you can export BEARER_TOKEN and omit -J bearer_token. If both are set, -J bearer_token takes precedence.

Notes:
- One request per CSV row; with 72 rows, 72 requests total (1 thread). Increase threads for concurrency.
- HTTP target path is `/dos-search/FHIR/R4/Organization` and params are URL-encoded by JMeter.
