# JWT Token Generation

Simple tools for generating JWT tokens for API authentication.

## Setup
Install required dependencies
```bash
make install
```

## Usage

**Local Development (environment variables):**

Set required environment variables:
```bash
export API_KEY="your-api-key"
export PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----"
export KID="your-key-id"
export TOKEN_URL="https://your-token-endpoint/oauth2/token"

make jwt-token env=local
```
Generate token
```
make jwt-token env=local
```

**AWS Secrets Manager:**

Configure AWS credentials (required for dev/int environments):

```
aws configure

# OR set environment variables:

export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_REGION="eu-west-2"
```

Fetch secrets from AWS Secret Manager and generate token for env (e.g dev, int etc)
```bash
make jwt-token env=dev
```

## Secret Format

AWS Secrets Manager secret: `/ftrs-dos/{environment}/apim-jwt-credentials`

```json
{
  "api_key": "your-api-key",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----",
  "kid": "your-key-id",
  "token_url": "https://your-token-endpoint/oauth2/token"
}
```
