# Performance Test Framework

## Overview

This is a Performance Testing Framework using JMeter to load test services within FTRS. The framework supports multiple test modes (proxy, load, stress) and can run tests either locally or on EC2 instances.

## Project Structure

```
├── performance/
    ├── parameter_files/          # Test data files (CSV, certificates, etc.)
    ├── IS_Test_Plan.jmx          # Main unified test plan (supports all modes)
    ├── scripts/
    │   ├── LoadParams.groovy     # Parameter loading script
    ├── Makefile
    └── README.MD
```

## Prerequisites and Configuration

See the main README.MD for general prerequisites.

### Install JMeter (local developer machine)

```sh
cd tests/performance
make install
```

This will:
- Install JMeter
- Install required JMeter plugins (PreciseThroughputTimer, VariableThroughputTimer, etc.)
- Install dependencies (AWS SDK JARs for Secrets Manager integration)

## Test Plan Overview: IS_Test_Plan.jmx

The `IS_Test_Plan.jmx` is a unified test plan that supports three different test modes via the `-Jtest_mode` parameter:

### Test Modes

1. **`test_mode=proxy`** - Tests via APIM proxy with JWT authentication
   - Runs: Get Token Thread Group (generates JWT and bearer token)
   - Runs: Organization Search Proxy Thread Group
   - Uses: APIM endpoint 
   - Authentication: JWT tokens from AWS Secrets Manager
   - Timer: PreciseThroughputTimer for consistent load

2. **`test_mode=load`** - Direct backend load testing with mTLS
   - Runs: Organization Search Backend Thread Group
   - Uses: Direct service endpoint 
   - Authentication: mTLS with PFX certificate
   - Timer: PreciseThroughputTimer for consistent load

3. **`test_mode=stress`** - Stress testing with ramped throughput
   - Runs: Organization Requests Backend Thread Group
   - Uses: Direct service endpoint with mTLS
   - Timer: Throughput Shaping Timer with configurable steps
   - Gradually increases load in steps

### Key Features

- **Setup Thread Group**: Runs first to initialize test mode variables and load parameters from `LoadParams.groovy`
- **Conditional Execution**: Each Thread Group has If Controllers that only execute in the appropriate test mode
- **Flow Control Actions**: Prevents StackOverflowError with infinite loops by stopping threads when not in the correct mode
- **Flexible Configuration**: All test parameters are configurable via command-line properties (`-J` flags)

### Common Parameters

All test modes support these parameters:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `test_mode` | Test mode: `proxy`, `load`, or `stress` | (required) |
| `num_threads` | Number of concurrent threads | 1 |
| `ramp_time` | Ramp-up time in seconds | 1 |
| `duration` | Test duration in seconds | 10 |
| `startup_delay` | Delay before starting in seconds | 0 |
| `loop_count` | Loop iterations (-1 for infinite) | 1 |

### Load Mode Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `serviceendpoint` | Backend service endpoint | (required) |
| `timer_throughput` | Target throughput (requests/period) | 9000.0 |
| `timer_throughput_period` | Period in seconds | 60 |

### Proxy Mode Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `apim_env` | APIM environment (e.g., `internal-dev`) | (required) |
| `env` | AWS environment | (required) |
| `AWS_SECRET_NAME` | AWS Secrets Manager secret name | (required) |
| `Apim_Domain` | APIM domain suffix | `.api.service.nhs.uk` |
| `token_duration` | Token refresh duration | 30 |
| `token_loop_count` | Token refresh loop count | -1 |

### Stress Mode Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `serviceendpoint` | Backend service endpoint | (required) |
| `throughput_step` | Throughput increase per step (req/sec) | 50 |
| `step_duration` | Duration of each step in seconds | 300 |

**Important Note for Stress Testing**: The Throughput Shaping Timer has 12 steps configured. The total test duration is calculated as:
```
Total Duration = 12 steps × step_duration
```
For a 5-minute (300 second) test, set `step_duration=25` (12 × 25 = 300 seconds).

## Test Configuration

### Test Setup

The files required to populate test parameters will need to be copied from the appropriate S3 bucket:
```sh
make download-performance-files
```

### GUI Setup
To run a test plan from the GUI, create `test_params.csv` with the following format:
```
APIM Env address, AWS Env, AWS Secret Name, internal R53 endpoint address

# Example:
internal-dev, dev, my-secret, test.dev.domain.uk

### Certificate Setup

Generate a PFX file from certificate and key files for mTLS authentication:
```sh
make jmeter-generate-pks-file \
  CERT_NAME=your-cert \
  KEY_NAME=your-key \
  PFX_NAME=jmeter_pfx \
  ENVIRONMENT=dev

# Or manually:
openssl pkcs12 -export \
  -in <cert-name>.crt \
  -inkey <key-name>.pem \
  -out <pfx-name>.pfx
```
You will be prompted to set a password for the PFX file.

Store the PEM file that corresponds to the API Key and KID extracted from the aws secret 

### Launch JMeter GUI
```sh
jmeter
```

## Running the Test Plan

### Using Make Targets

The Makefile provides convenient targets for running tests:

#### Load Testing (mTLS - Direct Backend)
```sh
make performance-test-mtls \
  PLAN_NAME=IS_Test_Plan \
  ENDPOINT=myendpoint.dev.ftrs.cloud.nhs.uk \
  PFX_PATH="path to pfx"  \
  PFX_PASSWORD="yourpassword" \
  NUM_THREADS=10 \
  RAMP_TIME=1 \
  DURATION=300 \
  STARTUP_DELAY=0 \
  THROUGHPUT=100 \
  THROUGHPUT_PERIOD=60
```

#### Proxy Testing (JWT Authentication via APIM)
```sh
make performance-test-jwt \
  PLAN_NAME=IS_Test_Plan \
  APIM_ENV=internal-dev \
  ENV=dev \
  SECRET_NAME="aws secret name"" \
  NUM_THREADS=10 \
  RAMP_TIME=1 \
  DURATION=300 \
  STARTUP_DELAY=0 \
  THROUGHPUT=100 \
  THROUGHPUT_PERIOD=60
```

#### Stress Testing (Ramped Throughput with mTLS)
```sh
make performance-stress-test-mtls \
  PLAN_NAME=IS_Test_Plan \
  ENDPOINT=myendpoint.dev.ftrs.cloud.nhs.uk \
  PFX_PATH="path to pfx" \
  PFX_PASSWORD="yourpassword" \
  NUM_THREADS=30 \
  RAMP_TIME=1 \
  DURATION=300 \
  STARTUP_DELAY=10 \
  THROUGHPUT_STEP=5 \
  STEP_DURATION=25
```
**Note**: For stress tests, ensure `STEP_DURATION × 12 steps = DURATION` for complete ramp profile.

### Running from Command Line

#### Load Mode (Direct Backend with mTLS)
```sh
jmeter -n -t IS_Test_Plan.jmx \
  -J serviceendpoint=myendpoint.dev.ftrs.cloud.nhs.uk \
  -f -l result.jtl -e -o "report" \
  -D javax.net.ssl.keyStore=PFX_PATH="path to pfx"  \
  -D javax.net.ssl.keyStorePassword="yourpassword" \
  -J test_mode="load" \
  -J num_threads=10 \
  -J ramp_time=1 \
  -J duration=300 \
  -J startup_delay=0 \
  -J timer_throughput=100 \
  -J timer_throughput_period=60
```

#### Proxy Mode (APIM with JWT)
```sh
jmeter -n -t IS_Test_Plan.jmx \
  -J apim_env=internal-dev \
  -J env=dev \
  -J AWS_SECRET_NAME="aws secret name" \
  -f -l result.jtl -e -o "report" \
  -J test_mode="proxy" \
  -J num_threads=10 \
  -J ramp_time=1 \
  -J duration=300 \
  -J startup_delay=0 \
  -J timer_throughput=100 \
  -J timer_throughput_period=60
```

#### Stress Mode (Ramped Throughput)
```sh
jmeter -n -t IS_Test_Plan.jmx \
  -J serviceendpoint=myendpoint.dev.ftrs.cloud.nhs.uk \
  -f -l result.jtl -e -o "report" \
  -D javax.net.ssl.keyStore="path to pfx file" \
  -D javax.net.ssl.keyStorePassword="yourpassword" \
  -J test_mode="stress" \
  -J num_threads=30 \
  -J ramp_time=1 \
  -J duration=300 \
  -J startup_delay=10 \
  -J throughput_step=5 \
  -J step_duration=25
```

### Generate Dashboard Report
```sh
make performance-test-dashboard TEST_DATA=result

# Or directly with JMeter:
jmeter -g result.jtl -f -e -o reports
```

## File Management

### Uploading Files to S3

Upload a single file to S3:
```sh
make upload-performance-file \
  WORKSPACE=ftrs-1234/ \
  FILE_PATH=./temp/ \
  FILE=folder_test.txt
```

Upload an entire folder to S3:
```sh
make upload-performance-folder \
  WORKSPACE=ftrs-1234/ \
  LOCAL_DIR=temp
```

### Downloading Files from S3

Download performance files from S3:
```sh
make download-main-performance-files LOCAL_DIR=temp
```


## Running JMeter on EC2 (Recommended for Performance Tests)

The infrastructure provisions an EC2 instance (private subnet) with JMeter pre-installed. Access is via AWS Systems Manager (SSM). The instance defaults to a stopped state - start it when needed and stop when done to save costs.

### Instance Management

Start the EC2 instance:
```sh
make jmeter-start-instance JMETER_INSTANCE_ID=i-xxxxxxxxxxxxxxxxx
```

Stop the EC2 instance:
```sh
make jmeter-stop-instance JMETER_INSTANCE_ID=i-xxxxxxxxxxxxxxxxx
```

Check instance details:
```sh
make jmeter-ec2-id JMETER_INSTANCE_ID=i-xxxxxxxxxxxxxxxxx
make jmeter-private-ip JMETER_INSTANCE_ID=i-xxxxxxxxxxxxxxxxx
```

Verify JMeter version on EC2:
```sh
make jmeter-version-remote JMETER_INSTANCE_ID=i-xxxxxxxxxxxxxxxxx
```

### File Transfer to EC2

#### Copy Single File to EC2
```sh
make jmeter-copy-ssm-inline \
  JMETER_INSTANCE_ID=i-xxxxxxxxxxxxxxxxx \
  FILE=IS_Test_Plan.jmx \
  DEST=IS_Test_Plan.jmx
```

Copy a file from a subdirectory:
```sh
make jmeter-copy-ssm-inline \
  JMETER_INSTANCE_ID=i-xxxxxxxxxxxxxxxxx \
  FILE=parameter_files/odscodes.csv \
  DEST=odscodes.csv
```

#### Copy Directory to EC2
Use this to send an entire directory (e.g., `parameter_files`) to the instance:

```sh
make jmeter-copy-dir-ssm-inline \
  JMETER_INSTANCE_ID=i-xxxxxxxxxxxxxxxxx \
  DIR=parameter_files \
  DEST_DIR=parameter_files
```

Place files directly in `/home/ssm-user` (no subfolder):
```sh
make jmeter-copy-dir-ssm-inline \
  JMETER_INSTANCE_ID=i-xxxxxxxxxxxxxxxxx \
  DIR=parameter_files \
  DEST_DIR=.
```

### File Transfer from EC2

#### Download Single File from EC2
```sh
make jmeter-fetch-file-inline \
  JMETER_INSTANCE_ID=i-xxxxxxxxxxxxxxxxx \
  REMOTE_FILE=result.jtl \
  LOCAL_DIR=downloads/testfolder
```

Download to an exact local path:
```sh
make jmeter-fetch-file-inline \
  JMETER_INSTANCE_ID=i-xxxxxxxxxxxxxxxxx \
  REMOTE_FILE=result.jtl \
  LOCAL_FILE=downloads/testfolder/my-result.jtl
```

Fetch from an absolute remote path:
```sh
make jmeter-fetch-file-inline \
  JMETER_INSTANCE_ID=i-xxxxxxxxxxxxxxxxx \
  REMOTE_FILE=/home/ssm-user/artifacts/result.jtl
```

#### Download Directory from EC2
Download all regular files from a remote directory:
```sh
make jmeter-fetch-dir-inline \
  JMETER_INSTANCE_ID=i-xxxxxxxxxxxxxxxxx \
  REMOTE_DIR=artifacts \
  LOCAL_DIR=downloads/testfolder
```

### Interactive EC2 Access

Open an SSM shell session to run JMeter tests manually:
```sh
make jmeter-ssm-shell JMETER_INSTANCE_ID=i-xxxxxxxxxxxxxxxxx
```

## Notes and Best Practices

### File Transfer Notes
- Very large files may exceed SSM inline limits; if you hit failures, split files or use S3
- File transfers are non-recursive; subdirectories must be copied separately
- The EC2 instance must be SSM-managed and in a running state
- Your AWS CLI credentials must have SSM permissions

### Test Execution Best Practices
1. **Run performance tests on EC2** to avoid network variability from local machines
2. **Use appropriate test modes**:
   - `proxy` mode for testing APIM integration and JWT authentication
   - `load` mode for sustained load testing against direct endpoints
   - `stress` mode for testing system behavior under increasing load
3. **Calculate stress test duration correctly**: `total_duration = 12 × step_duration`
4. **Monitor thread count**: Ensure `num_threads` is sufficient for target throughput. threads ≥ (target_TPS × avg_response_time_seconds)
5. **Use infinite loops with duration**: Set `loop_count=-1` and specify `duration` for time-based tests

