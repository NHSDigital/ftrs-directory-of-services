import { getSecret } from "@aws-lambda-powertools/parameters/secrets";
import { getParameter } from "@aws-lambda-powertools/parameters/ssm";
import type { SDKOptionsTypeFromPowertools } from "@/types/SDKOptionsTypeFromPowertools";
import { getLogger } from "@/utils/logger";

export async function getawsSecret(
  secretName: string,
): Promise<string | undefined> {
  const logger = getLogger();

  try {
    logger.debug("Fetching secret from Secrets Manager", { secretName });
    const secret = await getSecret(secretName, { maxAge: 60 });
    logger.info("Secret retrieved successfully", { secretName });
    if (secret instanceof Uint8Array) {
      return new TextDecoder().decode(secret);
    }
    return secret;
  } catch (error) {
    logger.error("Failed to retrieve secret", { secretName, error });
    throw error;
  }
}

export async function getawsParameter(
  parameterName: string,
  sdkOptions?: Partial<SDKOptionsTypeFromPowertools>,
): Promise<string> {
  const logger = getLogger();
  try {
    logger.debug("Fetching parameter from Parameter Store", { parameterName });
    const parameter = await getParameter(parameterName, {
      sdkOptions: {
        WithDecryption: true,
        transform: "json",
        ...sdkOptions,
      },
    });
    logger.info("Parameter retrieved successfully", { parameterName });
    return parameter!;
  } catch (error) {
    logger.error("Failed to retrieve parameter", { parameterName, error });
    throw error;
  }
}
