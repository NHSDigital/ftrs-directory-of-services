import { importPKCS8 } from "jose";
import * as client from "openid-client";
import type { CIS2ClientConfig } from "@/types/CIS2ClientConfig.ts";
import { getawsParameter, getawsSecret } from "@/utils/aws-util.ts";
import { getLogger } from "@/utils/logger";

export const validateConfig = (config: {
  clientId: string;
  issuerUrl: string;
  redirectUri: string;
  scope: string;
}): void => {
  if (!config.issuerUrl || !config.clientId) {
    throw new Error(
      "Invalid CIS2ClientConfig: issuerUrl and clientId are required",
    );
  }
};

export const getAuthConfig = async (): Promise<CIS2ClientConfig> => {
  const logger = getLogger();
  const cis2ConfigJson = await getawsParameter(
    `/${process.env.PROJECT}/${process.env.ENVIRONMENT}/cis2-client-config`,
  );
  const config: CIS2ClientConfig = JSON.parse(cis2ConfigJson);
  validateConfig(config);
  logger.info("CIS2 Client Config loaded successfully", {
    clientId: config.clientId,
  });
  return config;
};

export const getCIS2PrivateKey = async (): Promise<CryptoKey> => {
  const cis2privateKeyPem = await getawsSecret(
    `/${process.env.PROJECT}/${process.env.ENVIRONMENT}/cis2-private-key`,
  );
  if (!cis2privateKeyPem) throw new Error("CIS2 Private Key not found");

  return await importPKCS8(cis2privateKeyPem, "RS512");
};

export const getOIDCConfig = async (): Promise<{ oidcClient: client.Configuration; authConfig: CIS2ClientConfig }> => {
  const config = await getAuthConfig();
  const logger = getLogger();

  try {
    const issuerUrl = new URL(config.issuerUrl);
    logger.debug("Parsed issuer URL", { issuerUrl: issuerUrl.href });

    const discoveryURL = new URL(".well-known/openid-configuration", issuerUrl);

    const oidcClientConfig = await client.discovery(
      discoveryURL,
      config.clientId,
      {},
      client.PrivateKeyJwt(await getCIS2PrivateKey()),
    );

    logger.info("OIDC discovery successful");
    try {
      const metadata = oidcClientConfig.serverMetadata();
      logger.debug("Discovered endpoints", {
        authorization_endpoint: metadata.authorization_endpoint,
        token_endpoint: metadata.token_endpoint,
        issuer: metadata.issuer,
        userinfo_endpoint: metadata.userinfo_endpoint,
      });
    } catch (metadataError) {
      logger.warn("Could not log endpoint details", { error: metadataError });
    }

    return { oidcClient: oidcClientConfig, authConfig: config };
  } catch (error) {
    logger.error("CIS2 discovery failed", { error });

    if (error instanceof Error) {
      logger.error("Error details", {
        properties: Object.getOwnPropertyNames(error),
        stack: error.stack,
        code: "code" in error ? error.code : undefined,
        cause: "cause" in error ? error.cause : undefined,
      });
    }
    throw error;
  }
};
