import {getawsSecret} from "@/utils/aws-util.ts";

export const getCIS2PublicKey = async (): Promise<string> => {
  const cis2publicKeyPem = await getawsSecret(
    `/${process.env.PROJECT}/${process.env.ENVIRONMENT}/cis2-public-key`,
  );
  if (!cis2publicKeyPem) throw new Error("CIS2 public Key not found");
  return cis2publicKeyPem;
};
