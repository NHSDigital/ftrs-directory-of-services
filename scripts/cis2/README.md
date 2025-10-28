# CIS2 Key Pair Generation

This directory contains scripts for managing CIS2 (Care Identity Service 2) authentication keys.

## Overview

The `create-cis2-key-pair.sh` script generates RSA 4096-bit key pairs for CIS2 authentication and stores them securely in AWS Secrets Manager. The script:

- Generates a new RSA 4096-bit private key
- Extracts the corresponding public key
- Converts the public key to JWKS (JSON Web Key Set) format
- Automatically increments the key ID (kid) for key rotation
- Stores both keys in AWS Secrets Manager

## Prerequisites

Before running the script, ensure you have the following installed and configured:

### Required Tools

1. **OpenSSL** - For generating and manipulating keys

   ```bash
   # Check if installed
   openssl version
   ```

2. **`jq`** - For JSON processing

   ```bash
   # Check if installed
   jq --version

   # Install on macOS
   brew install jq

   # Install on Linux
   sudo apt-get install jq  # Debian/Ubuntu
   sudo yum install jq      # RHEL/CentOS
   ```

3. **AWS CLI** - For interacting with AWS Secrets Manager

   ```bash
   # Check if installed
   aws --version

   # Install on macOS
   brew install awscli
   ```

### AWS Configuration

1. **AWS Credentials** - Configure your AWS credentials

   ```bash
   aws configure
   ```

   OR

   AWS CLI Access can be configured via AWS SSO if needed: [AWS Single Sign-on (SSO) User Access - AWS CLI Access](https://nhsd-confluence.digital.nhs.uk/spaces/AWS/pages/592551759/AWS+Single+Sign+on+SSO+User+Access#AWSSingleSignon(SSO)UserAccess-AWSCLIAccess)

2. **AWS Permissions** - Ensure your AWS user/role has the following permissions:

   - `secretsmanager:DescribeSecret`
   - `secretsmanager:GetSecretValue`
   - `secretsmanager:UpdateSecret`

3. **Existing Secrets** - The secrets must already exist in AWS Secrets Manager:

   - `/<repo-name>/<environment>/cis2-private-key`
   - `/<repo-name>/<environment>/cis2-public-key`

   The script updates existing secrets rather than creating new ones.

## Usage

### Basic Syntax

```bash
./create-cis2-key-pair.sh -r <REPO_NAME> -e <ENVIRONMENT>
```

### Parameters

| Parameter | Short | Long | Required | Description |
|-----------|-------|------|----------|-------------|
| Repository | `-r` | `--repo-name` | Yes | Repository name (e.g., ftrs-directory-of-services) |
| Environment | `-e` | `--environment` | Yes | Target environment (e.g., dev, int, test, prod) |
| Help | `-h` | `--help` | No | Display help message |

### Examples

#### Development Environment

```bash
./create-cis2-key-pair.sh -r ftrs-directory-of-services -e dev
```

#### Integration Environment

```bash
./create-cis2-key-pair.sh -r ftrs-directory-of-services -e int
```

#### Production Environment

```bash
./create-cis2-key-pair.sh -r ftrs-directory-of-services -e prod
```

## Key Rotation

The script automatically handles key rotation by:

1. Checking if a public key already exists in AWS Secrets Manager
2. Extracting the current key ID (kid) from the existing JWKS
3. Incrementing the numeric portion of the kid (for example, changing from `environment-1` to `environment-2`)
4. Generating a new key pair with the incremented kid

### Key ID Format

Key IDs follow the format: `<environment>-<number>`

Examples:

- `dev-1`, `dev-2`, `dev-3`
- `prod-1`, `prod-2`, `prod-3`

## Output

Upon successful execution, the script will:

1. Display progress messages with color-coded output:

   - 🟢 **Green** - Informational messages
   - 🟡 **Yellow** - Warnings
   - 🔴 **Red** - Errors

2. Store the private key in PEM format at:

   ```text
   /<repo-name>/<environment>/cis2-private-key
   ```

3. Store the public key in JWKS format at:

   ```text
   /<repo-name>/<environment>/cis2-public-key
   ```

4. Display a summary:

   ```text
   ========================================
   Key pair generation and storage complete!
   Private key stored in: /ftrs-directory-of-services/dev/cis2-private-key
   Public key stored in: /ftrs-directory-of-services/dev/cis2-public-key
   ========================================
   ```

## Security Considerations

- **Temporary Files**: The script creates temporary files in a secure temporary directory, which are automatically cleaned up on exit
- **Private Key**: Never commit or share the private key. It is stored securely in AWS Secrets Manager only
- **Access Control**: Ensure proper IAM policies are in place to restrict access to the secrets
- **Key Rotation**: Regularly rotate keys according to your security policy

## Troubleshooting

### Common Issues

#### 1. "`jq` is required but not installed"

**Solution**: Install `jq` using your package manager (see Prerequisites)

#### 2. "Failed to generate private key"

**Solution**: Ensure OpenSSL is installed and up to date

   ```bash
   openssl version
   ```

#### 3. "Secret does not exist"

**Solution**: Create the secrets in AWS Secrets Manager from the CI/CD pipeline before running the script

#### 4. "Access Denied" errors

**Solution**: Verify your AWS credentials and IAM permissions

   ```bash
   # Check current AWS identity
   aws sts get-caller-identity

   # Verify access to Secrets Manager
   aws secretsmanager list-secrets
   ```

#### 5. "Could not parse existing kid number"

**Solution**: This is a warning, not an error. The script will start from kid number 1. Verify the JWKS format in the existing secret if needed.

## Key Rotation from the Github CI/CD pipeline

To achieve the same results from the above steps, we have a Github workflow. Steps to execute the workflow and the verification can be found [here](https://nhsd-confluence.digital.nhs.uk/x/ERhBS)

## Additional Resources

- [AWS Secrets Manager Documentation](https://docs.aws.amazon.com/secretsmanager/)
- [JWKS Specification](https://datatracker.ietf.org/doc/html/rfc7517)
- [OpenSSL Documentation](https://www.openssl.org/docs/)

## Support

For issues or questions, please contact the development team or create an issue in the repository.
