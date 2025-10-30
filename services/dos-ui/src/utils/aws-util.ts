import { getSecret } from '@aws-lambda-powertools/parameters/secrets';
import { getParameter } from '@aws-lambda-powertools/parameters/ssm';


export async function getawsSecret(secretName: string): Promise<string|undefined> {
  return await getSecret(secretName);
}

export async function getawsParameter(parameterName: string): Promise<any> {
  const parameter = await getParameter(parameterName,  {
                                        sdkOptions: {
                                        WithDecryption: true,
                                        transform: "json",},});
  return parameter;
}

