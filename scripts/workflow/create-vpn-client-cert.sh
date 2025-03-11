#! /bin/bash

set -e

# This script generates an .ovpn file to get a team member onto the VPN.
# Before running this bootstrapper script:
#  - Login to an appropriate AWS account as the appropriate user from the command line.
#  - Export the following variables prior to calling this script (they are not set here to avoid storing details in the repo):
#       USER_SHORTCODE
#       PROJECT              (e.g. "ftrs-directory-of-services")
#       ENVIRONMENT          (e.g. "dev")
#
#  - Optionally export:
#       VPN_DOMAIN         (defaults to PROJECT)
#       VPN_DESC           (defaults to "PROJECT-ENVIRONMENT-vpn")
#       TEMP_VPN_CERT_DIR  (defaults to "PROJECT-ENVIRONMENT-vpn-certs" in the home directory)
#       OPEN_VPN_ROOT      (defaults to "~/projects/open-vpn", path to your local clone of the open-vpn repo)

# Check that required exports have been set.
if [ -z "${USER_SHORTCODE:-}" ]; then
  echo "ERROR: USER_SHORTCODE not set"
  exit 1
fi

# Set  environment variables if not provided.
export PROJECT="${PROJECT:-ftrs-directory-of-services}"
export ENVIRONMENT="${ENVIRONMENT:-dev}"
export VPN_DOMAIN="${VPN_DOMAIN:-${PROJECT}-${ENVIRONMENT}}"
export VPN_DESC="${VPN_DESC:-${PROJECT}-${ENVIRONMENT}-vpn}"
export TEMP_VPN_CERT_DIR="${TEMP_VPN_CERT_DIR:-${PROJECT}-${ENVIRONMENT}-vpn-certs}"

echo "Creating cert and key for user '$USER_SHORTCODE' for VPN '$VPN_DESC'"

# Determine the OpenVPN project directory.
if [ -n "${OPEN_VPN_ROOT:-}" ]; then
  OPEN_VPN_PROJ_DIR="$OPEN_VPN_ROOT/easy-rsa/easyrsa3"
else
  OPEN_VPN_PROJ_DIR="~/projects/open-vpn/easy-rsa/easyrsa3"
fi

cd "$OPEN_VPN_PROJ_DIR"

echo "Creating client cert and key using easyrsa"
# Automate the confirmation ("yes") input for easyrsa.
cat <<EOF | ./easyrsa build-client-full "$USER_SHORTCODE.$VPN_DOMAIN.tld" nopass
yes
EOF

# Create a temporary directory (in the user's home) to store the generated certificates.
mkdir -p "~/$TEMP_VPN_CERT_DIR"
echo "Copying CA certificate to dedicated directory: $TEMP_VPN_CERT_DIR"
cp pki/ca.crt "~/$TEMP_VPN_CERT_DIR"

echo "Copying generated client certificate and key to dedicated directory"
cp "pki/issued/$USER_SHORTCODE.$VPN_DOMAIN.tld.crt" "~/$TEMP_VPN_CERT_DIR"
cp "pki/private/$USER_SHORTCODE.$VPN_DOMAIN.tld.key" "~/$TEMP_VPN_CERT_DIR"

cd "~/$TEMP_VPN_CERT_DIR"

echo "Importing generated client certificate and key into AWS ACM..."
aws acm import-certificate \
  --certificate fileb://"$USER_SHORTCODE.$VPN_DOMAIN.tld.crt" \
  --private-key fileb://"$USER_SHORTCODE.$VPN_DOMAIN.tld.key" \
  --certificate-chain fileb://ca.crt \
  > /dev/null

echo "Looking up VPN endpoint by name and protocol..."
CVN_ENDPOINT=$(aws ec2 describe-client-vpn-endpoints --filters Name="transport-protocol",Values="tcp" \
  | jq -r --arg VPN_DESC "$VPN_DESC" '.ClientVpnEndpoints[] | select(.Description == $VPN_DESC) | .ClientVpnEndpointId')

if [[ -z "$CVN_ENDPOINT" ]]; then
  echo "Error: No VPN endpoint found matching description '$VPN_DESC'."
  exit 1
fi

echo "Generating draft OVPN file for $USER_SHORTCODE for VPN endpoint $CVN_ENDPOINT..."
aws ec2 export-client-vpn-client-configuration --client-vpn-endpoint-id "$CVN_ENDPOINT" --output text > "vpn_config_${PROJECT//-/_}_${USER_SHORTCODE}_temp.ovpn"

echo "Extracting certificate block from client certificate file..."
cert=$(awk 'BEGIN {p=0} /-----BEGIN CERTIFICATE-----/ {p=1} p; /-----END CERTIFICATE-----/ {p=0}' "$USER_SHORTCODE.$VPN_DOMAIN.tld.crt")

echo "Extracting key block from client key file..."
key=$(awk 'BEGIN {p=0} /-----BEGIN PRIVATE KEY-----/ {p=1} p; /-----END PRIVATE KEY-----/ {p=0}' "$USER_SHORTCODE.$VPN_DOMAIN.tld.key")

# Detect OS and set sed command accordingly
if [[ "$OSTYPE" == "darwin"* ]]; then
    SED_CMD="sed -i ''"  # macOS (BSD sed) needs a blank backup extension
else
    SED_CMD="sed -i"     # Linux (GNU sed)
fi

echo "Inserting certificate and key markers into the config file..."
$SED_CMD "s#</ca>#</ca>\n<cert>\nINSERT_CERT_HERE\n</cert>#g" "vpn_config_${PROJECT//-/_}_${USER_SHORTCODE}_temp.ovpn"
$SED_CMD "s#</cert>#</cert>\n<key>\nINSERT_KEY_HERE\n</key>#g" "vpn_config_${PROJECT//-/_}_${USER_SHORTCODE}_temp.ovpn"

echo "Replacing markers with actual certificate and key..."
$SED_CMD "/INSERT_CERT_HERE/r /dev/stdin" "vpn_config_${PROJECT//-/_}_${USER_SHORTCODE}_temp.ovpn" <<< "$cert"
$SED_CMD "/INSERT_KEY_HERE/r /dev/stdin" "vpn_config_${PROJECT//-/_}_${USER_SHORTCODE}_temp.ovpn" <<< "$key"

$SED_CMD "/INSERT_CERT_HERE/d" "vpn_config_${PROJECT//-/_}_${USER_SHORTCODE}_temp.ovpn"
$SED_CMD "/INSERT_KEY_HERE/d" "vpn_config_${PROJECT//-/_}_${USER_SHORTCODE}_temp.ovpn"

mv "vpn_config_${PROJECT//-/_}_${USER_SHORTCODE}_temp.ovpn" "vpn_config_${PROJECT//-/_}_${USER_SHORTCODE}.ovpn"

echo "VPN configuration file is ready: vpn_config_${PROJECT}_${USER_SHORTCODE}.ovpn"