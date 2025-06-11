import { randomUUID } from "node:crypto";
import { Sha256 } from "@aws-crypto/sha256-js";
import { getParameter } from "@aws-lambda-powertools/parameters/ssm";
import { fromNodeProviderChain } from "@aws-sdk/credential-providers";
import { SignatureV4 } from "@aws-sdk/signature-v4";
import { ResponseError } from "./errors";

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
  headers?: Record<string, unknown>;
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

interface SignedRequestOptions extends RequestInit {
  method: string;
  pathname: string;
  expectedStatus?: number[];
}

/**
 * Make a signed fetch request to the CRUD API
 *
 * @param pathname - The path to the resource, e.g. `/organisation/`
 * @param options - Optional request options
 */
export const makeSignedFetch = async (options: SignedRequestOptions) => {
  const correlationId = randomUUID();
  const baseEndpoint = await getBaseEndpoint();

  const signedHeaders = await getSignedHeaders({
    method: options.method,
    url: `${baseEndpoint}${options.pathname}`,
    headers: {
      ...options.headers,
      "X-Correlation-ID": correlationId,
    },
  });

  const response = await fetch(`${baseEndpoint}${options.pathname}`, {
    ...options,
    headers: {
      ...options.headers,
      ...signedHeaders,
      "X-Correlation-ID": correlationId,
    },
  });

  if (
    options.expectedStatus &&
    !options.expectedStatus.includes(response.status)
  ) {
    throw ResponseError.fromResponse(response);
  }

  return response;
};
