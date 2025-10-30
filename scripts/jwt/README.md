# JWT Token Generation

Simple tools for generating JWT tokens for API authentication.

## Setup

Install required dependencies:

```bash
make install
```

## Usage

**Local Development (environment variables):**

Set required environment variables

```bash
export API_KEY="your-key"
export PRIVATE_KEY="example_key_value"
export KID="your-key-id"
export TOKEN_URL="https://your-token-endpoint/oauth2/token"
```

Generate token:

```bash
make jwt-token env=local
```

---

**AWS Secrets Manager:**

Configure AWS credentials (required for dev/int environments)

```bash
aws configure
```

Or set environment variables:

```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_REGION="eu-west-2"
```

Fetch secrets from AWS Secrets Manager and generate token for environment.

```bash
make jwt-token env=dev
```

## Secret Format

AWS Secrets Manager secret:
`/ftrs-dos/{environment}/apim-jwt-credentials`

```json
{
  "api_key": "your-key",
  "private_key": "example_key_value",
  "kid": "your-key-id",
  "token_url": "https://your-token-endpoint/oauth2/token"
}
```
