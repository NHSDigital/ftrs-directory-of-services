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

## Running JMeter on EC2 (recommended for performance tests)

The infrastructure provisions an EC2 instance (private subnet) with JMeter pre-installed. Access is via the VPN. Default state is Stopped; start it when needed and stop it when done.

Requirements:
- Connected to the environment VPN
- AWS CLI authenticated and set to the correct account/region (default eu-west-2)
- If using SSH, ensure the instance was launched with your EC2 key pair and you have the corresponding .pem file
- Alternatively, you can use AWS Systems Manager Session Manager (no SSH key required)

Helper commands (run from tests/performance):

Start/Stop the EC2 instance
```shell
make jmeter-start AWS_REGION=eu-west-2
make jmeter-stop AWS_REGION=eu-west-2
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

SSH into the instance (requires VPN and SSH key)
```shell
make jmeter-ssh AWS_REGION=eu-west-2 SSH_KEY_PATH=~/.ssh/your-key.pem
```

Copy a plan to the instance and run it via SSM
```shell
# Copy plan over SSH
make jmeter-copy-plan AWS_REGION=eu-west-2 SSH_KEY_PATH=~/.ssh/your-key.pem PLAN=IS_Test_Plan.jmx

# Run plan with args via SSM
make jmeter-run-remote AWS_REGION=eu-west-2 PLAN=IS_Test_Plan.jmx ARGS='-n -l result.jtl'
```

Notes:
- The instance installs JMeter, plugin manager and common plugins on first boot and then powers off. This ensures the default state is Stopped.
- Set a key pair name in Terraform variable ssh_key_pair_name to enable SSH access.
- You can also SCP parameter files into the instance user home directory before running tests.

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
