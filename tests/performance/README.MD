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


### Install jmeter

```
asdf plugin add jmeter
asdf install
```

### aws Configuration

```
brew install awscli  # macOS
sudo apt install awscli  # Linux
```
Make sure your AWS CLI is configured and authenticated:
```
aws configure
aws sts get-caller-identity
```
You'll be prompted to enter:
```
AWS Access Key ID:
AWS Secret Access Key:
Default region (e.g., us-east-1, us-west-2):
Output format (json, table, text – default is json):
Alternatively, configure manually by editing these files:
```

```
Linux/macOS: ~/.aws/credentials and ~/.aws/config
Windows: C:\Users\USERNAME\.aws\credentials and C:\Users\USERNAME\.aws\config
```

Change aws config file with values listed in Service Teams - Set up SSO for AWS confluence page. Also use Dos developer profile from your aws console for your CLI connection.

## Test Configuration

### GUI setup
To be able to run the test plan from the GUI you will need to create a csv file called plan_params.csv that contains 3 data items
```
username,password,endpoint
```

### Test setup

The files required to populate the test parameters will need to be copied down from the appropriate S3 bucket via the command, either from Main or the workspaced bucket
```
download-workspace-performance-parameter-files

OR

download-performance-parameter-files
```

###
To load the GUI
```
jmeter
```

## Running the test plan

### From command line and sending a mtls pfx file

```
jmeter -n -t IS_Test_Plan.jmx -f -l result.csv -e -o "report"  -J serviceendpoint=<endpoint> -D javax.net.ssl.keyStore="<full paths to pfx file>" -D javax.net.ssl.keyStorePassword='<password for pfx file>'
```

To generate a dashboard report in the folder reports based on the result.jtl file generated when the test plan ran
```
jmeter -g result.jtl -f -e -o reports
```
