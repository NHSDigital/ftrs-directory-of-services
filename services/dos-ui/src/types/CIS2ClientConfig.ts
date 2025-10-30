export interface CIS2ClientConfig {
  issuerUrl: string;
  clientId: string;
  redirectUri: string;
  scope: string;
  keyId : string;
}

export const ACR_VALUE = "AAL2_OR_AAL3_ANY";
