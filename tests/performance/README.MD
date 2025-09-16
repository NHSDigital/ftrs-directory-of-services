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

```shell

# In the performance directory
cd tests/performance
make install
```

## Test Configuration

### GUI setup
To be able to run a test plan from the GUI you will need to create a csv file called plan_params.csv that contains 3 data items
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

### From command line and sending a mtls pfx file

```
jmeter -n -t IS_Test_Plan.jmx -f -l result.jtl -e -o "report"  -J serviceendpoint=<endpoint> -D javax.net.ssl.keyStore="<full paths to pfx file>" -D javax.net.ssl.keyStorePassword='<password for pfx file>'
```

### From command line and sending a request with a JWT token

The *Generate JWT Token - JSR223 PreProcessor* generates a JWT token based on the provided KID and API Key.
This is then passed to *Get Bearer Token* request a bearer token to be sent in the request header

```
jmeter -n -t IS_Proxy_Test_Plan.jmx -f -l result.jtl -e -o "report" -J serviceendpoint=<endpoint> -J proxyendpoint=<proxyendpoint>  -J apikey=<apikey> -J kid=<kid>
```

To generate a dashboard report in the folder reports based on the result.jtl file generated when the test plan ran
```
jmeter -g result.jtl -f -e -o reports
```
