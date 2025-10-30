import * as client from 'openid-client';
import {CIS2ClientConfig} from "@/types/CIS2ClientConfig.ts";
import {getawsParameter, getawsSecret} from "@/utils/aws-util.ts";
import {importPKCS8} from "jose";


export const validateConfig = (config: { clientId: string; issuerUrl: string; redirectUri: string; scope: string }): void => {
  if (!config.issuerUrl || !config.clientId) {
    throw new Error('Invalid CIS2ClientConfig: issuerUrl and clientId are required');
  }
};

export const getAuthConfig = async (): Promise<CIS2ClientConfig> => {

  const workspaceSuffix = process.env.WORKSPACE ? `-${process.env.WORKSPACE}` : "";
  const cis2ConfigJson = await getawsParameter(`/${process.env.PROJECT}/${process.env.ENVIRONMENT}/cis2-client-config${workspaceSuffix}`);
  const config: CIS2ClientConfig = JSON.parse(cis2ConfigJson);
  validateConfig(config);
  return config;
};
const getCIS2PrivateKey = async (): Promise<CryptoKey> => {
  const cis2privateKeyPem =await getawsSecret(`/${process.env.PROJECT}/${process.env.ENVIRONMENT}/cis2-private-key`);
  if(!cis2privateKeyPem) throw new Error("CIS2 Private Key not found");
  return await importPKCS8(cis2privateKeyPem, 'RS512');
}

export const getOIDCConfig = async (): Promise<client.Configuration> => {

  const config = await getAuthConfig();

  try {
    const issuerUrl =  new URL(config.issuerUrl);
    const discoveryURL = new URL('.well-known/openid-configuration', issuerUrl);

    const oidcClientConfig = await client.discovery(
      discoveryURL,
      config.clientId,
      {},
      client.PrivateKeyJwt(await getCIS2PrivateKey())
    );

    return oidcClientConfig;
  } catch (error) {
    console.error('CIS2 discovery failed:', error);

    if (error instanceof Error) {
      console.error('Error properties:', Object.getOwnPropertyNames(error));
      console.error('Error stack:', error.stack);
      if ('code' in error) {
        console.error('Error code:', error.code);
      }

      if ('cause' in error) {
        console.error('Error cause:', error.cause);
      }
    }
    throw error;
  }
};

