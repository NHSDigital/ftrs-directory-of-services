import { createServerFn } from "@tanstack/react-start";
import * as client from "openid-client";
import { ACR_VALUE } from "@/types/CIS2ClientConfig.ts";
import { getAuthConfig, getOIDCConfig } from "@/utils/cis2Configuration.ts";
import { getLogger } from "@/utils/logger";

type GetAuthorisationUrlInput = {
  data: {
    state: string;
  };
};
export const getAuthorisationUrl = async ({
  data,
}: GetAuthorisationUrlInput) => {
  const logger = getLogger();

  try {
    const oidcConfig = await getOIDCConfig();
    const config = await getAuthConfig();

    const parameters = {
      redirect_uri: config.redirectUri,
      scope: config.scope,
      acr_values: ACR_VALUE,
      state: data.state,
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
};

export const getAuthorisationUrlFn = createServerFn({ method: "POST" })
  .inputValidator((input) => input as { state: string })
  .handler(getAuthorisationUrl);
