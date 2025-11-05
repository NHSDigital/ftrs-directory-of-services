import * as client from "openid-client";
import { ACR_VALUE } from "@/types/CIS2ClientConfig.ts";
import { getAuthConfig, getOIDCConfig } from "@/utils/cis2Configuration.ts";
import { logger } from "@/utils/logger";
import {createServerOnlyFn} from "@tanstack/react-start";


export const getAuthorisationUrl = createServerOnlyFn(async () =>{
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
      code_challenge_method: "S256",
      max_age: "300",
    };
    const authorizationUrl = client.buildAuthorizationUrl(
      oidcConfig,
      parameters,
    );
    logger.info("Authorization URL generated", {
      redirectUri: config.redirectUri,
    });
    return authorizationUrl.href;
  } catch (error) {
    if (error instanceof Error) {
      logger.error("Failed to generate authorization URL", {
        name: error.name,
        message: error.message,
        stack: error.stack,
      });
    }
    throw error;
  }
});
