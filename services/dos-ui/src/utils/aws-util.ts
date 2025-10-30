import { getSecret } from '@aws-lambda-powertools/parameters/secrets';
import { getParameter } from '@aws-lambda-powertools/parameters/ssm';
import { logger } from '@/utils/logger';


export async function getawsSecret(secretName: string): Promise<string | Uint8Array<ArrayBufferLike> | undefined> {
  try {
    logger.debug('Fetching secret from Secrets Manager', { secretName });
    const secret = await getSecret(secretName);
    logger.info('Secret retrieved successfully', { secretName });
    return secret;
  } catch (error) {
    logger.error('Failed to retrieve secret', { secretName, error });
    throw error;
  }
}

export async function getawsParameter(parameterName: string): Promise<any> {
  try {
    logger.debug('Fetching parameter from Parameter Store', { parameterName });
    const parameter = await getParameter(parameterName,  {
                                        sdkOptions: {
                                        WithDecryption: true,
                                        transform: "json",},});
    logger.info('Parameter retrieved successfully', { parameterName });
    return parameter;
  } catch (error) {
    logger.error('Failed to retrieve parameter', { parameterName, error });
    throw error;
  }
}

