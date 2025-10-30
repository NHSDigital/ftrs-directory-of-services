import * as client from 'openid-client';
import {getAuthConfig, getOIDCConfig} from "@/utils/cisConfiguration.ts";
import {ACR_VALUE} from "@/types/CIS2ClientConfig.ts";


export const getAuthorisationUrl = async (): Promise<string> => {

  try {
    const oidcConfig = await getOIDCConfig();
    const config = await getAuthConfig();

    const state = client.randomState();
    const nonce = client.randomNonce();
    const codeVerifier = client.randomPKCECodeVerifier();
    const codeChallenge = await client.calculatePKCECodeChallenge(codeVerifier);

    const parameters = {
      redirect_uri: config.redirectUri,
      scope: config.scope,
      acr_values: ACR_VALUE,
      state,
      nonce,
      code_challenge: codeChallenge,
      code_challenge_method: 'S256',
      max_age: '300'
    };
    const authorizationUrl = client.buildAuthorizationUrl(oidcConfig, parameters);
    return authorizationUrl.href
  } catch (error) {
    if (error instanceof Error) {
      console.error('Error name:', error.name);
      console.error('Error message:', error.message);
      console.error('Error stack:', error.stack);
    }
    throw error;
  }
}
