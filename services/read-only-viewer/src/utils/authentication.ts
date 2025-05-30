import { Sha256 } from "@aws-crypto/sha256-js";
import { getParameter } from "@aws-lambda-powertools/parameters/ssm";
import { fromNodeProviderChain } from "@aws-sdk/credential-providers";
import { SignatureV4 } from "@aws-sdk/signature-v4";

export const getBaseEndpoint = async () => {
  const environment = process.env.ENVIRONMENT;
  const workspace = process.env.WORKSPACE;

  const parameterPath = workspace
    ? `/ftrs-dos-${environment}-crud-apis-${workspace}/endpoint`
    : `/ftrs-dos-${environment}-crud-apis/endpoint`;

  const baseUrl = await getParameter(parameterPath);
  if (!baseUrl) {
    throw new Error(
      `Base URL not found for environment: ${environment}, workspace: ${workspace}`,
    );
  }
  return baseUrl;
};

export const getSignedHeaders = async (options: {
  method: string;
  url: string;
  headers?: Record<string, string>;
  body?: string;
}) => {
  const signer = new SignatureV4({
    credentials: fromNodeProviderChain({}),
    region: process.env.AWS_REGION || "eu-west-2",
    service: "execute-api",
    sha256: Sha256,
  });

  const parsedUrl = new URL(options.url);
  const headers = {
    ...options.headers,
    Host: parsedUrl.hostname,
  };

  const signedRequest = await signer.sign({
    method: options.method,
    headers: headers,
    hostname: parsedUrl.hostname,
    path: parsedUrl.pathname,
    protocol: "https:",
  });

  return signedRequest.headers;
};
